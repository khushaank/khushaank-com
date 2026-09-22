(() => {
  const button = document.querySelector('#theme-toggle');
  if (!button) return;
  const icons = {
    auto: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 3a9 9 0 0 0 0 18Z" fill="currentColor"></path><circle cx="12" cy="12" r="9" fill="none" stroke="currentColor" stroke-width="1.7"></circle></svg>',
    light: '<svg viewBox="0 0 24 24" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"><circle cx="12" cy="12" r="4"></circle><path d="M12 2v3M12 19v3M2 12h3M19 12h3M4.9 4.9 7 7M17 17l2.1 2.1M19.1 4.9 17 7M7 17l-2.1 2.1"></path></svg>',
    dark: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M20 15.3A8.5 8.5 0 1 1 8.7 4 7 7 0 0 0 20 15.3Z" fill="currentColor"></path></svg>'
  };
  const set = value => {
    document.documentElement.dataset.theme = value;
    button.innerHTML = icons[value];
    button.setAttribute('aria-label', `Change theme; currently ${value}`);
    button.title = `Change theme; currently ${value}`;
  };
  set(localStorage.getItem('theme') || 'auto');
  button.addEventListener('click', () => {
    const next = {auto: 'light', light: 'dark', dark: 'auto'}[document.documentElement.dataset.theme] || 'auto';
    localStorage.setItem('theme', next);
    set(next);
  });
})();
