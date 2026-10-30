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
  const backdrop = document.getElementById('nav-backdrop');

  function openMenu() {
    if (navLinks) navLinks.classList.add('open');
    if (backdrop) backdrop.classList.add('active');
    document.body.classList.add('nav-open');
    if (toggleBtn) {
      const icon = toggleBtn.querySelector('i');
      if (icon) {
        icon.classList.remove('fa-bars');
        icon.classList.add('fa-xmark');
      }
    }
  }

  function closeMenu() {
    if (navLinks) navLinks.classList.remove('open');
    if (backdrop) backdrop.classList.remove('active');
    document.body.classList.remove('nav-open');
    if (toggleBtn) {
      const icon = toggleBtn.querySelector('i');
      if (icon) {
        icon.classList.remove('fa-xmark');
        icon.classList.add('fa-bars');
      }
    }
  }

  if (toggleBtn && navLinks) {
    toggleBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      if (navLinks.classList.contains('open')) {
        closeMenu();
      } else {
        openMenu();
      }
    });

    if (backdrop) {
      backdrop.addEventListener('click', closeMenu);
    }

    // Close when clicking any nav item on mobile
    const links = navLinks.querySelectorAll('a');
    links.forEach(link => {
      link.addEventListener('click', closeMenu);
    });

    // Close on escape key
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && navLinks.classList.contains('open')) {
        closeMenu();
      }
    });
  }
}
