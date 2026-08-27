// ==========================================================================
// FlavorBridge Smart Search Frontend
// ==========================================================================

document.addEventListener('DOMContentLoaded', () => {
  const searchInput = document.querySelector('#global-search-input') || document.querySelector('.hero-search-box .search-input');
  
  if (searchInput) {
    searchInput.addEventListener('keydown', (e) => {
      if (e.key === 'Enter') {
        const query = searchInput.value.trim();
        if (query) {
          window.location.href = `/products?q=${encodeURIComponent(query)}`;
        }
      }
    });
  }

  // Quick tag search handler
  document.querySelectorAll('.hero-quick-tag').forEach(tag => {
    tag.addEventListener('click', (e) => {
      e.preventDefault();
      const term = tag.getAttribute('data-term') || tag.textContent.trim();
      window.location.href = `/products?q=${encodeURIComponent(term)}`;
    });
  });
});
