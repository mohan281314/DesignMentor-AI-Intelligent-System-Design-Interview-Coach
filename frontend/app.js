/* ── DesignMentor AI — Frontend App ─────────────────────────────── */
const API = '';   // same origin

/* ── Utilities ───────────────────────────────────────────────────── */
const $ = id => document.getElementById(id);
const md = text => marked.parse(text || '');

function showToast(msg, isError = false) {
  const t = $('toast');
  t.textContent = msg;
  t.className = 'toast' + (isError ? ' error' : '');
  clearTimeout(t._timer);
  t._timer = setTimeout(() => t.classList.add('hidden'), 3500);
}

function setLoading(btn, loading, label = 'Generate') {
  btn.disabled = loading;
  btn.innerHTML = loading
    ? `<span class="spinner"></span> Working…`
    : label;
}

async function apiFetch(path, body) {
  const res = await fetch(API + path, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body)
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || `HTTP ${res.status}`);
  }
  return res.json();
}

async function apiDelete(path) {
  const res = await fetch(API + path, { method: 'DELETE' });
  return res.ok;
}

/* ── Tab Navigation ──────────────────────────────────────────────── */
document.querySelectorAll('.tab-btn').forEach(btn => {
  btn.addEventListener('click', () => {
    document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
    document.querySelectorAll('.tab-panel').forEach(p => p.classList.add('hidden'));
    btn.classList.add('active');
    $('tab-' + btn.dataset.tab).classList.remove('hidden');
  });
});

/* ── Design Generator ────────────────────────────────────────────── */
$('design-btn').addEventListener('click', async () => {
  const topic = $('design-topic').value.trim();
  if (!topic) return showToast('Enter a topic first', true);
  const btn = $('design-btn');
  const out = $('design-output');
  setLoading(btn, true, 'Generate Design');
  out.classList.add('hidden');
  try {
    const data = await apiFetch('/design', { topic });
    out.innerHTML = md(data.design);
    out.dataset.sessionId = data.session_id;
    out.classList.remove('hidden');
    showToast('Design generated!');
  } catch (e) {
    showToast('Error: ' + e.message, true);
  } finally {
    setLoading(btn, false, 'Generate Design');
  }
});

$('design-topic').addEventListener('keydown', e => {
  if (e.key === 'Enter') $('design-btn').click();
});

/* ── Interview ───────────────────────────────────────────────────── */
let interviewSession = null;
let interviewTurn = 0;
const MAX_TURNS = 5;

function showInterviewScreen(screen) {
  ['start', 'active', 'complete'].forEach(s =>
    $(`interview-${s}-screen`).classList.add('hidden')
  );
  $(`interview-${screen}-screen`).classList.remove('hidden');
}

async function startInterview() {
  const topic = $('interview-topic').value.trim();
  if (!topic) return showToast('Enter a topic first', true);
  const btn = $('interview-start-btn');
  setLoading(btn, true, 'Start Interview');
  try {
    const data = await apiFetch('/interview/start', { topic });
    interviewSession = data.session_id;
    interviewTurn = 1;
    $('interview-topic-label').textContent = '📌 ' + data.topic;
    $('interview-progress').textContent = `Question ${interviewTurn} / ${MAX_TURNS}`;
    $('interview-question-box').innerHTML = md(data.first_question);
    $('interview-answer').value = '';
    $('interview-eval-box').classList.add('hidden');
    showInterviewScreen('active');
    showToast('Interview started!');
  } catch (e) {
    showToast('Error: ' + e.message, true);
  } finally {
    setLoading(btn, false, 'Start Interview');
  }
}

async function submitAnswer() {
  const answer = $('interview-answer').value.trim();
  if (!answer) return showToast('Write your answer first', true);
  const btn = $('interview-submit-btn');
  setLoading(btn, true, 'Submit Answer');
  const evalBox = $('interview-eval-box');
  evalBox.classList.add('hidden');
  try {
    const data = await apiFetch('/interview/answer', {
      session_id: interviewSession,
      answer
    });
    evalBox.innerHTML = md(data.evaluation);
    evalBox.classList.remove('hidden');
    interviewTurn++;
    if (data.is_complete) {
      showInterviewScreen('complete');
    } else {
      $('interview-progress').textContent = `Question ${interviewTurn} / ${MAX_TURNS}`;
      $('interview-question-box').innerHTML = md(data.next_question);
      $('interview-answer').value = '';
      evalBox.scrollIntoView({ behavior: 'smooth' });
    }
  } catch (e) {
    showToast('Error: ' + e.message, true);
  } finally {
    setLoading(btn, false, 'Submit Answer');
  }
}

function resetInterview() {
  interviewSession = null;
  interviewTurn = 0;
  $('interview-topic').value = '';
  showInterviewScreen('start');
}

$('interview-start-btn').addEventListener('click', startInterview);
$('interview-submit-btn').addEventListener('click', submitAnswer);
$('interview-reset-btn').addEventListener('click', resetInterview);
$('interview-new-btn').addEventListener('click', resetInterview);
$('interview-topic').addEventListener('keydown', e => {
  if (e.key === 'Enter') startInterview();
});

/* ── Evaluate ────────────────────────────────────────────────────── */
$('eval-btn').addEventListener('click', async () => {
  const question = $('eval-question').value.trim();
  const answer   = $('eval-answer').value.trim();
  const reference = $('eval-reference').value.trim();
  if (!question || !answer) return showToast('Question and answer are required', true);
  const btn = $('eval-btn');
  const out = $('eval-output');
  setLoading(btn, true, 'Evaluate Answer');
  out.classList.add('hidden');
  try {
    const payload = { question, user_answer: answer };
    if (reference) payload.reference = reference;
    const data = await apiFetch('/evaluate', payload);
    out.innerHTML = md(data.evaluation);
    out.classList.remove('hidden');
    showToast('Evaluation complete!');
  } catch (e) {
    showToast('Error: ' + e.message, true);
  } finally {
    setLoading(btn, false, 'Evaluate Answer');
  }
});

