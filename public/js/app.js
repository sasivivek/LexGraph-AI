/**
 * LexGraph AI — Frontend Application
 * Interactive Legal AI Assistant with Knowledge Graph
 */

const API_BASE = '';
let allSections = [];
let graphStats = null;

// ============================================
// CHAT STATE
// ============================================
let chatSessionId = '';
let chatTurnCount = 0;
let isChatSending = false;

// ============================================
// INITIALIZATION
// ============================================
document.addEventListener('DOMContentLoaded', () => {
  initNavigation();
  initChatInput();
  checkHealth();
  loadSections();
  loadAmendments();
  loadRules();
  loadGraphStats();
});

// ============================================
// NAVIGATION
// ============================================
function initNavigation() {
  document.querySelectorAll('.nav-btn').forEach((btn) => {
    btn.addEventListener('click', () => {
      const panel = btn.dataset.panel;
      switchPanel(panel);
    });
  });
}

function switchPanel(panelName) {
  document.querySelectorAll('.nav-btn').forEach((b) => b.classList.remove('active'));
  const activeBtn = document.querySelector(`[data-panel="${panelName}"]`);
  if (activeBtn) activeBtn.classList.add('active');

  document.querySelectorAll('.panel').forEach((p) => p.classList.remove('active'));
  const activePanel = document.getElementById(`panel-${panelName}`);
  if (activePanel) activePanel.classList.add('active');
}

// ============================================
// HEALTH CHECK
// ============================================
async function checkHealth() {
  const statusEl = document.getElementById('connection-status');
  const dotEl = statusEl.querySelector('.status-dot');
  const textEl = statusEl.querySelector('span:last-child');

  try {
    const res = await fetch(`${API_BASE}/api/health`);
    const data = await res.json();

    if (data.neo4j === 'connected') {
      dotEl.className = 'status-dot connected';
      textEl.textContent = 'Neo4j Connected';
    } else {
      dotEl.className = 'status-dot disconnected';
      textEl.textContent = 'Neo4j Disconnected';
    }
  } catch (e) {
    dotEl.className = 'status-dot disconnected';
    textEl.textContent = 'Server Offline';
  }
}

// ============================================
// INTERACTIVE CHAT (ChatGPT-like)
// ============================================
function initChatInput() {
  const textarea = document.getElementById('chat-input');

  // Auto-expand textarea
  textarea.addEventListener('input', () => {
    textarea.style.height = 'auto';
    textarea.style.height = Math.min(textarea.scrollHeight, 160) + 'px';
  });

  // Send on Enter, newline on Shift+Enter
  textarea.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendChatMessage();
    }
  });
}

function sendChatFromPrompt(text) {
  document.getElementById('chat-input').value = text;
  sendChatMessage();
}

