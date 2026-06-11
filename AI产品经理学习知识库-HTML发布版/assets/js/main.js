(function () {
  const modal = document.querySelector('[data-search-modal]');
  const searchInput = document.querySelector('[data-search-input]');
  const searchResults = document.querySelector('[data-search-results]');
  const inArticle = document.body.querySelector('article') && location.pathname.includes('/articles/');
  const inModule = location.pathname.includes('/modules/');

  function urlFor(item) {
    if (inArticle) return item.articleUrl;
    if (inModule) return item.moduleUrl;
    return item.url;
  }

  function renderResults(query) {
    if (!searchResults) return;
    const q = query.trim().toLowerCase();
    const data = window.SEARCH_INDEX || [];
    const results = q
      ? data.filter((item) => [item.title, item.section, item.excerpt, item.text].join(' ').toLowerCase().includes(q)).slice(0, 14)
      : data.slice(0, 10);
    searchResults.innerHTML = results.map((item) => `
      <a class="block rounded-lg p-4 hover:bg-slate-50" href="${urlFor(item)}">
        <div class="flex items-center justify-between gap-3">
          <strong class="text-slate-950">${item.title}</strong>
          <span class="shrink-0 rounded-full bg-slate-100 px-2 py-1 text-xs font-bold text-slate-500">${item.section}</span>
        </div>
        <p class="mt-2 text-sm leading-6 text-slate-600">${item.excerpt}</p>
      </a>
    `).join('') || '<div class="p-4 text-sm text-slate-500">没搜到，换个关键词试试。</div>';
  }

  function openSearch() {
    if (!modal) return;
    modal.classList.add('open');
    modal.setAttribute('aria-hidden', 'false');
    renderResults('');
    setTimeout(() => searchInput && searchInput.focus(), 20);
  }
  function closeSearch() {
    if (!modal) return;
    modal.classList.remove('open');
    modal.setAttribute('aria-hidden', 'true');
  }
  document.querySelectorAll('[data-search-open]').forEach((button) => button.addEventListener('click', openSearch));
  document.querySelectorAll('[data-search-close]').forEach((button) => button.addEventListener('click', closeSearch));
  if (searchInput) searchInput.addEventListener('input', (event) => renderResults(event.target.value));
  if (modal) modal.addEventListener('click', (event) => { if (event.target === modal) closeSearch(); });
  document.addEventListener('keydown', (event) => {
    if (event.key === '/' && !event.metaKey && !event.ctrlKey && document.activeElement.tagName !== 'INPUT') {
      event.preventDefault();
      openSearch();
    }
    if (event.key === 'Escape') closeSearch();
  });

  const progress = document.getElementById('progressBar');
  function updateProgress() {
    if (!progress) return;
    const max = document.documentElement.scrollHeight - window.innerHeight;
    progress.style.width = `${Math.min(100, Math.max(0, max > 0 ? (window.scrollY / max) * 100 : 0))}%`;
  }
  window.addEventListener('scroll', updateProgress, { passive: true });
  updateProgress();

  document.querySelectorAll('pre').forEach((pre) => {
    const button = document.createElement('button');
    button.className = 'copy-code';
    button.type = 'button';
    button.textContent = '复制';
    button.addEventListener('click', async () => {
      const code = pre.innerText.replace(/^复制\s*/, '');
      try {
        await navigator.clipboard.writeText(code);
        button.textContent = '已复制';
        setTimeout(() => { button.textContent = '复制'; }, 1200);
      } catch (error) {
        button.textContent = '手动复制';
      }
    });
    pre.appendChild(button);
  });

  const navFilter = document.querySelector('[data-nav-filter]');
  if (navFilter) {
    navFilter.addEventListener('input', (event) => {
      const q = event.target.value.trim().toLowerCase();
      document.querySelectorAll('[data-title]').forEach((link) => {
        const haystack = `${link.dataset.title || ''} ${link.dataset.module || ''}`;
        link.style.display = haystack.includes(q) ? '' : 'none';
      });
    });
  }

  document.querySelectorAll('[data-nav-toggle]').forEach((button) => {
    button.addEventListener('click', () => {
      const sidebar = document.getElementById('sidebar');
      if (sidebar) sidebar.classList.toggle('open');
    });
  });
})();
