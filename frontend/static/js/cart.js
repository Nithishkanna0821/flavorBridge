// ==========================================================================
// FlavorBridge Cart Management & AJAX Sync
// ==========================================================================

document.addEventListener('DOMContentLoaded', () => {
  initCartButtons();
  initCartQuantityControls();
  fetchCartCount();
});

/**
 * Fetch and update live cart badge count across pages
 */
function fetchCartCount() {
  fetch('/api/cart-count')
    .then(res => res.json())
    .then(data => {
      updateCartBadge(data.count);
    })
    .catch(err => console.debug('Cart sync:', err));
}

function updateCartBadge(count) {
  const badges = document.querySelectorAll('.cart-badge');
  badges.forEach(badge => {
    badge.textContent = count;
    badge.style.display = count > 0 ? 'flex' : 'none';
  });
}

/**
 * Handle Add to Cart button clicks asynchronously with Single-Kitchen Conflict Management
 */
function initCartButtons() {
  document.querySelectorAll('.btn-add-to-cart-ajax').forEach(btn => {
    if (btn.dataset.cartBound) return;
    btn.dataset.cartBound = 'true';

    btn.addEventListener('click', function(e) {
      e.preventDefault();
      const productId = this.getAttribute('data-product-id');
      const qtyInput = document.querySelector(`#qty-${productId}`) || document.querySelector('#detail-qty');
      const quantity = qtyInput ? parseInt(qtyInput.value) || 1 : 1;

      const originalHtml = this.innerHTML;
      this.disabled = true;
      this.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Adding...';

      fetch('/add-to-cart', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-Requested-With': 'XMLHttpRequest'
        },
        body: JSON.stringify({
          product_id: parseInt(productId),
          quantity: quantity
        })
      })
      .then(async res => {
        const data = await res.json();
        return { status: res.status, data };
      })
      .then(({ status, data }) => {
        this.disabled = false;
        
        if (data.success) {
          this.innerHTML = '<i class="fa-solid fa-check"></i> Added!';
          this.classList.add('btn-secondary');
          this.classList.remove('btn-primary');
          updateCartBadge(data.cart_count);
          showToast(data.message, 'success');

          setTimeout(() => {
            this.innerHTML = originalHtml;
            this.classList.remove('btn-secondary');
            this.classList.add('btn-primary');
          }, 2000);
        } else if (data.conflict) {
          // Single-kitchen order conflict detected
          this.innerHTML = originalHtml;
          showKitchenConflictModal(data, this, originalHtml);
        } else {
          this.innerHTML = originalHtml;
          showToast(data.message || 'Error adding to cart', 'error');
        }
      })
      .catch(err => {
        this.disabled = false;
        this.innerHTML = originalHtml;
        showToast('Please sign in to add items to your cart. Redirecting to login...', 'info');
        setTimeout(() => {
          window.location.href = '/login?next=' + encodeURIComponent(window.location.pathname + window.location.search);
        }, 1200);
      });
    });
  });
}

/**
 * Modern modal when trying to mix items from multiple kitchens in a single cart
 */
