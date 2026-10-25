const taskForm = document.getElementById('task-form');
const input = document.getElementById('task-input');
const list = document.getElementById('task-list');
const emptyState = document.getElementById('empty-state');
const message = document.getElementById('success-message');
let tasks = [];

async function api(path, options = {}) {
  const response = await fetch(path, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  });
  if (!response.ok) {
    const body = await response.json().catch(() => ({}));
    throw new Error(body.error || `Request failed (${response.status})`);
  }
  if (response.status === 204) return null;
  return response.json();
}

function notify(text, isError = false) {
  message.textContent = text;
  message.classList.toggle('error', isError);
}

function render() {
  list.replaceChildren();
  document.getElementById('total-count').textContent = tasks.length;
  const completed = tasks.filter(task => task.completed).length;
  document.getElementById('done-count').textContent = completed;
  document.getElementById('pending-count').textContent = `${tasks.length - completed} remaining`;
  emptyState.hidden = tasks.length !== 0;

  for (const task of tasks) {
    const li = document.createElement('li');
    li.className = task.completed ? 'completed' : '';
    li.dataset.taskId = String(task.id);

    const toggle = document.createElement('button');
    toggle.type = 'button';
    toggle.className = 'toggle-btn';
    toggle.textContent = task.completed ? '✓' : '';
    toggle.setAttribute('aria-label', `Toggle ${task.title}`);
    toggle.addEventListener('click', () => changeTask(task.id));

    const title = document.createElement('span');
    title.className = 'task-title';
    title.textContent = task.title; // textContent avoids HTML injection.

    const remove = document.createElement('button');
    remove.type = 'button';
    remove.className = 'delete-btn';
    remove.textContent = '×';
    remove.setAttribute('aria-label', `Delete ${task.title}`);
    remove.addEventListener('click', () => removeTask(task.id));

    li.append(toggle, title, remove);
    list.appendChild(li);
  }
}

async function refresh() {
  try {
    tasks = await api('/api/tasks');
    render();
  } catch (error) {
    notify(`Could not load tasks: ${error.message}`, true);
  }
}

async function changeTask(id) {
  try {
    await api(`/api/tasks/${id}`, { method: 'PATCH' });
    await refresh();
    notify('Task updated.');
  } catch (error) { notify(error.message, true); }
}

async function removeTask(id) {
  try {
    await api(`/api/tasks/${id}`, { method: 'DELETE' });
    await refresh();
    notify('Task deleted.');
  } catch (error) { notify(error.message, true); }
}

taskForm.addEventListener('submit', async event => {
  event.preventDefault();
  const title = input.value.trim();
  if (!title) return;
  try {
    await api('/api/tasks', { method: 'POST', body: JSON.stringify({ title }) });
    input.value = '';
    await refresh();
    notify('Task added successfully!');
    input.focus();
  } catch (error) { notify(error.message, true); }
});

refresh();
