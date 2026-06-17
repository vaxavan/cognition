const API_BASE = 'http://localhost:8000';
let chatId = null;
let uploadedFiles = []; // { id, name, checked }

// Проверка авторизации
const token = localStorage.getItem('token');
if (!token) {
    window.location.href = '/auth.html';
}

// Функция для запросов с токеном
async function fetchWithAuth(url, options = {}) {
    return fetch(url, {
        ...options,
        headers: {
            ...options.headers,
            'Authorization': `Bearer ${token}`
        }
    });
}

// Кнопка выхода
document.getElementById('logout-btn').addEventListener('click', () => {
    localStorage.removeItem('token');
    window.location.href = '/auth.html';
});

// Отображение email пользователя
try {
    const payload = JSON.parse(atob(token.split('.')[1]));
    document.getElementById('user-email').textContent = payload.sub;
} catch (e) {
    console.error('Ошибка парсинга токена:', e);
}

// ========== САЙДБАР С ФАЙЛАМИ ==========
const filesSidebar = document.getElementById('files-sidebar');
const toggleSidebarBtn = document.getElementById('toggle-sidebar-btn');
const showSidebarBtn = document.getElementById('show-sidebar-btn');
const filesList = document.getElementById('files-list');
const fileInput = document.getElementById('file-input');
const uploadFileBtn = document.getElementById('upload-file-btn');

// Переключение сайдбара
toggleSidebarBtn.addEventListener('click', () => {
    filesSidebar.classList.add('hidden');
    showSidebarBtn.classList.remove('hidden');
});

showSidebarBtn.addEventListener('click', () => {
    filesSidebar.classList.remove('hidden');
    showSidebarBtn.classList.add('hidden');
});

// Загрузка файлов
uploadFileBtn.addEventListener('click', () => fileInput.click());

async function uploadFileToServer(file) {
    // 1. Запросить presigned URL
    const res1 = await fetchWithAuth(`${API_BASE}/api/v1/files/request-upload`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
            filename: file.name,
            project_id: 'default'  // или chat_id, если есть
        })
    });
    
    if (!res1.ok) {
        const err = await res1.json();
        throw new Error(err.detail || 'Ошибка запроса upload URL');
    }
    
    const data1 = await res1.json();
    const file_id = data1.file_id;
    const upload_url = data1.upload_url;
    
    // 2. Загрузить файл напрямую в MinIO
    const res2 = await fetch(upload_url, {
        method: 'PUT',
        body: file,
        headers: { 'Content-Type': file.type }
    });
    
    if (!res2.ok) {
        throw new Error('Ошибка загрузки файла в хранилище');
    }
    
    // 3. Подтвердить загрузку
    await fetchWithAuth(`${API_BASE}/api/v1/files/confirm-upload`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
            filename: file.name,
            project_id: 'default',
            file_id: file_id 
        })
    });
    
    return file_id;
}

fileInput.addEventListener('change', async (e) => {
    const files = Array.from(e.target.files);
    
    for (const file of files) {
        try {
            // Загружаем файл на сервер и получаем реальный ID
            const fileId = await uploadFileToServer(file);
            
            const newFile = {
                id: fileId,
                name: file.name,
                checked: true
            };
            uploadedFiles.push(newFile);
            addFileToList(newFile);
        } catch (error) {
            console.error('Ошибка загрузки:', error);
            alert(`Не удалось загрузить файл ${file.name}`);
        }
    }
    
    fileInput.value = '';
});


function addFileToList(file) {
    // Используем data-атрибут вместо класса
    const emptyMsg = filesList.querySelector('[data-empty-msg]');
    if (emptyMsg) emptyMsg.remove();
    
    const fileEl = document.createElement('div');
    fileEl.className = 'flex items-center gap-3 p-2 bg-gray-800/50 rounded-lg hover:bg-gray-800 transition';
    fileEl.dataset.fileId = file.id;
    
    // Чекбокс
    const checkbox = document.createElement('input');
    checkbox.type = 'checkbox';
    checkbox.className = 'file-checkbox w-4 h-4 accent-blue-600';
    checkbox.checked = file.checked;
    checkbox.addEventListener('change', () => { file.checked = checkbox.checked; });
    
    // Имя файла
    const span = document.createElement('span');
    span.className = 'text-sm text-gray-300 truncate flex-1';
    span.title = file.name;
    span.textContent = '📄 ' + file.name;
    
    // Кнопка удаления - ИСПРАВЛЕНО: используем text-gray-400
    const removeBtn = document.createElement('button');
    removeBtn.className = 'remove-file-btn text-gray-400 hover:text-red-400 p-1 transition';
    removeBtn.title = 'Удалить файл';
    removeBtn.innerHTML = `
        <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <line x1="18" y1="6" x2="6" y2="18"></line>
            <line x1="6" y1="6" x2="18" y2="18"></line>
        </svg>`;
    removeBtn.addEventListener('click', async () => {
        if (!confirm(`Удалить файл "${file.name}"?`)) return;
        try {
            const res = await fetchWithAuth(`${API_BASE}/api/v1/files/${file.id}`, { method: 'DELETE' });
            if (!res.ok) throw new Error('Ошибка удаления');
        } catch (e) { 
            console.error('Ошибка удаления:', e);
            alert(`Не удалось удалить файл ${file.name}`);
            return;
        }
        uploadedFiles = uploadedFiles.filter(f => f.id !== file.id);
        fileEl.remove();
        if (filesList.children.length === 0) {
            filesList.innerHTML = '<div class="text-gray-500 text-sm text-center py-4" data-empty-msg>Нет загруженных файлов</div>';
        }
    });
    
    fileEl.appendChild(checkbox);
    fileEl.appendChild(span);
    fileEl.appendChild(removeBtn);
    filesList.appendChild(fileEl);
}

