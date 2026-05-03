/**
 * Paclassy — dark_mode.js
 * Persists dark mode preference; called early in <head> to avoid flash.
 */
(function () {
  const stored = localStorage.getItem('darkMode');
  const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
  if (stored === 'true' || (stored === null && prefersDark)) {
    document.documentElement.classList.add('dark');
  }
})();