function showKitchenConflictModal(conflictData, originalBtn, originalHtml) {
  const existingModal = document.querySelector('#kitchen-conflict-modal');
  if (existingModal) existingModal.remove();

  const modal = document.createElement('div');
  modal.id = 'kitchen-conflict-modal';
  modal.style.position = 'fixed';
  modal.style.top = '0';
  modal.style.left = '0';
  modal.style.width = '100vw';
  modal.style.height = '100vh';
  modal.style.backgroundColor = 'rgba(28, 35, 33, 0.65)';
  modal.style.backdropFilter = 'blur(5px)';
  modal.style.zIndex = '10000';
  modal.style.display = 'flex';
  modal.style.alignItems = 'center';
  modal.style.justifyContent = 'center';
  modal.style.padding = '1.25rem';
  modal.style.animation = 'fadeIn 0.2s ease-in-out';

  modal.innerHTML = `
    <div style="background: #FFFFFF; border-radius: 20px; max-width: 480px; width: 100%; padding: 2.25rem 2rem; box-shadow: 0 24px 48px rgba(0,0,0,0.22); border: 1px solid #ECE7DE; text-align: center;">
      <div style="width: 64px; height: 64px; border-radius: 50%; background: #FEF9E7; color: #D35400; display: flex; align-items: center; justify-content: center; font-size: 1.9rem; margin: 0 auto 1.25rem; border: 1px solid #F9E79F;">
        <i class="fa-solid fa-kitchen-set"></i>
      </div>
      <h3 style="font-size: 1.35rem; margin-bottom: 0.75rem; color: #1C2321; font-weight: 800; font-family: var(--font-heading, inherit);">Order from One Kitchen at a Time</h3>
      <p style="font-size: 0.92rem; color: #555; line-height: 1.55; margin-bottom: 1.75rem;">
        Your cart already contains delicacies from <strong>"${conflictData.existing_kitchen}"</strong>.
        <br><br>
        To ensure regional authenticity and fresh single-origin dispatch, each order is prepared by <strong>one artisan kitchen</strong>.
        <br><br>
        Would you like to clear your current cart and start an order with <strong>"${conflictData.new_kitchen}"</strong>?
      </p>
      <div style="display: flex; gap: 0.85rem; justify-content: center; flex-wrap: wrap;">
        <button type="button" id="btn-cancel-conflict" class="btn btn-outline" style="flex: 1; min-width: 140px; padding: 0.75rem 1rem;">
          Keep Existing Cart
        </button>
        <button type="button" id="btn-confirm-reset-cart" class="btn btn-primary" style="flex: 1; min-width: 160px; padding: 0.75rem 1rem;">
          <i class="fa-solid fa-rotate"></i> Clear & Add New
        </button>
      </div>
    </div>
  `;

  document.body.appendChild(modal);

  document.querySelector('#btn-cancel-conflict').addEventListener('click', () => {
    modal.remove();
  });

  // Close on outside background click
  modal.addEventListener('click', (e) => {
    if (e.target === modal) modal.remove();
  });

  document.querySelector('#btn-confirm-reset-cart').addEventListener('click', () => {
    const confirmBtn = document.querySelector('#btn-confirm-reset-cart');
    confirmBtn.disabled = true;
    confirmBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Switching...';

    fetch('/add-to-cart', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-Requested-With': 'XMLHttpRequest'
      },
      body: JSON.stringify({
        product_id: conflictData.product_id,
        quantity: conflictData.quantity,
        reset_cart: true
      })
    })
    .then(res => res.json())
    .then(data => {
      modal.remove();
      if (data.success) {
        if (originalBtn && originalHtml) {
          originalBtn.disabled = false;
          originalBtn.innerHTML = '<i class="fa-solid fa-check"></i> Added!';
          originalBtn.classList.add('btn-secondary');
          originalBtn.classList.remove('btn-primary');
          setTimeout(() => {
            originalBtn.innerHTML = originalHtml;
            originalBtn.classList.remove('btn-secondary');
            originalBtn.classList.add('btn-primary');
          }, 2000);
        }
        updateCartBadge(data.cart_count);
        showToast(`Cart updated to ${conflictData.new_kitchen}!`, 'success');
      } else {
        showToast(data.message || 'Error updating cart', 'error');
      }
    })
    .catch(err => {
      modal.remove();
      showToast('Error switching kitchen', 'error');
    });
  });
}

/**
 * Handle cart quantity increment/decrement and live subtotal updates
 */
function initCartQuantityControls() {
  document.querySelectorAll('.cart-qty-btn').forEach(btn => {
    // Avoid double binding
    if (btn.dataset.bound) return;
    btn.dataset.bound = 'true';

    btn.addEventListener('click', function(e) {
      e.preventDefault();
      const itemId = this.getAttribute('data-item-id');
      const action = this.getAttribute('data-action');
      
      // Find associated input (either in the same stepper or by ID)
      const stepper = this.closest('.quantity-stepper');
      const input = stepper ? stepper.querySelector('input') : document.querySelector(`#cart-qty-input-${itemId}`);
      if (!input) return;

      let currentVal = parseInt(input.value) || 1;
      if (action === 'increase') {
        currentVal += 1;
      } else if (action === 'decrease') {
        currentVal = Math.max(0, currentVal - 1);
      }

      // Update input display immediately
      input.value = currentVal;
      updateCartItemQuantity(itemId, currentVal);
    });
  });
}

