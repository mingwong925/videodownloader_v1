from __future__ import annotations

import re
import subprocess
import threading
import uuid
from pathlib import Path
from urllib.parse import parse_qs, urlparse

import imageio_ffmpeg
from fastapi import BackgroundTasks, FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, HttpUrl

BASE_DIR = Path(__file__).parent
DOWNLOAD_DIR = BASE_DIR / "downloads"
DOWNLOAD_DIR.mkdir(exist_ok=True)
FFMPEG_PATH = imageio_ffmpeg.get_ffmpeg_exe()
ALLOWED_HOSTS = {"youtube.com", "www.youtube.com", "m.youtube.com", "youtu.be", "instagram.com", "www.instagram.com", "facebook.com", "www.facebook.com", "fb.watch", "x.com", "www.x.com", "twitter.com", "www.twitter.com", "tiktok.com", "www.tiktok.com", "douyin.com", "www.douyin.com", "m.douyin.com", "v.douyin.com", "iesdouyin.com", "www.iesdouyin.com", "bilibili.com", "www.bilibili.com", "m.bilibili.com", "b23.tv"}
jobs: dict[str, dict[str, str | int]] = {}
jobs_lock = threading.Lock()


class DownloadRequest(BaseModel):
    url: HttpUrl
    mode: str = "video"
    quality: str = "best"


app = FastAPI(title="抓片", description="Download public media from supported platforms")
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")


def normalize_source_url(url: str) -> str:
    parsed = urlparse(url)
    hostname = (parsed.hostname or "").lower()
    if "douyin.com" in hostname and parsed.path.rstrip("/") in {"/jingxuan", "/hot", "/discover"}:
        modal_id = parse_qs(parsed.query).get("modal_id", [""])[0]
        if modal_id.isdigit():
            return f"https://www.douyin.com/video/{modal_id}"
    return url


def validate_source(url: str) -> None:
    parsed = urlparse(url)
    hostname = (parsed.hostname or "").lower().rstrip(".")
    if parsed.scheme not in {"http", "https"} or hostname not in ALLOWED_HOSTS:
        raise HTTPException(status_code=400, detail="目前只支援 YouTube、Instagram、Facebook、X、TikTok、抖音與 bilibili 網址")


def update_job(job_id: str, **values: str | int) -> None:
    with jobs_lock:
        jobs[job_id].update(values)


