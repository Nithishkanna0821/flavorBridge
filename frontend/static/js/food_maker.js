// ==========================================================================
// FlavorBridge Food Maker Dashboard & Operations Interactivity
// Provides Instant AJAX status updates, fast image preview, and responsive actions
// ==========================================================================

document.addEventListener('DOMContentLoaded', () => {
  initMakerOrderStatusAjax();
  initMakerDeleteProductAjax();
  initImagePreviews();
  initSubmitButtonSpinners();
});

/**
 * Handle instant AJAX Order Status Updates on Dashboard, Kitchen Orders, and Order Details
 */
function initMakerOrderStatusAjax() {
  document.querySelectorAll('.order-status-ajax-form, form[action*="update-order-status"]').forEach(form => {
    if (form.dataset.ajaxBound) return;
    form.dataset.ajaxBound = 'true';

    const select = form.querySelector('select[name="status"]');
    const submitBtn = form.querySelector('button[type="submit"]');
    const orderIdInput = form.querySelector('input[name="order_id"]');

    if (!select || !orderIdInput) return;

    form.addEventListener('submit', function(e) {
      e.preventDefault();
      executeStatusUpdate(this, select, submitBtn, orderIdInput.value, select.value);
    });

    // Optional: auto-save on select change for super fast updates
    select.addEventListener('change', function() {
      executeStatusUpdate(form, select, submitBtn, orderIdInput.value, this.value);
    });
  });
}

function executeStatusUpdate(form, select, submitBtn, orderId, newStatus) {
  const originalBtnHtml = submitBtn ? submitBtn.innerHTML : 'Save';
  if (submitBtn) {
    submitBtn.disabled = true;
    submitBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Saving...';
  }

  fetch('/update-order-status', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-Requested-With': 'XMLHttpRequest'
    },
    body: JSON.stringify({
      order_id: parseInt(orderId),
      status: newStatus
    })
  })
  .then(res => res.json())
  .then(data => {
    if (data.success) {
      // 1. Update status badge text and classes
      const badges = document.querySelectorAll(`#order-status-badge-${orderId}, .order-badge-${orderId}`);
      badges.forEach(badge => {
        badge.textContent = data.status;
        badge.className = 'badge';
        if (data.status === 'Delivered') {
          badge.classList.add('badge-verified');
        } else if (['Preparing', 'Shipped', 'Out for Delivery'].includes(data.status)) {
          badge.classList.add('badge-fresh');
        } else {
          badge.classList.add('badge-pending');
        }
        badge.style.animation = 'pulseBadge 0.3s ease-in-out';
      });

      // 2. Button visual feedback
      if (submitBtn) {
        submitBtn.disabled = false;
        submitBtn.innerHTML = '<i class="fa-solid fa-check"></i> Saved!';
        submitBtn.classList.remove('btn-secondary');
        submitBtn.classList.add('btn-primary');
        setTimeout(() => {
          submitBtn.innerHTML = originalBtnHtml;
          submitBtn.classList.remove('btn-primary');
          submitBtn.classList.add('btn-secondary');
        }, 1500);
      }

      // 3. Live Dashboard Metric Updates
      if (newStatus === 'Delivered') {
        const activeOrdersEl = document.querySelector('#maker-metric-active-orders');
        const completedOrdersEl = document.querySelector('#maker-metric-completed-orders');
        if (activeOrdersEl) {
          const currentVal = parseInt(activeOrdersEl.textContent.trim()) || 0;
          activeOrdersEl.textContent = Math.max(0, currentVal - 1);
        }
        if (completedOrdersEl) {
          const currentVal = parseInt(completedOrdersEl.textContent.trim()) || 0;
          completedOrdersEl.textContent = currentVal + 1;
        }
      }

      // 4. Update Stepper on Order Details Page if present
      if (data.status_step) {
        updateOrderTimelineStepper(data.status_step);
      }

      if (typeof showToast === 'function') {
        showToast(data.message, 'success');
      }
    } else {
      if (submitBtn) {
        submitBtn.disabled = false;
        submitBtn.innerHTML = originalBtnHtml;
      }
      if (typeof showToast === 'function') {
        showToast(data.message || 'Error updating status', 'error');
      }
    }
  })
  .catch(err => {
    console.warn('Status update fallback to standard submit:', err);
    if (submitBtn) {
      submitBtn.disabled = false;
      submitBtn.innerHTML = originalBtnHtml;
    }
    form.submit();
  });
}

/**
 * Updates visual tracking stepper nodes dynamically
 */
function updateOrderTimelineStepper(stepNum) {
  const steps = document.querySelectorAll('.order-stepper .step-node');
  steps.forEach((node, index) => {
    const nodeStep = index + 1;
    node.classList.remove('active', 'completed');
    if (nodeStep < stepNum) {
      node.classList.add('completed');
    } else if (nodeStep === stepNum) {
      node.classList.add('active');
    }
  });
}

