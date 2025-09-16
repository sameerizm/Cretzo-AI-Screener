const form = document.getElementById('upload-form');
const resultsContainer = document.getElementById('results-container');

form.addEventListener('submit', async (e) => {
  e.preventDefault();
  resultsContainer.innerHTML = '<em>Processing — model may download on first run...</em>';
  const fd = new FormData(form);
  try {
    const res = await fetch('/screen', { method: 'POST', body: fd });
    if (!res.ok) {
      const err = await res.json();
      resultsContainer.innerHTML = `<div class="result">Error: ${err.error || res.statusText}</div>`;
      return;
    }
    const json = await res.json();
    const results = json.results || [];
    resultsContainer.innerHTML = '';
    const grid = document.createElement('div');
    grid.className = 'cv-grid';
    results.forEach(r => {
      const d = document.createElement('div');
      d.className = 'result';
      d.innerHTML = `<strong>${r.cv_name}</strong><br><div><strong>${r.percentage}%</strong> ${r.emoji}</div><small>Missing: ${r.missing_skills.length ? r.missing_skills.join(', ') : 'None'}</small>`;
      grid.appendChild(d);
    });
    resultsContainer.appendChild(grid);
    const sid = json.screening_id;
    const dl = document.createElement('div');
    dl.innerHTML = `<br><a href="/download_report/${sid}" target="_blank"><button>Download Combined PDF Report</button></a>`;
    resultsContainer.appendChild(dl);
  } catch (err) {
    console.error(err);
    resultsContainer.innerHTML = `<div class="result">Error: ${err.message}</div>`;
  }
});

function scrollToForm() {
  document.getElementById('form-section').scrollIntoView({behavior:'smooth'});
}