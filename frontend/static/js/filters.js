// ==========================================================================
// FlavorBridge Filter and Search Interactivity
// ==========================================================================

document.addEventListener('DOMContentLoaded', () => {
  initFilterControls();
  initMobileMenu();
});

function initFilterControls() {
  const filterForm = document.querySelector('#catalog-filter-form');
  if (!filterForm) return;

  // Auto-submit on change for quick dropdowns and radios
  const autoSubmitInputs = filterForm.querySelectorAll('select, input[type="radio"], input[type="checkbox"]');
  autoSubmitInputs.forEach(input => {
    input.addEventListener('change', () => {
      filterForm.submit();
    });
  });

  // Price range debounce
  const minPriceInput = document.querySelector('#min-price-input');
  const maxPriceInput = document.querySelector('#max-price-input');
  let timeout = null;

  [minPriceInput, maxPriceInput].forEach(inp => {
    if (inp) {
      inp.addEventListener('input', () => {
        clearTimeout(timeout);
        timeout = setTimeout(() => {
          filterForm.submit();
        }, 800);
      });
    }
  });
}

function initMobileMenu() {
  const toggleBtn = document.querySelector('.mobile-nav-toggle');
  const navLinks = document.querySelector('.nav-links');

  if (toggleBtn && navLinks) {
    toggleBtn.addEventListener('click', () => {
      navLinks.classList.toggle('open');
      const icon = toggleBtn.querySelector('i');
      if (icon) {
        icon.classList.toggle('fa-bars');
        icon.classList.toggle('fa-xmark');
      }
    });
  }
}