/**
 * Handle instant AJAX Product Deletion with row animation
 */
function initMakerDeleteProductAjax() {
  document.querySelectorAll('.btn-delete-product-ajax').forEach(btn => {
    if (btn.dataset.ajaxBound) return;
    btn.dataset.ajaxBound = 'true';

    btn.addEventListener('click', function(e) {
      e.preventDefault();
      const prodId = this.getAttribute('data-product-id');
      const prodName = this.getAttribute('data-product-name') || 'this delicacy';

      if (!confirm(`Are you sure you want to remove "${prodName}" from your catalog?`)) {
        return;
      }

      const row = document.getElementById(`prod-row-${prodId}`) || this.closest('tr');
      const originalHtml = this.innerHTML;
      this.disabled = true;
      this.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i>';

      fetch(`/delete-product/${prodId}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-Requested-With': 'XMLHttpRequest'
        }
      })
      .then(res => res.json())
      .then(data => {
        if (data.success) {
          if (row) {
            row.style.opacity = '0';
            row.style.transform = 'scale(0.95)';
            row.style.transition = 'all 0.25s ease';
            setTimeout(() => {
              row.remove();
              // Update active product count if badge exists
              const countEl = document.querySelector('#maker-metric-active-delicacies');
              if (countEl) {
                const count = parseInt(countEl.textContent.trim()) || 0;
                countEl.textContent = Math.max(0, count - 1);
              }
            }, 250);
          }
          if (typeof showToast === 'function') {
            showToast(data.message, 'info');
          }
        } else {
          this.disabled = false;
          this.innerHTML = originalHtml;
          if (typeof showToast === 'function') {
            showToast(data.message || 'Error deleting product', 'error');
          }
        }
      })
      .catch(err => {
        this.disabled = false;
        this.innerHTML = originalHtml;
        const parentForm = this.closest('form');
        if (parentForm) parentForm.submit();
      });
    });
  });
}

/**
 * Instant Client-Side Image Previews on File Selection
 */
function initImagePreviews() {
  const inputs = document.querySelectorAll('input[type="file"][accept*="image"], #prod-image, #daily-image');
  inputs.forEach(input => {
    input.addEventListener('change', function() {
      const file = this.files && this.files[0];
      if (!file) return;

      // Ensure file is an image
      if (!file.type.startsWith('image/')) return;

      // Find or create preview container
      let previewContainer = document.getElementById(`${this.id}-preview`);
      if (!previewContainer) {
        previewContainer = document.createElement('div');
        previewContainer.id = `${this.id}-preview`;
        previewContainer.style.marginTop = '10px';
        previewContainer.style.display = 'flex';
        previewContainer.style.alignItems = 'center';
        previewContainer.style.gap = '12px';
        previewContainer.style.padding = '8px 12px';
        previewContainer.style.background = '#FAF7F2';
        previewContainer.style.borderRadius = '10px';
        previewContainer.style.border = '1px solid #ECE7DE';
        this.parentNode.insertBefore(previewContainer, this.nextSibling);
      }

      const reader = new FileReader();
      reader.onload = function(e) {
        const sizeKb = Math.round(file.size / 1024);
        previewContainer.innerHTML = `
          <img src="${e.target.result}" alt="Preview" style="width: 52px; height: 52px; border-radius: 8px; object-fit: cover; border: 1px solid #D5C8B4; box-shadow: 0 2px 4px rgba(0,0,0,0.06);">
          <div style="font-size: 0.82rem; color: #2C3E50;">
            <strong style="display:block; color: #1C2321;">${file.name}</strong>
            <span>${sizeKb} KB &bull; <i class="fa-solid fa-circle-check" style="color: #27AE60;"></i> Ready for upload</span>
          </div>
        `;
      };
      reader.readAsDataURL(file);
    });
  });
}

/**
 * Button Loading State on Form Submit to prevent double clicks and show speed
 */
function initSubmitButtonSpinners() {
  document.querySelectorAll('form').forEach(form => {
    // Avoid double binding or intercepting forms handled by AJAX
    if (form.classList.contains('order-status-ajax-form')) return;

    form.addEventListener('submit', function(e) {
      if (typeof this.checkValidity === 'function' && !this.checkValidity()) {
        return;
      }
      const submitBtn = this.querySelector('button[type="submit"]');
      if (submitBtn && !submitBtn.disabled) {
        setTimeout(() => {
          submitBtn.disabled = true;
          const orig = submitBtn.innerHTML;
          submitBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Processing...';
          // Auto-restore after 8s in case user cancels
          setTimeout(() => {
            submitBtn.disabled = false;
            submitBtn.innerHTML = orig;
          }, 8000);
        }, 50);
      }
    });
  });
}
