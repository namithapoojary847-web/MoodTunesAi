/**
 * MoodTunes - Authentication & User State Management + Theme Switcher
 */

console.log("AUTH JS LOADED");

document.addEventListener('DOMContentLoaded', () => {
    initTheme();
    checkCurrentUser();

    const authModal = document.getElementById('authModalOverlay');
    const btnOpenAuth = document.getElementById('btnOpenAuth');
    const btnCloseAuth = document.getElementById('btnCloseAuthModal');
    const tabLogin = document.getElementById('tabLogin');
    const tabRegister = document.getElementById('tabRegister');
    const formLogin = document.getElementById('formLogin');
    const formRegister = document.getElementById('formRegister');
    const btnLogout = document.getElementById('btnLogout');
    const btnThemeToggle = document.getElementById('btnThemeToggle');

    console.log("Login button:", btnOpenAuth);
console.log("Logout button:", btnLogout);
console.log("Modal:", authModal);

    if (btnThemeToggle) {
        btnThemeToggle.addEventListener('click', toggleTheme);
    }

    if (btnOpenAuth) btnOpenAuth.addEventListener('click', () => openAuthModal('login'));
    if (btnCloseAuth) btnCloseAuth.addEventListener('click', closeAuthModal);

    

    if (tabLogin && tabRegister) {
        tabLogin.addEventListener('click', () => switchAuthTab('login'));
        tabRegister.addEventListener('click', () => switchAuthTab('register'));
    }

    if (formLogin) {
        formLogin.addEventListener('submit', handleLogin);
    }
    if (formRegister) {
        formRegister.addEventListener('submit', handleRegister);
    }
    if (btnLogout) {
        btnLogout.addEventListener('click', handleLogout);
    }

    // Mood-button clicks and recommendation rendering are handled by
    // script.js -> player.js (loadRecommendationsForMood/renderTrackList).
    // Do not duplicate that logic here — a second handler on the same
    // buttons caused two different card layouts to race and overwrite
    // each other's DOM, which looked like "cards randomly resizing".
});


function initTheme() {
    const savedTheme = localStorage.getItem('moodtunes-theme') || 'dark';
    document.documentElement.setAttribute('data-theme', savedTheme);
    updateThemeIcon(savedTheme);
}

function toggleTheme() {
    const currentTheme = document.documentElement.getAttribute('data-theme') || 'dark';
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
    
    document.documentElement.setAttribute('data-theme', newTheme);
    localStorage.setItem('moodtunes-theme', newTheme);
    updateThemeIcon(newTheme);
}

function updateThemeIcon(theme) {
    const btnThemeToggle = document.getElementById('btnThemeToggle');
    if (btnThemeToggle) {
        btnThemeToggle.textContent = theme === 'dark' ? '☀️' : '🌙';
        btnThemeToggle.title = theme === 'dark' ? 'Switch to Light Mode' : 'Switch to Dark Mode';
    }
}

async function checkCurrentUser() {
    try {
        const response = await fetch('/api/user');
        const data = await response.json();

        const btnOpenAuth = document.getElementById('btnOpenAuth');
        const btnLogout = document.getElementById('btnLogout');
        const userNameDisplay = document.getElementById('sidebarUserName');

        if (data.logged_in) {
            if (btnOpenAuth) btnOpenAuth.style.display = 'none';
            if (btnLogout) btnLogout.style.display = 'flex';
            if (userNameDisplay) userNameDisplay.textContent = data.user.username;
        } else {
            if (btnOpenAuth) btnOpenAuth.style.display = 'flex';
            if (btnLogout) btnLogout.style.display = 'none';
            if (userNameDisplay) userNameDisplay.textContent = 'Guest User';
        }
    } catch (err) {
        console.error("Error checking user status:", err);
    }
}
function openAuthModal(tab = 'login') {

    console.log("OPEN AUTH CALLED");

    const modal = document.getElementById('authModalOverlay');

    console.log(modal);

    if (modal) {
        modal.classList.add('active');
        switchAuthTab(tab);
    }
}

function closeAuthModal() {
    const modal = document.getElementById('authModalOverlay');
    if (modal) modal.classList.remove('active');
}

function switchAuthTab(tab) {
    const tabLogin = document.getElementById('tabLogin');
    const tabRegister = document.getElementById('tabRegister');
    const formLogin = document.getElementById('formLogin');
    const formRegister = document.getElementById('formRegister');

    if (tab === 'login') {
        tabLogin.classList.add('active');
        tabRegister.classList.remove('active');
        formLogin.style.display = 'block';
        formRegister.style.display = 'none';
    } else {
        tabRegister.classList.add('active');
        tabLogin.classList.remove('active');
        formRegister.style.display = 'block';
        formLogin.style.display = 'none';
    }
}

async function handleLogin(e) {
    e.preventDefault();
    const identifier = document.getElementById('loginIdentifier').value;
    const password = document.getElementById('loginPassword').value;

    try {
        const response = await fetch('/api/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ identifier, password })
        });
        const data = await response.json();

        if (data.success) {
            alert("Welcome back, " + data.user.username + "!");
            closeAuthModal();
            checkCurrentUser();
            location.reload();
        } else {
            alert(data.error || "Login failed.");
        }
    } catch (err) {
        console.error("Login error:", err);
    }
}

async function handleRegister(e) {
    e.preventDefault();
    const username = document.getElementById('regUsername').value;
    const email = document.getElementById('regEmail').value;
    const password = document.getElementById('regPassword').value;

    try {
        const response = await fetch('/api/register', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, email, password })
        });
        const data = await response.json();

        if (data.success) {
            alert("Account created successfully! Welcome, " + data.user.username);
            closeAuthModal();
            checkCurrentUser();
            location.reload();
        } else {
            alert(data.error || "Registration failed.");
        }
    } catch (err) {
        console.error("Register error:", err);
    }
}

async function handleLogout() {
    try {
        await fetch('/api/logout', { method: 'POST' });
        alert("Logged out successfully.");
        checkCurrentUser();
        location.reload();
    } catch (err) {
        console.error("Logout error:", err);
    }
}

window.openAuthModal = openAuthModal;