/* ── Diagram ─────────────────────────────────────────────────────── */
mermaid.initialize({ startOnLoad: false, theme: 'dark' });

$('diagram-btn').addEventListener('click', async () => {
  const topic   = $('diagram-topic').value.trim();
  const summary = $('diagram-summary').value.trim();
  if (!topic || !summary) return showToast('Topic and summary are required', true);
  const btn = $('diagram-btn');
  const out = $('diagram-output');
  setLoading(btn, true, 'Generate Diagram');
  out.classList.add('hidden');
  try {
    const data = await apiFetch('/diagram', { topic, design_summary: summary });

    // Render Mermaid
    const renderBox = $('diagram-render');
    renderBox.innerHTML = '';
    const { svg } = await mermaid.render('mermaid-svg', data.mermaid_code);
    renderBox.innerHTML = svg;

    // Explanation
    $('diagram-explanation').innerHTML = md(data.explanation);

    // Suggestions
    const suggBox = $('diagram-suggestions');
    if (data.suggestions && data.suggestions.length) {
      suggBox.innerHTML = `<h4>💡 Suggestions</h4><ul>${data.suggestions.map(s => `<li>${s}</li>`).join('')}</ul>`;
      suggBox.classList.remove('hidden');
    } else {
      suggBox.classList.add('hidden');
    }

    out.classList.remove('hidden');
    showToast('Diagram generated!');
  } catch (e) {
    // Fallback: show raw mermaid code if render fails
    $('diagram-render').innerHTML = `<pre><code>${e.message}</code></pre>`;
    out.classList.remove('hidden');
    showToast('Render error — showing raw code', true);
  } finally {
    setLoading(btn, false, 'Generate Diagram');
  }
});

/* ── Feedback ────────────────────────────────────────────────────── */
$('feedback-btn').addEventListener('click', async () => {
  const topic     = $('feedback-topic').value.trim();
  const sessionId = $('feedback-session').value.trim();
  if (!topic) return showToast('Enter a topic first', true);
  const btn = $('feedback-btn');
  const out = $('feedback-output');
  setLoading(btn, true, 'Generate Report');
  out.classList.add('hidden');
  try {
    const payload = { topic };
    if (sessionId) payload.session_id = sessionId;
    const data = await apiFetch('/feedback', payload);
    out.innerHTML = md(data.report);
    out.classList.remove('hidden');
    showToast('Report generated!');
  } catch (e) {
    showToast('Error: ' + e.message, true);
  } finally {
    setLoading(btn, false, 'Generate Report');
  }
});

/* ── Chat ────────────────────────────────────────────────────────── */
let chatSessionId = null;

function appendChatMessage(role, content) {
  const box = $('chat-messages');
  const msg = document.createElement('div');
  msg.className = `chat-msg ${role}`;
  const label = document.createElement('div');
  label.className = 'chat-label';
  label.textContent = role === 'user' ? 'You' : 'DesignMentor AI';
  const bubble = document.createElement('div');
  bubble.className = 'chat-bubble';
  bubble.innerHTML = role === 'assistant' ? md(content) : content;
  msg.appendChild(label);
  msg.appendChild(bubble);
  box.appendChild(msg);
  box.scrollTop = box.scrollHeight;
}

function appendTypingIndicator() {
  const box = $('chat-messages');
  const el = document.createElement('div');
  el.className = 'chat-msg assistant';
  el.id = 'typing-indicator';
  el.innerHTML = '<div class="chat-label">DesignMentor AI</div><div class="chat-bubble"><span class="spinner"></span> Thinking…</div>';
  box.appendChild(el);
  box.scrollTop = box.scrollHeight;
}

function removeTypingIndicator() {
  const el = $('typing-indicator');
  if (el) el.remove();
}

async function sendChat() {
  const input = $('chat-input');
  const message = input.value.trim();
  if (!message) return;
  const btn = $('chat-send-btn');
  btn.disabled = true;
  input.value = '';
  appendChatMessage('user', message);
  appendTypingIndicator();
  try {
    const payload = { message };
    if (chatSessionId) payload.session_id = chatSessionId;
    const data = await apiFetch('/chat', payload);
    chatSessionId = data.session_id;
    removeTypingIndicator();
    appendChatMessage('assistant', data.reply);
  } catch (e) {
    removeTypingIndicator();
    showToast('Error: ' + e.message, true);
  } finally {
    btn.disabled = false;
    input.focus();
  }
}

$('chat-send-btn').addEventListener('click', sendChat);
$('chat-input').addEventListener('keydown', e => {
  if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendChat(); }
});

$('chat-clear-btn').addEventListener('click', async () => {
  if (chatSessionId) {
    await apiDelete(`/session/${chatSessionId}`).catch(() => {});
    chatSessionId = null;
  }
  $('chat-messages').innerHTML = '';
  showToast('Conversation cleared');
});

// Welcome message
appendChatMessage('assistant',
  "Hello! I'm **DesignMentor AI**, your system design interview coach.\n\n" +
  "Ask me anything — trade-offs, architectures, interview tips, or try:\n" +
  "- *\"How do I design a URL shortener?\"*\n" +
  "- *\"Explain the CAP theorem\"*\n" +
  "- *\"What are common mistakes in system design interviews?\"*"
);