// ========== ЧАТ ==========
const messagesContainer = document.querySelector('#chat-messages .max-w-3xl');
const messageInput = document.getElementById('message-input');
const sendBtn = document.getElementById('send-btn');
const modelSelector = document.getElementById('model-selector');

marked.setOptions({
    highlight: (code, lang) => {
        if (lang && hljs.getLanguage(lang)) return hljs.highlight(code, { language: lang }).value;
        return hljs.highlightAuto(code).value;
    },
    breaks: true
});

function addMessage(role, content, isStreaming = false) {
    const div = document.createElement('div');
    div.className = `flex ${role === 'user' ? 'justify-end' : 'justify-start'}`;
    const bubble = document.createElement('div');
    bubble.className = `max-w-[80%] px-4 py-3 rounded-2xl ${
        role === 'user' ? 'message-user' : 'message-assistant'
    }`;
    if (role === 'assistant') {
        bubble.innerHTML = marked.parse(content);
        if (isStreaming) bubble.classList.add('streaming-cursor');
        bubble.querySelectorAll('pre code').forEach(block => hljs.highlightElement(block));
    } else {
        bubble.textContent = content;
    }
    div.appendChild(bubble);
    messagesContainer.appendChild(div);
    
    const mainElement = document.getElementById('chat-messages');
    mainElement.scrollTop = mainElement.scrollHeight;
    
    return bubble;
}

async function ensureChat() {
    if (chatId) return chatId;
    const res = await fetchWithAuth(`${API_BASE}/api/v1/chats`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name: 'Чат ' + new Date().toLocaleString() })
    });
    const chat = await res.json();
    chatId = chat.id;
    return chatId;
}

async function sendMessage() {
    const content = messageInput.value.trim();
    if (!content) return;
    messageInput.value = '';
    addMessage('user', content);

    const id = await ensureChat();
    const selectedModel = modelSelector.value;
    const checkedFiles = uploadedFiles.filter(f => f.checked);
    
    const assistantBubble = addMessage('assistant', '', true);
    let fullResponse = '';

    try {
        const response = await fetchWithAuth(`${API_BASE}/api/v1/chats/${id}/messages`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 
                content,
                model: selectedModel,
                files: checkedFiles.map(f => f.id)
            })
        });
        
        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        
        while (true) {
            const { done, value } = await reader.read();
            if (done) break;
            
            const chunk = decoder.decode(value);
            const lines = chunk.split('\n');
            
            for (const line of lines) {
                if (line.startsWith('data: ')) {
                    const data = line.slice(6);
                    if (data === '[DONE]') continue;
                    
                    try {
                        const parsed = JSON.parse(data);
                        if (parsed.content) {
                            fullResponse += parsed.content;
                            assistantBubble.innerHTML = marked.parse(fullResponse);
                            assistantBubble.querySelectorAll('pre code').forEach(block => hljs.highlightElement(block));
                            const mainElement = document.getElementById('chat-messages');
                            mainElement.scrollTop = mainElement.scrollHeight;
                        }
                    } catch (e) {}
                }
            }
        }
        assistantBubble.classList.remove('streaming-cursor');
    } catch (e) {
        assistantBubble.textContent = 'Ошибка соединения';
        assistantBubble.classList.remove('streaming-cursor');
    }
}

sendBtn.addEventListener('click', sendMessage);
messageInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
    }
});

messageInput.addEventListener('input', function() {
    this.style.height = 'auto';
    this.style.height = Math.min(this.scrollHeight, 150) + 'px';
});
async function loadFiles() {
    try {
        const response = await fetchWithAuth(`${API_BASE}/api/v1/files/list`);
        if (response.ok) {
            const data = await response.json();
            data.files.forEach(file => {
                uploadedFiles.push({
                    id: file.file_id,
                    name: file.filename,
                    checked: true
                });
                addFileToList({ id: file.file_id, name: file.filename, checked: true });
            });
        }
    } catch (e) {
        console.log('Файлы не загружены:', e);
    }
}

document.addEventListener('DOMContentLoaded', () => {
    console.log('DOM загружен, вызываю loadFiles');
    console.log('filesList существует:', !!document.getElementById('files-list'));
    loadFiles();
});