// ==========================================================================
// FlavorBridge Regional Food Assistant Chat Logic
// ==========================================================================

document.addEventListener('DOMContentLoaded', () => {
  const chatBody = document.querySelector('#assistant-chat-body');
  const chatInput = document.querySelector('#assistant-user-input');
  const sendBtn = document.querySelector('#assistant-send-btn');
  const chipsContainer = document.querySelector('#assistant-quick-chips');

  if (!chatBody || !chatInput || !sendBtn) return;

  // Send message on click
  sendBtn.addEventListener('click', () => {
    submitAssistantMessage();
  });

  // Send message on Enter key
  chatInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') {
      submitAssistantMessage();
    }
  });

  // Handle quick prompt chip clicks
  if (chipsContainer) {
    chipsContainer.addEventListener('click', (e) => {
      const chip = e.target.closest('.prompt-chip');
      if (chip) {
        const query = chip.getAttribute('data-prompt') || chip.textContent.trim();
        chatInput.value = query;
        submitAssistantMessage();
      }
    });
  }

  function submitAssistantMessage() {
    const query = chatInput.value.trim();
    if (!query) return;

    // Append User Bubble
    appendUserBubble(query);
    chatInput.value = '';
    chatInput.focus();

    // Append Typing Indicator
    const typingId = appendTypingIndicator();

    // Call Backend AI NLP API
    fetch('/api/food-assistant', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-Requested-With': 'XMLHttpRequest'
      },
      body: JSON.stringify({ query: query })
    })
    .then(res => res.json())
    .then(data => {
      removeTypingIndicator(typingId);
      appendBotResponse(data);
    })
    .catch(err => {
      removeTypingIndicator(typingId);
      appendBotBubble("I encountered an issue processing your regional query. Please try searching again!");
    });
  }

  function appendUserBubble(text) {
    const bubble = document.createElement('div');
    bubble.className = 'chat-bubble chat-bubble-user';
    bubble.textContent = text;
    chatBody.appendChild(bubble);
    scrollChatToBottom();
  }

  function appendBotBubble(text) {
    const bubble = document.createElement('div');
    bubble.className = 'chat-bubble chat-bubble-bot';
    bubble.innerHTML = `<p>${text}</p>`;
    chatBody.appendChild(bubble);
    scrollChatToBottom();
  }

  function appendTypingIndicator() {
    const id = 'typing-' + Date.now();
    const bubble = document.createElement('div');
    bubble.id = id;
    bubble.className = 'chat-bubble chat-bubble-bot';
    bubble.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Finding authentic regional culinary matches...';
    chatBody.appendChild(bubble);
    scrollChatToBottom();
    return id;
  }

  function removeTypingIndicator(id) {
    const el = document.getElementById(id);
    if (el) el.remove();
  }

  function appendBotResponse(data) {
    const wrapper = document.createElement('div');
    wrapper.className = 'chat-bubble chat-bubble-bot';
    wrapper.style.width = '100%';
    wrapper.style.maxWidth = '100%';

    let html = `<p style="font-weight: 600; margin-bottom: 0.85rem; color: #1C2321;">${data.reply}</p>`;

    if (data.products && data.products.length > 0) {
      html += `<div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); gap: 1rem; margin-top: 1rem;">`;
      
      data.products.forEach(p => {
        const verifiedTag = p.maker_verified ? '<span class="badge badge-verified" style="font-size:0.68rem;"><i class="fa-solid fa-circle-check"></i> Verified</span>' : '';
        const typeBadge = p.product_type === 'Fresh Food' ? '<span class="badge badge-fresh" style="font-size:0.68rem;">Fresh</span>' : '<span class="badge badge-packaged" style="font-size:0.68rem;">Packaged</span>';

        html += `
          <div style="background:#FFFFFF; border:1px solid #ECE7DE; border-radius:12px; padding:12px; display:flex; flex-direction:column; box-shadow:0 2px 6px rgba(0,0,0,0.04);">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:6px;">
              ${typeBadge}
              ${verifiedTag}
            </div>
            <h4 style="font-size:1rem; margin-bottom:4px; color:#1C2321;">${p.name}</h4>
            <div style="font-size:0.78rem; color:#718096; margin-bottom:6px;"><i class="fa-solid fa-location-dot"></i> ${p.city} • ${p.maker_name}</div>
            <div style="font-size:0.75rem; color:#D35400; font-weight:600; margin-bottom:10px; background:#FDF2E9; padding:3px 6px; border-radius:4px;">${p.match_reason}</div>
            <div style="margin-top:auto; display:flex; align-items:center; justify-content:space-between; padding-top:8px; border-top:1px solid #F7FAFC;">
              <span style="font-weight:800; font-size:1.1rem; color:#1C2321;">₹${p.price}</span>
              <div style="display:flex; gap:6px;">
                <a href="/product/${p.id}" class="btn btn-outline btn-sm" style="padding:4px 8px; font-size:0.78rem;">View</a>
                <button class="btn btn-primary btn-sm btn-add-to-cart-ajax" data-product-id="${p.id}" style="padding:4px 8px; font-size:0.78rem;"><i class="fa-solid fa-cart-plus"></i></button>
              </div>
            </div>
          </div>
        `;
      });
      html += `</div>`;
    }

    if (data.safety_note) {
      html += `<div style="font-size:0.74rem; color:#718096; margin-top:12px; padding-top:8px; border-top:1px dashed #E2E8F0; display:flex; align-items:center; gap:6px;">
        <i class="fa-solid fa-shield-halved" style="color:#27AE60;"></i> ${data.safety_note}
      </div>`;
    }

    wrapper.innerHTML = html;
    chatBody.appendChild(wrapper);
    scrollChatToBottom();

    // Re-bind dynamic cart buttons inside the chat
    if (typeof initCartButtons === 'function') {
      initCartButtons();
    }
  }

  function scrollChatToBottom() {
    chatBody.scrollTop = chatBody.scrollHeight;
  }
});