async function sendChatMessage() {
  const textarea = document.getElementById('chat-input');
  const message = textarea.value.trim();
  if (!message || isChatSending) return;

  isChatSending = true;
  textarea.value = '';
  textarea.style.height = 'auto';

  // Hide welcome screen
  const welcome = document.getElementById('chat-welcome');
  if (welcome) welcome.style.display = 'none';

  // Add user message
  addUserMessage(message);
  showTypingIndicator();
  updateSendButton(true);

  try {
    const res = await fetch(`${API_BASE}/api/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        message: message,
        session_id: chatSessionId,
      }),
    });

    const data = await res.json();
    removeTypingIndicator();

    if (data.success) {
      chatSessionId = data.session_id;
      chatTurnCount = data.turn_count;
      addAIMessage(data.reply, data.source, data.has_context);
      updateSessionInfo();
    } else {
      addSystemMessage(`⚠️ Error: ${data.error || 'Unknown error'}`);
    }
  } catch (e) {
    removeTypingIndicator();
    addSystemMessage('⚠️ Could not reach the server. Please ensure it is running.');
  }

  isChatSending = false;
  updateSendButton(false);
  textarea.focus();
}

function startNewChat() {
  // Clear session on server
  if (chatSessionId) {
    fetch(`${API_BASE}/api/chat/clear`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ session_id: chatSessionId }),
    }).catch(() => {});
  }

  chatSessionId = '';
  chatTurnCount = 0;

  const messagesEl = document.getElementById('chat-messages');
  messagesEl.innerHTML = '';

  // Re-create welcome screen
  messagesEl.innerHTML = createWelcomeHTML();
  updateSessionInfo();
}

function clearCurrentChat() {
  if (chatTurnCount === 0) return;

  if (confirm('Clear this conversation? This cannot be undone.')) {
    startNewChat();
  }
}

function updateSessionInfo() {
  const statusText = document.getElementById('chat-status-text');
  const sessionDot = document.querySelector('.session-dot');

  if (chatTurnCount > 0) {
    statusText.textContent = `${chatTurnCount} exchange${chatTurnCount !== 1 ? 's' : ''} • Session active`;
    sessionDot.classList.add('active');
  } else {
    statusText.textContent = 'New conversation';
    sessionDot.classList.remove('active');
  }
}

function updateSendButton(sending) {
  const btn = document.getElementById('chat-send');
  if (sending) {
    btn.classList.add('sending');
    btn.disabled = true;
  } else {
    btn.classList.remove('sending');
    btn.disabled = false;
  }
}

// ============================================
// CHAT MESSAGE RENDERING
// ============================================
function addUserMessage(text) {
  const container = document.getElementById('chat-messages');
  const msg = document.createElement('div');
  msg.className = 'message user';

  msg.innerHTML = `
    <div class="message-avatar user-avatar">
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <path d="M20 21v-2a4 4 0 00-4-4H8a4 4 0 00-4 4v2"/>
        <circle cx="12" cy="7" r="4"/>
      </svg>
    </div>
    <div class="message-content">
      <p>${escapeHtml(text)}</p>
    </div>
  `;

  container.appendChild(msg);
  scrollToBottom();
}

function addAIMessage(text, source, hasContext) {
  const container = document.getElementById('chat-messages');
  const msg = document.createElement('div');
  msg.className = 'message ai';

  const renderedText = renderMarkdown(text);

  let metaHtml = '';
  if (hasContext) {
    metaHtml = '<div class="response-meta"><span class="meta-pill grounded">📊 Graph-Grounded</span></div>';
  }

  msg.innerHTML = `
    <div class="message-avatar ai-avatar">
      <svg width="18" height="18" viewBox="0 0 28 28" fill="none">
        <path d="M14 2L2 8v12l12 6 12-6V8L14 2z" stroke="currentColor" stroke-width="1.5" fill="none"/>
        <circle cx="14" cy="14" r="3" fill="currentColor" opacity="0.6"/>
      </svg>
    </div>
    <div class="message-content ai-content">
      <div class="ai-response-text">${renderedText}</div>
      ${metaHtml}
    </div>
  `;

  container.appendChild(msg);
  scrollToBottom();
}

function addSystemMessage(text) {
  const container = document.getElementById('chat-messages');
  const msg = document.createElement('div');
  msg.className = 'message system';

  msg.innerHTML = `
    <div class="message-avatar system-avatar">
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <circle cx="12" cy="12" r="10"/>
        <path d="M12 16v-4M12 8h.01"/>
      </svg>
    </div>
    <div class="message-content">
      <p>${text}</p>
    </div>
  `;

  container.appendChild(msg);
  scrollToBottom();
}

function showTypingIndicator() {
  const container = document.getElementById('chat-messages');
  const indicator = document.createElement('div');
  indicator.className = 'message ai';
  indicator.id = 'typing-indicator';

  indicator.innerHTML = `
    <div class="message-avatar ai-avatar">
      <svg width="18" height="18" viewBox="0 0 28 28" fill="none">
        <path d="M14 2L2 8v12l12 6 12-6V8L14 2z" stroke="currentColor" stroke-width="1.5" fill="none"/>
        <circle cx="14" cy="14" r="3" fill="currentColor" opacity="0.6"/>
      </svg>
    </div>
    <div class="message-content ai-content">
      <div class="typing-indicator">
        <div class="typing-text">Analyzing with knowledge graph</div>
        <div class="typing-dots">
          <span></span><span></span><span></span>
        </div>
      </div>
    </div>
  `;

  container.appendChild(indicator);
  scrollToBottom();
}

function removeTypingIndicator() {
  const indicator = document.getElementById('typing-indicator');
  if (indicator) indicator.remove();
}

function scrollToBottom() {
  const container = document.getElementById('chat-messages');
  requestAnimationFrame(() => {
    container.scrollTop = container.scrollHeight;
  });
}

// ============================================
// LEGACY SUPPORT — Natural Language Query (still available via /api/query/natural)
// ============================================
function askQuestion(question) {
  document.getElementById('chat-input').value = question;
  sendChatMessage();
}

// ============================================
// WELCOME SCREEN HTML GENERATOR
// ============================================
function createWelcomeHTML() {
  return `
    <div class="chat-welcome" id="chat-welcome">
      <div class="welcome-icon">
        <svg width="48" height="48" viewBox="0 0 28 28" fill="none">
          <path d="M14 2L2 8v12l12 6 12-6V8L14 2z" stroke="url(#wg2)" stroke-width="1.5" fill="none"/>
          <path d="M14 8l-6 3v6l6 3 6-3v-6l-6-3z" fill="url(#wg2)" opacity="0.2"/>
          <circle cx="14" cy="14" r="3" fill="url(#wg2)"/>
          <defs><linearGradient id="wg2" x1="0" y1="0" x2="28" y2="28"><stop stop-color="#818cf8"/><stop offset="1" stop-color="#6366f1"/></linearGradient></defs>
        </svg>
      </div>
      <h3>Welcome to LexGraph AI</h3>
      <p>Your intelligent legal assistant for the Companies Act, 2013. Ask me anything about sections, amendments, rules, compliance, or corporate law concepts.</p>
      
      <div class="welcome-grid">
        <div class="welcome-category">
          <div class="welcome-category-title">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>
            Sections & Provisions
          </div>
          <button class="welcome-prompt" onclick="sendChatFromPrompt('What does Section 149 say about independent directors?')">What does Section 149 say about independent directors?</button>
          <button class="welcome-prompt" onclick="sendChatFromPrompt('Explain Section 185 on loans to directors')">Explain Section 185 on loans to directors</button>
        </div>
        <div class="welcome-category">
          <div class="welcome-category-title">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M11 4H4a2 2 0 00-2 2v14a2 2 0 002 2h14a2 2 0 002-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 013 3L12 15l-4 1 1-4 9.5-9.5z"/></svg>
            Amendments & Changes
          </div>
          <button class="welcome-prompt" onclick="sendChatFromPrompt('What sections were amended in 2026?')">What sections were amended in 2026?</button>
          <button class="welcome-prompt" onclick="sendChatFromPrompt('How has Section 135 on CSR changed?')">How has Section 135 on CSR changed?</button>
        </div>
        <div class="welcome-category">
          <div class="welcome-category-title">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><path d="M12 16v-4M12 8h.01"/></svg>
            Compliance & Concepts
          </div>
          <button class="welcome-prompt" onclick="sendChatFromPrompt('What are the duties of a company director?')">What are the duties of a company director?</button>
          <button class="welcome-prompt" onclick="sendChatFromPrompt('Explain the process for declaring dividends')">Explain the process for declaring dividends</button>
        </div>
        <div class="welcome-category">
          <div class="welcome-category-title">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/></svg>
            Rules & Definitions
          </div>
          <button class="welcome-prompt" onclick="sendChatFromPrompt('What rules apply to audit committees?')">What rules apply to audit committees?</button>
          <button class="welcome-prompt" onclick="sendChatFromPrompt('Define small company under the Act')">Define "small company" under the Act</button>
        </div>
      </div>
    </div>
  `;
}

// ============================================
// BROWSE SECTIONS
// ============================================
async function loadSections() {
  try {
    const res = await fetch(`${API_BASE}/api/sections`);
    const data = await res.json();

    if (data.success) {
      allSections = data.data;
      renderSections(allSections);
      populateGraphSelect(allSections);
    } else {
      document.getElementById('sections-list').innerHTML = `
        <div class="empty-state">
          <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1"><circle cx="12" cy="12" r="10"/><path d="M12 16v-4M12 8h.01"/></svg>
          <p>Could not load sections. Ensure Neo4j is running and data is ingested.</p>
        </div>`;
    }
  } catch (e) {
    document.getElementById('sections-list').innerHTML = `
      <div class="empty-state">
        <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1"><path d="M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>
        <p>Server is offline. Start it with <code>python run.py</code></p>
      </div>`;
  }
}

function renderSections(sections) {
  const container = document.getElementById('sections-list');

  if (!sections.length) {
    container.innerHTML = `
      <div class="empty-state">
        <p>No sections found matching your search.</p>
      </div>`;
    return;
  }

  container.innerHTML = sections.map((s) => `
    <div class="section-card" onclick="openSectionDetail(${s.number})">
      <div class="section-card-header">
        <span class="section-number">§ ${s.number}</span>
        <div class="section-badges">
          ${s.isAmended ? '<span class="badge amended">Amended</span>' : ''}
        </div>
      </div>
      <div class="section-title">${escapeHtml(s.title || 'Untitled')}</div>
      <div class="section-part">${s.partTitle ? `Part ${s.partNumber} — ${escapeHtml(s.partTitle)}` : ''}</div>
    </div>
  `).join('');
}

function filterSections(query) {
  const q = query.toLowerCase();
  const filtered = allSections.filter((s) =>
    (s.title && s.title.toLowerCase().includes(q)) ||
    String(s.number).includes(q) ||
    (s.partTitle && s.partTitle.toLowerCase().includes(q))
  );
  renderSections(filtered);
}

async function openSectionDetail(sectionNumber) {
  const listEl = document.getElementById('sections-list');
  const detailEl = document.getElementById('section-detail');
  const contentEl = document.getElementById('section-detail-content');

  listEl.style.display = 'none';
  detailEl.style.display = 'block';
  contentEl.innerHTML = '<div class="loading-spinner"><div class="spinner"></div><p>Loading section details...</p></div>';

  try {
    const [sectionRes, amendsRes, rulesRes, refsRes] = await Promise.all([
      fetch(`${API_BASE}/api/section/${sectionNumber}`),
      fetch(`${API_BASE}/api/section/${sectionNumber}/amendments`),
      fetch(`${API_BASE}/api/section/${sectionNumber}/rules`),
      fetch(`${API_BASE}/api/section/${sectionNumber}/references`),
    ]);

    const section = await sectionRes.json();
    const amendments = await amendsRes.json();
    const rules = await rulesRes.json();
    const refs = await refsRes.json();

    let html = '';

    if (section.success && section.data) {
      const s = section.data;
      html += `
        <div class="detail-section">
          <h3>
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>
            Section ${s.number}: ${escapeHtml(s.title || '')}
            ${s.isAmended ? '<span class="badge amended">Amended</span>' : ''}
          </h3>
          ${s.partTitle ? `<p style="color:var(--text-muted);font-size:0.8rem;margin-bottom:12px;">Part ${s.partNumber} — ${escapeHtml(s.partTitle)}</p>` : ''}
          
          ${s.isAmended && s.effectiveText !== s.originalText ? `
            <h4 style="color:var(--success);font-size:0.85rem;margin-bottom:6px;">Current (Effective) Text:</h4>
            <div class="effective-text detail-text">${escapeHtml(s.effectiveText || '')}</div>
            <h4 style="color:var(--error);font-size:0.85rem;margin:12px 0 6px;">Original Text:</h4>
            <div class="original-text detail-text">${escapeHtml(s.originalText || '')}</div>
          ` : `
            <div class="detail-text">${escapeHtml(s.effectiveText || s.originalText || '')}</div>
          `}

          ${s.subsections && s.subsections.length > 0 && s.subsections[0].number ? `
            <h4 style="margin-top:16px;margin-bottom:8px;font-size:0.88rem;">Subsections:</h4>
            ${s.subsections.filter(ss => ss.number).map(ss => `
              <div style="margin-left:16px;margin-bottom:8px;padding:8px 12px;background:rgba(255,255,255,0.02);border-radius:6px;border-left:2px solid var(--accent);">
                <span style="color:var(--accent-light);font-family:var(--font-mono);font-size:0.78rem;">(${ss.number})</span>
                <span class="detail-text"> ${escapeHtml(ss.text || '')}</span>
              </div>
            `).join('')}
          ` : ''}
        </div>
      `;
    }

    // Amendments
    if (amendments.success && amendments.data && amendments.data.length > 0) {
      html += `
        <div class="detail-section">
          <h3>
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M11 4H4a2 2 0 00-2 2v14a2 2 0 002 2h14a2 2 0 002-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 013 3L12 15l-4 1 1-4 9.5-9.5z"/></svg>
            Amendments (${amendments.data.length})
          </h3>
          ${amendments.data.map((am) => `
            <div class="amendment-card" style="margin-top:8px;">
              <div class="amendment-card-header">
                <span class="amendment-type ${am.type || ''}">${escapeHtml(am.type || 'amendment')}</span>
                <span class="amendment-target">${am.amendmentAct || `Amendment ${am.year || ''}`}</span>
              </div>
              <div class="amendment-desc">${escapeHtml(am.description || '')}</div>
            </div>
          `).join('')}
        </div>
      `;
    }

    // Rules
    if (rules.success && rules.data && rules.data.length > 0) {
      html += `
        <div class="detail-section">
          <h3>
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/></svg>
            Applicable Rules (${rules.data.length})
          </h3>
          ${rules.data.map((r) => `
            <div class="rule-card" style="margin-top:8px;">
              <div class="rule-card-header">
                <span class="rule-number">Rule ${escapeHtml(r.number || '')}</span>
                <span class="rule-category">${escapeHtml(r.category || '')}</span>
              </div>
              <div class="rule-title">${escapeHtml(r.title || '')}</div>
              <div class="rule-text">${escapeHtml(r.text || '')}</div>
            </div>
          `).join('')}
        </div>
      `;
    }

    // Cross-references
    if (refs.success) {
      const hasRefsTo = refs.referencesTo && refs.referencesTo.length > 0;
      const hasRefsBy = refs.referencedBy && refs.referencedBy.length > 0;

      if (hasRefsTo || hasRefsBy) {
        html += `
          <div class="detail-section">
            <h3>
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M10 13a5 5 0 007.54.54l3-3a5 5 0 00-7.07-7.07l-1.72 1.71"/><path d="M14 11a5 5 0 00-7.54-.54l-3 3a5 5 0 007.07 7.07l1.71-1.71"/></svg>
              Cross-References
            </h3>
            ${hasRefsTo ? `
              <h4 style="font-size:0.85rem;color:var(--accent-light);margin:8px 0 6px;">This section refers to:</h4>
              ${refs.referencesTo.map(r => `
                <div class="rule-section-link" onclick="openSectionDetail(${r.number})">
                  → Section ${r.number}: ${escapeHtml(r.title || '')} ${r.context ? `<span style="color:var(--text-muted);font-size:0.72rem;margin-left:6px;">(${escapeHtml(r.context)})</span>` : ''}
                </div>
              `).join('')}
            ` : ''}
            ${hasRefsBy ? `
              <h4 style="font-size:0.85rem;color:var(--accent-light);margin:12px 0 6px;">Referenced by:</h4>
              ${refs.referencedBy.map(r => `
                <div class="rule-section-link" onclick="openSectionDetail(${r.number})">
                  ← Section ${r.number}: ${escapeHtml(r.title || '')} ${r.context ? `<span style="color:var(--text-muted);font-size:0.72rem;margin-left:6px;">(${escapeHtml(r.context)})</span>` : ''}
                </div>
              `).join('')}
            ` : ''}
          </div>
        `;
      }
    }

    contentEl.innerHTML = html || '<div class="empty-state"><p>No data available for this section.</p></div>';
  } catch (e) {
    contentEl.innerHTML = `<div class="empty-state"><p>Error loading section details: ${e.message}</p></div>`;
  }
}

function closeSectionDetail() {
  document.getElementById('sections-list').style.display = '';
  document.getElementById('section-detail').style.display = 'none';
}

// ============================================
// AMENDMENTS
// ============================================
async function loadAmendments() {
  try {
    const res = await fetch(`${API_BASE}/api/amendments`);
    const data = await res.json();

    if (data.success && data.data.length > 0) {
      const container = document.getElementById('amendments-list');
      container.innerHTML = data.data.map((am) => `
        <div class="amendment-card">
          <div class="amendment-card-header">
            <span class="amendment-type ${am.type || ''}">${escapeHtml(am.type || 'amendment')}</span>
            <span class="amendment-target">Section ${am.targetSection} ${am.sectionTitle ? '— ' + escapeHtml(am.sectionTitle) : ''}</span>
          </div>
          <div class="amendment-desc">${escapeHtml(am.description || '')}</div>
          <div style="margin-top:8px;">
            <span class="meta-tag">${escapeHtml(am.relationship || '')}</span>
            <span class="meta-tag">Year: ${am.year || 'N/A'}</span>
          </div>
        </div>
      `).join('');
    }
  } catch (e) {
    document.getElementById('amendments-list').innerHTML = `
      <div class="empty-state">
        <p>Could not load amendments.</p>
      </div>`;
  }
}

// ============================================
// RULES
// ============================================
async function loadRules() {
  try {
    const res = await fetch(`${API_BASE}/api/rules`);
    const data = await res.json();

    if (data.success && data.data.length > 0) {
      const container = document.getElementById('rules-list');
      container.innerHTML = data.data.map((r) => `
        <div class="rule-card">
          <div class="rule-card-header">
            <span class="rule-number">Rule ${escapeHtml(r.number || '')}</span>
            <span class="rule-category">${escapeHtml(r.category || '')}</span>
          </div>
          <div class="rule-title">${escapeHtml(r.title || '')}</div>
          <div class="rule-text">${escapeHtml(r.text || '')}</div>
          ${r.sectionNumber ? `
            <div class="rule-section-link" onclick="switchPanel('browse'); setTimeout(() => openSectionDetail(${r.sectionNumber}), 300);">
              → Section ${r.sectionNumber}: ${escapeHtml(r.sectionTitle || '')}
            </div>
          ` : ''}
        </div>
      `).join('');
    }
  } catch (e) {
    document.getElementById('rules-list').innerHTML = `
      <div class="empty-state">
        <p>Could not load rules.</p>
      </div>`;
  }
}

// ============================================
// GRAPH VISUALIZATION
// ============================================
function populateGraphSelect(sections) {
  const select = document.getElementById('graph-section-select');
  sections.forEach((s) => {
    const opt = document.createElement('option');
    opt.value = s.number;
    opt.textContent = `§ ${s.number} — ${s.title || 'Untitled'}`;
    select.appendChild(opt);
  });
}

async function loadGraphForSection(sectionNumber) {
  if (!sectionNumber) return;

  const canvas = document.getElementById('graph-canvas');
  const infoEl = document.getElementById('graph-info');

  canvas.innerHTML = '<div class="loading-spinner"><div class="spinner"></div><p>Loading graph...</p></div>';
  infoEl.style.display = 'none';

  try {
    const [sectionRes, amendsRes, rulesRes, refsRes] = await Promise.all([
      fetch(`${API_BASE}/api/section/${sectionNumber}`).then(r => r.json()),
      fetch(`${API_BASE}/api/section/${sectionNumber}/amendments`).then(r => r.json()),
      fetch(`${API_BASE}/api/section/${sectionNumber}/rules`).then(r => r.json()),
      fetch(`${API_BASE}/api/section/${sectionNumber}/references`).then(r => r.json()),
    ]);

    const nodes = [];
    const edges = [];

    const section = sectionRes.data;
    nodes.push({
      id: `s${sectionNumber}`,
      label: `§${sectionNumber}`,
      title: section ? section.title : '',
      type: 'section',
      x: 0.5, y: 0.5, size: 50,
    });

    if (amendsRes.success && amendsRes.data) {
      amendsRes.data.forEach((am, i) => {
        const angle = (Math.PI * 2 * i) / Math.max(amendsRes.data.length, 1) - Math.PI / 2;
        nodes.push({
          id: `am${i}`, label: am.type || 'Amend', title: am.description || '',
          type: 'amendment',
          x: 0.5 + Math.cos(angle) * 0.3, y: 0.3 + Math.sin(angle) * 0.2, size: 36,
        });
        edges.push({ from: `am${i}`, to: `s${sectionNumber}`, label: am.type === 'substitution' ? 'SUBSTITUTES' : am.type === 'insertion' ? 'INSERTS' : 'AMENDS' });
      });
    }

    if (rulesRes.success && rulesRes.data) {
      rulesRes.data.forEach((r, i) => {
        const angle = (Math.PI * 2 * i) / Math.max(rulesRes.data.length, 1);
        nodes.push({
          id: `r${i}`, label: `Rule ${r.number}`, title: r.title || '',
          type: 'rule',
          x: 0.5 + Math.cos(angle) * 0.3, y: 0.7 + Math.sin(angle) * 0.15, size: 36,
        });
        edges.push({ from: `r${i}`, to: `s${sectionNumber}`, label: 'DERIVED_FROM' });
      });
    }

    if (refsRes.success) {
      if (refsRes.referencesTo) {
        refsRes.referencesTo.forEach((ref, i) => {
          nodes.push({
            id: `ref_to_${i}`, label: `§${ref.number}`, title: ref.title || '',
            type: 'ref',
            x: 0.15 + i * 0.08, y: 0.5 + (i % 2 === 0 ? -0.1 : 0.1), size: 32,
          });
          edges.push({ from: `s${sectionNumber}`, to: `ref_to_${i}`, label: 'REFERS_TO' });
        });
      }
      if (refsRes.referencedBy) {
        refsRes.referencedBy.forEach((ref, i) => {
          nodes.push({
            id: `ref_by_${i}`, label: `§${ref.number}`, title: ref.title || '',
            type: 'ref',
            x: 0.85 - i * 0.08, y: 0.5 + (i % 2 === 0 ? -0.1 : 0.1), size: 32,
          });
          edges.push({ from: `ref_by_${i}`, to: `s${sectionNumber}`, label: 'REFERS_TO' });
        });
      }
    }

    renderGraph(canvas, nodes, edges);

    infoEl.style.display = 'block';
    infoEl.innerHTML = `
      <div style="display:flex;gap:16px;flex-wrap:wrap;">
        <span style="display:flex;align-items:center;gap:6px;font-size:0.78rem;">
          <span style="width:12px;height:12px;border-radius:50%;background:linear-gradient(135deg,#6366f1,#818cf8);"></span> Section
        </span>
        <span style="display:flex;align-items:center;gap:6px;font-size:0.78rem;">
          <span style="width:12px;height:12px;border-radius:50%;background:linear-gradient(135deg,#f59e0b,#fbbf24);"></span> Amendment
        </span>
        <span style="display:flex;align-items:center;gap:6px;font-size:0.78rem;">
          <span style="width:12px;height:12px;border-radius:50%;background:linear-gradient(135deg,#10b981,#34d399);"></span> Rule
        </span>
        <span style="display:flex;align-items:center;gap:6px;font-size:0.78rem;">
          <span style="width:12px;height:12px;border-radius:50%;background:linear-gradient(135deg,#ec4899,#f472b6);"></span> Cross-Reference
        </span>
        <span style="font-size:0.78rem;color:var(--text-muted);margin-left:auto;">${nodes.length} nodes, ${edges.length} edges</span>
      </div>
    `;
  } catch (e) {
    canvas.innerHTML = `<div class="empty-state"><p>Error loading graph: ${e.message}</p></div>`;
  }
}

function renderGraph(container, nodes, edges) {
  const width = container.clientWidth || 800;
  const height = container.clientHeight || 500;

  let html = '<div class="graph-vis">';

  edges.forEach((edge) => {
    const fromNode = nodes.find(n => n.id === edge.from);
    const toNode = nodes.find(n => n.id === edge.to);
    if (!fromNode || !toNode) return;

    const x1 = fromNode.x * width;
    const y1 = fromNode.y * height;
    const x2 = toNode.x * width;
    const y2 = toNode.y * height;

    const dx = x2 - x1;
    const dy = y2 - y1;
    const length = Math.sqrt(dx * dx + dy * dy);
    const angle = Math.atan2(dy, dx) * 180 / Math.PI;

    html += `<div class="graph-edge" style="left:${x1}px;top:${y1}px;width:${length}px;transform:rotate(${angle}deg);"></div>`;

    const mx = (x1 + x2) / 2;
    const my = (y1 + y2) / 2;
    html += `<div class="graph-edge-label" style="left:${mx}px;top:${my - 10}px;">${edge.label}</div>`;
  });

  nodes.forEach((node) => {
    const x = node.x * width - node.size / 2;
    const y = node.y * height - node.size / 2;
    const typeClass = `node-${node.type}`;

    html += `
      <div class="graph-node ${typeClass}" style="left:${x}px;top:${y}px;width:${node.size}px;height:${node.size}px;font-size:${node.size > 40 ? '0.75rem' : '0.65rem'};font-weight:600;"
           title="${escapeHtml(node.title)}">
        ${node.label}
        <div class="graph-node-label">${escapeHtml(node.title.substring(0, 30))}${node.title.length > 30 ? '...' : ''}</div>
      </div>
    `;
  });

  html += '</div>';
  container.innerHTML = html;
}

async function loadFullGraphStats() {
  const infoEl = document.getElementById('graph-info');
  const canvas = document.getElementById('graph-canvas');

  try {
    const res = await fetch(`${API_BASE}/api/graph/stats`);
    const data = await res.json();

    if (data.success) {
      infoEl.style.display = 'block';

      canvas.innerHTML = `
        <div style="padding:24px;">
          <h3 style="margin-bottom:16px;font-size:1.1rem;">Knowledge Graph Overview</h3>
          <div class="stats-grid">
            <div class="stats-item">
              <div class="stats-item-value">${data.totalNodes}</div>
              <div class="stats-item-label">Total Nodes</div>
            </div>
            <div class="stats-item">
              <div class="stats-item-value">${data.totalRelationships}</div>
              <div class="stats-item-label">Total Relationships</div>
            </div>
            ${data.nodesByType.map(s => `
              <div class="stats-item">
                <div class="stats-item-value">${s.count}</div>
                <div class="stats-item-label">${s.label} Nodes</div>
              </div>
            `).join('')}
          </div>
          <h4 style="margin:20px 0 12px;font-size:0.95rem;color:var(--text-secondary);">Relationship Types</h4>
          <div class="stats-grid">
            ${data.relationshipsByType.map(r => `
              <div class="stats-item">
                <div class="stats-item-value">${r.count}</div>
                <div class="stats-item-label">${r.type}</div>
              </div>
            `).join('')}
          </div>
        </div>
      `;

      infoEl.innerHTML = '<p style="font-size:0.8rem;color:var(--text-muted);">These statistics reflect the current state of the Neo4j knowledge graph.</p>';
    }
  } catch (e) {
    canvas.innerHTML = `<div class="empty-state"><p>Could not load graph statistics.</p></div>`;
  }
}

async function loadGraphStats() {
  try {
    const res = await fetch(`${API_BASE}/api/graph/stats`);
    const data = await res.json();
    if (data.success) {
      const sectionCount = data.nodesByType.find(n => n.label === 'Section');
      const amendCount = data.nodesByType.find(n => n.label === 'Amendment');
      const ruleCount = data.nodesByType.find(n => n.label === 'Rule');

      document.getElementById('stat-sections').textContent = sectionCount ? sectionCount.count : '0';
      document.getElementById('stat-amendments').textContent = amendCount ? amendCount.count : '0';
      document.getElementById('stat-rules').textContent = ruleCount ? ruleCount.count : '0';
      document.getElementById('stat-relationships').textContent = data.totalRelationships || '0';
    }
  } catch (e) {
    // Stats will show default "—"
  }
}

// ============================================
// UTILITIES
// ============================================
function escapeHtml(text) {
  if (!text) return '';
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
}

function renderMarkdown(text) {
  if (!text) return '';

  // Basic markdown-like rendering
  let html = escapeHtml(text);

  // Headers
  html = html.replace(/^#### (.+)$/gm, '<h4>$1</h4>');
  html = html.replace(/^### (.+)$/gm, '<h3>$1</h3>');
  html = html.replace(/^## (.+)$/gm, '<h2>$1</h2>');
  html = html.replace(/^# (.+)$/gm, '<h1 style="font-size:1.15rem;">$1</h1>');

  // Bold
  html = html.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');

  // Italic
  html = html.replace(/\*(.+?)\*/g, '<em>$1</em>');

  // Code blocks
  html = html.replace(/```(\w*)\n([\s\S]*?)```/g, '<pre><code>$2</code></pre>');

  // Inline code
  html = html.replace(/`(.+?)`/g, '<code>$1</code>');

  // Bullet lists
  html = html.replace(/^- (.+)$/gm, '<li>$1</li>');
  html = html.replace(/(<li>.*<\/li>)/gs, '<ul>$1</ul>');
  html = html.replace(/<\/ul>\s*<ul>/g, '');

  // Numbered lists
  html = html.replace(/^\d+\. (.+)$/gm, '<li>$1</li>');

  // Horizontal rules
  html = html.replace(/^---$/gm, '<hr style="border:none;border-top:1px solid var(--border);margin:12px 0;">');

  // Line breaks for paragraphs
  html = html.replace(/\n\n/g, '</p><p>');
  html = html.replace(/\n/g, '<br>');

  // Wrap in paragraph
  if (!html.startsWith('<h') && !html.startsWith('<ul') && !html.startsWith('<p>')) {
    html = `<p>${html}</p>`;
  }

  return html;
}
