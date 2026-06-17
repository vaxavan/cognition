// auth.js
const API_BASE = 'http://localhost:8000';

// Если уже есть токен — на главную
const token = localStorage.getItem('token');
if (token) {
    window.location.href = '/';
}

// Состояние
let currentEmail = '';
let currentPassword = '';

// DOM элементы
const stepCredentials = document.getElementById('step-credentials');
const stepCode = document.getElementById('step-code');
const emailInput = document.getElementById('email-input');
const passwordInput = document.getElementById('password-input');
const codeInput = document.getElementById('code-input');
const emailDisplay = document.getElementById('email-display');
const errorMessage = document.getElementById('error-message');

const continueBtn = document.getElementById('continue-btn');
const verifyBtn = document.getElementById('verify-btn');
const backBtn = document.getElementById('back-btn');

// Показать ошибку
function showError(text) {
    errorMessage.textContent = text;
    errorMessage.classList.remove('hidden');
    setTimeout(() => errorMessage.classList.add('hidden'), 3000);
}

// Шаг 1: Проверка почты и пароля, отправка кода
continueBtn.addEventListener('click', async () => {
    const email = emailInput.value.trim();
    const password = passwordInput.value.trim();
    
    if (!email || !email.includes('@')) {
        showError('Введите корректный email');
        return;
    }
    
    if (password.length < 6) {
        showError('Пароль должен быть не менее 6 символов');
        return;
    }

    try {
        // Отправляем код на почту
        const res = await fetch(`${API_BASE}/auth/send-code`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password })
        });

        const data = await res.json();
        
        if (!res.ok) {
            throw new Error(data.detail || 'Ошибка отправки кода');
        }

        currentEmail = email;
        currentPassword = password;
        emailDisplay.textContent = email;
        
        // Переход ко второму шагу
        stepCredentials.classList.add('hidden');
        stepCode.classList.remove('hidden');
        codeInput.focus();
        
    } catch (e) {
        showError(e.message);
    }
});

// Шаг 2: Проверка кода и авторизация
verifyBtn.addEventListener('click', async () => {
    const code = codeInput.value.trim();
    
    if (code.length !== 6) {
        showError('Введите 6-значный код');
        return;
    }

    try {
        const res = await fetch(`${API_BASE}/auth/verify`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 
                email: currentEmail, 
                password: currentPassword,
                code 
            })
        });

        const data = await res.json();
        
        if (!res.ok) {
            throw new Error(data.detail || 'Неверный код');
        }

        // Успешная авторизация
        localStorage.setItem('token', data.access_token);
        window.location.href = '/';
        
    } catch (e) {
        showError(e.message);
    }
});

// Возврат к вводу почты и пароля
backBtn.addEventListener('click', () => {
    stepCode.classList.add('hidden');
    stepCredentials.classList.remove('hidden');
    codeInput.value = '';
});

// Автофокус и форматирование кода
codeInput.addEventListener('input', (e) => {
    e.target.value = e.target.value.replace(/\D/g, '').slice(0, 6);
});

// Enter в полях
emailInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') continueBtn.click();
});

passwordInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') continueBtn.click();
});

codeInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') verifyBtn.click();
});