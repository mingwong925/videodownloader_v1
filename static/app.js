const form = document.querySelector('#download-form');
const mode = document.querySelector('#mode');
const qualityWrap = document.querySelector('#quality-wrap');
const emptyState = document.querySelector('#empty-state');
const jobList = document.querySelector('#job-list');
mode.addEventListener('change', () => { qualityWrap.hidden = mode.value === 'audio'; });
function addJobCard(id) {
  emptyState.hidden = true;
  const card = document.createElement('article'); card.className = 'job'; card.id = `job-${id}`;
  card.innerHTML = '<div><div class="job-title">正在準備下載…</div><div class="job-meta">佇列中</div><div class="bar"><i></i></div></div>';
  jobList.prepend(card); return card;
}
async function pollJob(id, card) {
  const response = await fetch(`/api/download/${id}`); const job = await response.json();
  const title = card.querySelector('.job-title'); const meta = card.querySelector('.job-meta'); const bar = card.querySelector('i'); bar.style.width = `${job.progress || 0}%`;
  if (job.status === 'ready') { title.textContent = '下載完成'; meta.textContent = '檔案已準備好'; const button = document.createElement('button'); button.textContent = '下載檔案 ↓'; button.onclick = () => { window.location.href = `/api/file/${id}`; }; card.append(button); return; }
  if (job.status === 'error') { card.classList.add('error'); title.textContent = '下載失敗'; meta.textContent = job.error || '請確認網址後再試一次'; return; }
  meta.textContent = job.status === 'queued' ? '排隊中' : `處理中 ${job.progress || 0}%`; window.setTimeout(() => pollJob(id, card), 900);
}
form.addEventListener('submit', async (event) => {
  event.preventDefault(); const button = form.querySelector('button'); button.disabled = true; button.firstChild.textContent = '建立工作中 ';
  try { const response = await fetch('/api/download', { method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({ url:document.querySelector('#url').value, mode:mode.value, quality:document.querySelector('#quality').value }) }); const data = await response.json(); if (!response.ok) throw new Error(data.detail || '網址無法處理'); pollJob(data.job_id, addJobCard(data.job_id)); document.querySelector('#url').value = ''; }
  catch (error) { const card = addJobCard(`error-${Date.now()}`); card.classList.add('error'); card.querySelector('.job-title').textContent = '無法建立下載'; card.querySelector('.job-meta').textContent = error.message; }
  finally { button.disabled = false; button.firstChild.textContent = '開始抓取 '; }
});
