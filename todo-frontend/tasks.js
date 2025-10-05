if (!getToken()) window.location.href = 'index.html';

const tbody = document.getElementById('tasks-tbody');
const form = document.getElementById('task-form');
const resetBtn = document.getElementById('reset-btn');
const formMsg = document.getElementById('form-msg');
const listMsg = document.getElementById('list-msg');
const logoutBtn = document.getElementById('logout-btn');

const limitEl = document.getElementById('limit');
const offsetEl = document.getElementById('offset');
const reloadBtn = document.getElementById('reload');
const fp = document.getElementById('filter-priority');
const fd = document.getElementById('filter-done');

logoutBtn.addEventListener('click', () => { clearToken(); window.location.href = 'index.html'; });

function readForm() {
  return {
    id: document.getElementById('task-id').value || null,
    title: document.getElementById('task-title').value.trim(),
    description: document.getElementById('task-desc').value.trim(),
    priority: Number(document.getElementById('task-priority').value || 0),
    is_done: document.getElementById('task-done').checked
  };
}

function fillForm(task) {
  const p = task.payload || {};
  document.getElementById('task-id').value = task.id || '';
  document.getElementById('task-title').value = p.title || '';
  document.getElementById('task-desc').value = p.description || '';
  document.getElementById('task-priority').value = p.priority ?? 1;
  document.getElementById('task-done').checked = !!p.is_done;
}

function resetForm() {
  document.getElementById('task-id').value = '';
  document.getElementById('task-title').value = '';
  document.getElementById('task-desc').value = '';
  document.getElementById('task-priority').value = 1;
  document.getElementById('task-done').checked = false;
  formMsg.textContent = '';
}

function escapeHtml(str){
  return String(str ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
}

function badge(v){ return v ? 'success' : 'secondary'; }

async function loadTasks() {
  listMsg.textContent = '';
  tbody.innerHTML = '<tr><td colspan="5">Loading...</td></tr>';
  const params = new URLSearchParams();
  const limit = Number(limitEl.value || 20);
  const offset = Number(offsetEl.value || 0);
  params.set('limit', String(limit));
  params.set('offset', String(offset));
  if (fp.value !== '') params.set('priority', fp.value);
  if (fd.value !== '') params.set('is_done', fd.value);

  try {
    const list = await apiFetch(`/tasks/?${params.toString()}`, { method: 'GET' });
    tbody.innerHTML = '';
    list.forEach(addRow);
  } catch (e) {
    tbody.innerHTML = '';
    listMsg.textContent = e.message || 'Failed to load tasks';
  }
}

function addRow(task) {
  const p = task.payload || {};
  const tr = document.createElement('tr');
  tr.innerHTML = `
    <td>${escapeHtml(p.title)}</td>
    <td>${escapeHtml(p.priority)}</td>
    <td><span class="badge text-bg-${badge(p.is_done)}">${p.is_done ? 'Yes' : 'No'}</span></td>
    <td>${escapeHtml(p.description)}</td>
    <td>
      <button class="btn btn-sm btn-outline-primary me-2">Edit</button>
      <button class="btn btn-sm btn-outline-danger">Delete</button>
    </td>
  `;
  const [editBtn, delBtn] = tr.querySelectorAll('button');
  editBtn.addEventListener('click', () => fillForm(task));
  delBtn.addEventListener('click', async () => {
    if (!confirm('Delete this task?')) return;
    try {
      await apiFetch(`/tasks/${task.id}`, { method: 'DELETE' });
      await loadTasks();
    } catch (e) {
      listMsg.textContent = e.message || 'Delete failed';
    }
  });
  tbody.appendChild(tr);
}

form.addEventListener('submit', async (e) => {
  e.preventDefault();
  const { id, title, description, priority, is_done } = readForm();
  if (!title) {
    formMsg.textContent = 'Title is required';
    return;
  }
  formMsg.textContent = '';
  try {
    if (id) {
      const body = {};
      // Only send changed fields for PATCH behavior; for simplicity sending all non-empty fields is acceptable
      body.title = title;
      body.description = description;
      body.priority = priority;
      body.is_done = is_done;
      await apiFetch(`/tasks/${id}`, { method: 'PATCH', body: JSON.stringify(body) });
    } else {
      await apiFetch('/tasks/', { method: 'POST', body: JSON.stringify({ title, description, priority, is_done }) });
    }
    resetForm();
    await loadTasks();
  } catch (e) {
    formMsg.textContent = e.message || 'Save failed';
  }
});

reloadBtn.addEventListener('click', () => loadTasks());
fp.addEventListener('change', () => loadTasks());
fd.addEventListener('change', () => loadTasks());

// init
resetForm();
loadTasks();