function updateCartItemQuantity(itemId, quantity) {
  fetch('/update-cart', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-Requested-With': 'XMLHttpRequest'
    },
    body: JSON.stringify({
      item_id: parseInt(itemId),
      quantity: quantity
    })
  })
  .then(res => res.json())
  .then(data => {
    if (data.success) {
      if (quantity === 0) {
        // Smoothly remove row from cart table and checkout summary
        const row = document.querySelector(`#cart-row-${itemId}`);
        if (row) {
          row.style.opacity = '0';
          row.style.transform = 'scale(0.95)';
          row.style.transition = 'all 0.25s ease';
          setTimeout(() => row.remove(), 250);
        }

        const checkoutItem = document.querySelector(`#checkout-item-${itemId}`);
        if (checkoutItem) {
          checkoutItem.style.opacity = '0';
          checkoutItem.style.transform = 'scale(0.95)';
          checkoutItem.style.transition = 'all 0.25s ease';
          setTimeout(() => checkoutItem.remove(), 250);
        }

        showToast('Delicacy removed from your cart.', 'info');

        if (data.cart_count === 0) {
          setTimeout(() => window.location.reload(), 300);
          return;
        }
      } else {
        // Sync all quantity inputs for this item on the page
        document.querySelectorAll(`input[id^="cart-qty-input-${itemId}"]`).forEach(inp => {
          inp.value = quantity;
        });

        // Update item subtotals
        const itemSubtotalEl = document.querySelector(`#item-subtotal-${itemId}`);
        if (itemSubtotalEl) {
          itemSubtotalEl.textContent = `₹${data.item_subtotal.toFixed(2)}`;
        }
        const checkoutSubtotalEl = document.querySelector(`#checkout-subtotal-${itemId}`);
        if (checkoutSubtotalEl) {
          checkoutSubtotalEl.textContent = `₹${data.item_subtotal.toFixed(2)}`;
        }
      }

      // Update Cart Page Summary Cards
      const subtotalEl = document.querySelector('#cart-subtotal-val');
      const deliveryEl = document.querySelector('#cart-delivery-val');
      const totalEl = document.querySelector('#cart-total-val');

      if (subtotalEl) subtotalEl.textContent = `₹${data.subtotal.toFixed(2)}`;
      if (deliveryEl) deliveryEl.textContent = data.delivery_fee === 0 ? 'FREE' : `₹${data.delivery_fee.toFixed(2)}`;
      if (totalEl) totalEl.textContent = `₹${data.total.toFixed(2)}`;

      // Update Checkout Page Summary Cards
      const checkoutSubtotal = document.querySelector('#checkout-subtotal-val');
      const checkoutDelivery = document.querySelector('#checkout-delivery-val');
      const checkoutTotal = document.querySelector('#checkout-total-val');
      const checkoutCount = document.querySelector('#checkout-count-val');

      if (checkoutSubtotal) checkoutSubtotal.textContent = `₹${data.subtotal.toFixed(2)}`;
      if (checkoutDelivery) checkoutDelivery.textContent = data.delivery_fee === 0 ? 'FREE' : `₹${data.delivery_fee.toFixed(2)}`;
      if (checkoutTotal) checkoutTotal.textContent = `₹${data.total.toFixed(2)}`;
      if (checkoutCount) checkoutCount.textContent = `(${data.cart_count} Items)`;

      // Update navigation cart count badges
      updateCartBadge(data.cart_count);
    } else {
      showToast(data.message || 'Error updating quantity', 'error');
    }
  })
  .catch(err => console.error('Cart update error:', err));
}

/**
 * Reusable dynamic toast popup notification
 */
function showToast(message, type = 'info') {
  let container = document.querySelector('#toast-container');
  if (!container) {
    container = document.createElement('div');
    container.id = 'toast-container';
    container.style.position = 'fixed';
    container.style.bottom = '24px';
    container.style.right = '24px';
    container.style.zIndex = '9999';
    container.style.display = 'flex';
    container.style.flexDirection = 'column';
    container.style.gap = '10px';
    document.body.appendChild(container);
  }

  const toast = document.createElement('div');
  const bgColor = type === 'success' ? '#27AE60' : type === 'error' ? '#C0392B' : '#D35400';
  toast.style.background = bgColor;
  toast.style.color = '#FFFFFF';
  toast.style.padding = '12px 20px';
  toast.style.borderRadius = '10px';
  toast.style.boxShadow = '0 6px 16px rgba(0,0,0,0.15)';
  toast.style.fontSize = '0.92rem';
  toast.style.fontWeight = '600';
  toast.style.display = 'flex';
  toast.style.alignItems = 'center';
  toast.style.gap = '8px';
  toast.style.animation = 'fadeIn 0.2s ease-in-out';

  const icon = type === 'success' ? 'fa-circle-check' : type === 'error' ? 'fa-circle-exclamation' : 'fa-bell';
  toast.innerHTML = `<i class="fa-solid ${icon}"></i> <span>${message}</span>`;

  container.appendChild(toast);

  setTimeout(() => {
    toast.style.opacity = '0';
    toast.style.transform = 'translateY(10px)';
    toast.style.transition = 'all 0.3s ease';
    setTimeout(() => toast.remove(), 300);
  }, 3500);
}
