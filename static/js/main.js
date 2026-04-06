// ═══════════════════════════════════════
//  IELTS Mentor — Main JS
// ═══════════════════════════════════════

// ── Mobile nav ─────────────────────────
const hamburger = document.getElementById('hamburger');
const navLinks  = document.getElementById('navLinks');
if (hamburger) {
  hamburger.addEventListener('click', () => {
    navLinks.classList.toggle('open');
  });
}

// ── AI Chat ─────────────────────────────
const chatToggle  = document.getElementById('chatToggle');
const chatPanel   = document.getElementById('chatPanel');
const chatClose   = document.getElementById('chatClose');
const chatInput   = document.getElementById('chatInput');
const chatSend    = document.getElementById('chatSend');
const chatMessages= document.getElementById('chatMessages');

if (chatToggle) {
  chatToggle.addEventListener('click', () => chatPanel.classList.toggle('open'));
  chatClose.addEventListener('click', () => chatPanel.classList.remove('open'));

  async function sendChat() {
    const msg = chatInput.value.trim();
    if (!msg) return;
    appendMsg(msg, 'user');
    chatInput.value = '';
    const typing = appendMsg('Thinking... 🤔', 'bot', true);
    try {
      const res = await fetch('/api/ai-chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: msg })
      });
      const data = await res.json();
      typing.remove();
      appendMsg(data.response, 'bot');
    } catch {
      typing.remove();
      appendMsg('Sorry, I had a connection issue. Check your internet and try again!', 'bot');
    }
  }

  chatSend.addEventListener('click', sendChat);
  chatInput.addEventListener('keydown', e => { if (e.key === 'Enter') sendChat(); });

  function appendMsg(text, role, typing = false) {
    const div = document.createElement('div');
    div.className = `chat-msg ${role}`;
    div.innerHTML = `
      <span class="msg-avatar">${role === 'bot' ? '🤖' : '👤'}</span>
      <div class="msg-bubble ${typing ? 'chat-typing' : ''}">${text}</div>
    `;
    chatMessages.appendChild(div);
    chatMessages.scrollTop = chatMessages.scrollHeight;
    return div;
  }
}

// ── XP Toast ────────────────────────────
function showXP(amount) {
  const toast = document.getElementById('xpToast');
  if (!toast) return;
  toast.textContent = `+${amount} XP 🎯`;
  toast.classList.add('show');
  setTimeout(() => toast.classList.remove('show'), 2500);
}

// ── Word counter for textarea ────────────
document.querySelectorAll('.writing-area').forEach(area => {
  const counter = area.parentElement.querySelector('.word-count');
  if (!counter) return;
  area.addEventListener('input', () => {
    const words = area.value.trim() ? area.value.trim().split(/\s+/).length : 0;
    const minWords = parseInt(area.dataset.minWords || 150);
    const color = words >= minWords ? '#3fb950' : words >= minWords * 0.8 ? '#f0883e' : '#8b949e';
    counter.textContent = `${words} words ${words >= minWords ? '✓' : `(need ${minWords - words} more)`}`;
    counter.style.color = color;
  });
});

// ── Vocabulary flashcard flip ────────────
document.querySelectorAll('.vocab-known-btn').forEach(btn => {
  btn.addEventListener('click', async () => {
    const word = btn.dataset.word;
    const res = await fetch('/api/mark-word', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ word })
    });
    const data = await res.json();
    btn.textContent = '✓ Known';
    btn.classList.add('known');
    btn.disabled = true;
    showXP(2);
    const countEl = document.getElementById('knownCount');
    if (countEl) countEl.textContent = data.known_count;
  });
});

// ── Schedule week toggle ─────────────────
document.querySelectorAll('.week-header').forEach(header => {
  header.addEventListener('click', () => {
    const days = header.nextElementSibling;
    const isOpen = !days.classList.contains('hidden');
    document.querySelectorAll('.week-days').forEach(d => d.classList.add('hidden'));
    if (!isOpen) days.classList.remove('hidden');
  });
});

// ── Open current week on schedule page ───
const currentWeekEl = document.querySelector('.week-card.current-week .week-days');
if (currentWeekEl) currentWeekEl.classList.remove('hidden');
