// ==========================================================================
// FlavorBridge Form Validation & Dynamic Role Switcher
// ==========================================================================

document.addEventListener('DOMContentLoaded', () => {
  initRoleSwitcher();
  initFormValidation();
});

function initRoleSwitcher() {
  const roleRadios = document.querySelectorAll('input[name="role"]');
  const foodMakerFields = document.querySelector('#food-maker-extra-fields');

  if (roleRadios.length > 0 && foodMakerFields) {
    roleRadios.forEach(radio => {
      radio.addEventListener('change', function() {
        if (this.value === 'food_maker') {
          foodMakerFields.style.display = 'block';
          foodMakerFields.style.animation = 'fadeIn 0.25s ease-in-out';
          const reqInputs = foodMakerFields.querySelectorAll('input, textarea');
          reqInputs.forEach(inp => inp.setAttribute('data-maker-required', 'true'));
        } else {
          foodMakerFields.style.display = 'none';
        }
      });
    });

    // Initial check
    const activeRadio = document.querySelector('input[name="role"]:checked');
    if (activeRadio && activeRadio.value === 'food_maker') {
      foodMakerFields.style.display = 'block';
    }
  }
}

function initFormValidation() {
  const forms = document.querySelectorAll('form[data-validate="true"]');
  forms.forEach(form => {
    form.addEventListener('submit', function(e) {
      const emailInput = form.querySelector('input[type="email"]');
      const phoneInput = form.querySelector('input[name="phone"]');

      if (emailInput && emailInput.value.trim()) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(emailInput.value.trim())) {
          e.preventDefault();
          alert('Please enter a valid email address.');
          emailInput.focus();
          return;
        }
      }

      if (phoneInput && phoneInput.value.trim()) {
        const cleanPhone = phoneInput.value.replace(/[\s\-\+]/g, '');
        if (cleanPhone.length < 10) {
          e.preventDefault();
          alert('Please enter a valid 10-digit phone number.');
          phoneInput.focus();
          return;
        }
      }
    });
  });
}
