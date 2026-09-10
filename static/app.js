const form = document.querySelector('#download-form');
const mode = document.querySelector('#mode');
const qualityWrap = document.querySelector('#quality-wrap');
const emptyState = document.querySelector('#empty-state');
const jobList = document.querySelector('#job-list');
const inspectResults = document.querySelector('#inspect-results');
if (new URLSearchParams(window.location.search).has('desktop')) {
  document.querySelector('.eyebrow').textContent = 'ONE APP · MORE THAN 15 PLATFORMS';
  const otherSources = document.createElement('b'); otherSources.textContent = '其他來源'; document.querySelector('.platforms').append(otherSources);
}
mode.addEventListener('change', () => { qualityWrap.hidden = mode.value === 'audio'; });
function addJobCard(id) {
  emptyState.hidden = true;
  const card = document.createElement('article'); card.className = 'job'; card.id = `job-${id}`;
  card.innerHTML = '<div class="job-content"><div class="job-title">正在準備下載…</div><div class="job-meta">佇列中</div><div class="bar"><i></i></div></div>';
  jobList.prepend(card); return card;
}
function animateProgress(bar, target) {
  const next = Math.max(Number(bar.dataset.progress || 0), Math.min(100, Number(target) || 0));
  const start = Number(bar.dataset.progress || 0);
  if (next === start) return;
  const startedAt = performance.now();
  const duration = 700;
  const step = (now) => {
    const ratio = Math.min(1, (now - startedAt) / duration);
    const eased = 1 - (1 - ratio) ** 3;
    const value = start + (next - start) * eased;
    bar.style.width = `${value}%`;
    if (ratio < 1) window.requestAnimationFrame(step); else bar.dataset.progress = String(next);
  };
  window.requestAnimationFrame(step);
}
async function pollJob(id, card) {
  const title = card.querySelector('.job-title'); const meta = card.querySelector('.job-meta'); const bar = card.querySelector('i');
  try {
    const response = await fetch(`/api/download/${id}`); const job = await response.json();
    animateProgress(bar, job.progress || 0);
    if (job.thumbnail && !card.querySelector('.thumbnail')) { const thumbnail = document.createElement('img'); thumbnail.className = 'thumbnail'; thumbnail.src = job.thumbnail; thumbnail.alt = ''; thumbnail.loading = 'lazy'; card.classList.add('has-thumbnail'); card.prepend(thumbnail); }
    if (job.status === 'ready') {
      title.textContent = '下載完成'; meta.textContent = '按下按鈕將檔案儲存到你的電腦';
      const link = document.createElement('a'); link.className = 'download-link'; link.textContent = '下載檔案 ↓'; link.href = `/api/file/${encodeURIComponent(id)}`; link.download = ''; link.target = '_blank'; link.rel = 'noopener';
      link.addEventListener('click', async (event) => {
        if (!window.pywebview?.api?.save_file) return;
        event.preventDefault();
        link.textContent = '儲存中…';
        try { const savedPath = await window.pywebview.api.save_file(id, job.filename || 'pianke-video.mp4'); if (!savedPath) { meta.textContent = '已取消儲存'; link.textContent = '下載檔案 ↓'; } else { meta.textContent = `已儲存至 ${savedPath}`; link.textContent = '已儲存 ✓'; } }
        catch (error) { meta.textContent = `儲存失敗：${error.message || '請再試一次'}`; link.textContent = '下載檔案 ↓'; }
      });
      card.append(link); return;
    }
    if (job.status === 'error') { card.classList.add('error'); title.textContent = '下載失敗'; meta.textContent = job.error || '請確認網址後再試一次'; return; }
    meta.textContent = job.status === 'queued' ? '排隊中' : `${job.status === 'converting' ? '正在轉換' : '下載中'} ${job.progress || 0}%`; window.setTimeout(() => pollJob(id, card), 900);
  } catch (error) { card.classList.add('error'); title.textContent = '無法取得下載狀態'; meta.textContent = '服務可能正在休眠，請重新提交網址'; }
}
form.addEventListener('submit', async (event) => {
  event.preventDefault(); const button = form.querySelector('button'); button.disabled = true; button.firstChild.textContent = '建立工作中 ';
  try { const isDesktop = new URLSearchParams(window.location.search).has('desktop'); const response = await fetch('/api/download', { method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({ url:document.querySelector('#url').value, mode:mode.value, quality:document.querySelector('#quality').value, desktop:isDesktop }) }); const data = await response.json(); if (!response.ok) throw new Error(data.detail || '網址無法處理'); pollJob(data.job_id, addJobCard(data.job_id)); document.querySelector('#url').value = ''; }
  catch (error) { const card = addJobCard(`error-${Date.now()}`); card.classList.add('error'); card.querySelector('.job-title').textContent = '無法建立下載'; card.querySelector('.job-meta').textContent = error.message; }
  finally { button.disabled = false; button.firstChild.textContent = '開始抓取 '; }
});

document.querySelector('#inspect-submit').addEventListener('click', async () => {
  const url = document.querySelector('#url').value;
  inspectResults.hidden = false; inspectResults.textContent = '正在分析頁面…';
  try {
    const isDesktop = new URLSearchParams(window.location.search).has('desktop');
    const response = await fetch('/api/inspect', { method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({ url, desktop:isDesktop }) });
    const data = await response.json(); if (!response.ok) throw new Error(data.detail || '分析失敗');
    inspectResults.replaceChildren();
    if (!data.links?.length) { inspectResults.textContent = '頁面沒有找到公開影片連結；動態載入、登入或 DRM 影片可能無法分析。'; return; }
    data.links.forEach((item) => { const link = document.createElement('button'); link.type = 'button'; link.textContent = `${item.type.toUpperCase()} · ${item.url}`; link.onclick = () => { document.querySelector('#url').value = item.url; inspectResults.hidden = true; }; inspectResults.append(link); });
  } catch (error) { inspectResults.textContent = error.message; }
});