def run_download(job_id: str, url: str, mode: str, quality: str) -> None:
    output_template = str(DOWNLOAD_DIR / f"{job_id}_%(title).80s.%(ext)s")
    if mode == "audio":
        format_selector, postprocessors = "bestaudio/best", ["--extract-audio", "--audio-format", "mp3"]
    else:
        format_selector = {"best": "bv*+ba/b", "1080": "bv*[height<=1080]+ba/b[height<=1080]", "720": "bv*[height<=720]+ba/b[height<=720]", "480": "bv*[height<=480]+ba/b[height<=480]"}.get(quality, "bv*+ba/b")
        postprocessors = ["--merge-output-format", "mp4", "--recode-video", "mp4", "--postprocessor-args", "VideoConvertor:-c:v libx264 -pix_fmt yuv420p -c:a aac"]
    command = ["yt-dlp", "--no-playlist", "--newline", "--ffmpeg-location", FFMPEG_PATH, "--format", format_selector, "--output", output_template, *postprocessors]
    hostname = (urlparse(url).hostname or "").lower()
    if "douyin.com" in hostname:
        command.extend(["--cookies-from-browser", "chrome", "--referer", "https://www.douyin.com/", "--user-agent", "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/131 Safari/537.36"])
    command.append(url)
    try:
        update_job(job_id, status="downloading", progress=3)
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, start_new_session=True)
        assert process.stdout is not None
        output_lines = []
        for line in process.stdout:
            output_lines.append(line.strip())
            output_lines = output_lines[-5:]
            match = re.search(r"(\d+(?:\.\d+)?)%", line)
            if match:
                download_progress = int(float(match.group(1)))
                update_job(job_id, progress=min(80, 5 + int(download_progress * 0.75)))
        if process.wait() != 0:
            detail = next((line for line in reversed(output_lines) if line.startswith("ERROR:")), None)
            if detail and "Fresh cookies" in detail:
                detail = "抖音要求有效 cookies。請先在 Chrome 登入 douyin.com，重新整理本工具後再下載。"
            raise RuntimeError(detail or "yt-dlp 無法取得這個網址，可能需要登入、網址失效或內容不可公開存取")
        files = list(DOWNLOAD_DIR.glob(f"{job_id}_*"))
        if not files:
            raise RuntimeError("下載完成但找不到輸出檔案")
        source_path = files[0]
        if mode == "video":
            update_job(job_id, status="converting", progress=82)
            compatible_path = source_path.with_name(f"{source_path.stem}.compatible.mp4")
            conversion_command = [
                FFMPEG_PATH,
                "-y",
                "-i",
                str(source_path),
                "-map",
                "0:v:0",
                "-map",
                "0:a?",
                "-c:v",
                "libx264",
                "-preset",
                "veryfast",
                "-pix_fmt",
                "yuv420p",
                "-c:a",
                "aac",
                "-movflags",
                "+faststart",
                "-progress",
                "pipe:1",
                "-nostats",
                str(compatible_path),
            ]
            conversion = subprocess.Popen(conversion_command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, start_new_session=True)
            assert conversion.stdout is not None
            duration_seconds = None
            for line in conversion.stdout:
                duration_match = re.search(r"Duration: (\d+):(\d+):(\d+(?:\.\d+)?)", line)
                if duration_match:
                    hours, minutes, seconds = duration_match.groups()
                    duration_seconds = int(hours) * 3600 + int(minutes) * 60 + float(seconds)
                time_match = re.search(r"out_time_ms=(\d+)", line)
                if duration_seconds and time_match:
                    elapsed_seconds = int(time_match.group(1)) / 1_000_000
                    conversion_progress = min(98, 82 + int((elapsed_seconds / duration_seconds) * 16))
                    update_job(job_id, progress=conversion_progress)
            if conversion.wait() != 0:
                raise RuntimeError("影片相容性轉碼失敗")
            source_path.unlink()
            compatible_path.rename(source_path.with_suffix(".mp4"))
            source_path = source_path.with_suffix(".mp4")
        update_job(job_id, status="ready", progress=100, filename=source_path.name)
    except (OSError, RuntimeError, subprocess.CalledProcessError) as error:
        update_job(job_id, status="error", progress=0, error=str(error))


@app.get("/")
def index() -> FileResponse:
    return FileResponse(BASE_DIR / "static" / "index.html")


@app.post("/api/download")
def create_download(request: DownloadRequest, background_tasks: BackgroundTasks) -> dict[str, str]:
    if request.mode not in {"video", "audio"}:
        raise HTTPException(status_code=400, detail="不支援的輸出格式")
    source_url = normalize_source_url(str(request.url))
    validate_source(source_url)
    job_id = uuid.uuid4().hex
    with jobs_lock:
        jobs[job_id] = {"status": "queued", "progress": 0}
    background_tasks.add_task(run_download, job_id, source_url, request.mode, request.quality)
    return {"job_id": job_id}


@app.get("/api/download/{job_id}")
def download_status(job_id: str) -> dict[str, str | int]:
    with jobs_lock:
        job = jobs.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="找不到下載工作")
    return job


@app.get("/api/file/{job_id}")
def get_file(job_id: str) -> FileResponse:
    with jobs_lock:
        job = jobs.get(job_id)
    if not job or job.get("status") != "ready":
        raise HTTPException(status_code=404, detail="檔案尚未準備好")
    filename = str(job["filename"])
    path = DOWNLOAD_DIR / filename
    if not path.exists() or path.parent != DOWNLOAD_DIR:
        raise HTTPException(status_code=404, detail="檔案不存在")
    safe_name = re.sub(r"[^\w\-. ]", "_", filename.split("_", 1)[-1])
    return FileResponse(path, filename=safe_name, media_type="application/octet-stream")


@app.delete("/api/download/{job_id}")
def remove_download(job_id: str) -> dict[str, str]:
    with jobs_lock:
        job = jobs.pop(job_id, None)
    if job and job.get("filename"):
        (DOWNLOAD_DIR / str(job["filename"])).unlink(missing_ok=True)
    return {"status": "deleted"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)
