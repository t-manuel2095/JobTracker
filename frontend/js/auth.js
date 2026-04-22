/**
 * AUTH.js - Handles authentication and authorization
 */

class AuthManager {
    constructor() {
        this.checkAuth();
    }

    checkAuth() {
        const token = localStorage.getItem('auth_token');
        if (token) {
            this.showMainContent();
        } else {
            this.showAuthForms();
        }
    }

    async register(username, email, password) {
        try {
            await api.register(username, email, password);
            // Auto-login after registration
            await this.login(username, password);
        } catch (error) {
            this.showAlert('Registration failed', 'error');
        }
    }

    async login(username, password) {
        try {
            const response = await api.login(username, password);
            api.setToken(response.access);
            this.showMainContent();
            this.showAlert('Login successful!', 'success');
        } catch (error) {
            this.showAlert('Login failed. Check your credentials.', 'error');
        }
    }

    logout() {
        api.logout();
        this.showAuthForms();
        this.showAlert('You have been logged out.', 'info');
    }

    showAuthForms() {
        const authContainer = document.getElementById('auth-container');
        const mainContent = document.getElementById('main-content');
        const logoutBtn = document.getElementById('logoutBtn');

        authContainer.style.display = 'flex';
        mainContent.style.display = 'none';
        logoutBtn.style.display = 'none';

        authContainer.innerHTML = `
            <div style="width: 100%; max-width: 900px;">
                <div style="display: flex; gap: 2rem; flex-wrap: wrap;">
                    <!-- Login Form -->
                    <div class="auth-form" style="flex: 1; min-width: 300px;">
                        <h2>Login</h2>
                        <form id="loginForm">
                            <div class="form-group">
                                <label>Username</label>
                                <input type="text" id="loginUsername" required>
                            </div>
                            <div class="form-group">
                                <label>Password</label>
                                <input type="password" id="loginPassword" required>
                            </div>
                            <button type="submit" class="btn btn-primary">Login</button>
                        </form>
                        <div class="auth-link">
                            Don't have an account? <a href="#" onclick="document.getElementById('registerForm').scrollIntoView(); return false;">Register here</a>
                        </div>
                    </div>

                    <!-- Register Form -->
                    <div class="auth-form" style="flex: 1; min-width: 300px;">
                        <h2>Register</h2>
                        <form id="registerForm">
                            <div class="form-group">
                                <label>Username</label>
                                <input type="text" id="registerUsername" required>
                            </div>
                            <div class="form-group">
                                <label>Email</label>
                                <input type="email" id="registerEmail" required>
                            </div>
                            <div class="form-group">
                                <label>Password</label>
                                <input type="password" id="registerPassword" required>
                            </div>
                            <button type="submit" class="btn btn-success">Register</button>
                        </form>
                    </div>
                </div>
            </div>
        `;

        // Attach event listeners
        document.getElementById('loginForm').addEventListener('submit', (e) => {
            e.preventDefault();
            const username = document.getElementById('loginUsername').value;
            const password = document.getElementById('loginPassword').value;
            this.login(username, password);
        });

        document.getElementById('registerForm').addEventListener('submit', (e) => {
            e.preventDefault();
            const username = document.getElementById('registerUsername').value;
            const email = document.getElementById('registerEmail').value;
            const password = document.getElementById('registerPassword').value;
            this.register(username, email, password);
        });
    }

    showMainContent() {
        const authContainer = document.getElementById('auth-container');
        const mainContent = document.getElementById('main-content');
        const logoutBtn = document.getElementById('logoutBtn');

        authContainer.style.display = 'none';
        mainContent.style.display = 'block';
        logoutBtn.style.display = 'block';

        logoutBtn.addEventListener('click', () => this.logout());
    }

    showAlert(message, type = 'info') {
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type}`;
        alertDiv.textContent = message;

        const container = document.querySelector('.container');
        container.insertBefore(alertDiv, container.firstChild);

        setTimeout(() => alertDiv.remove(), 5000);
    }
}

// Create global auth manager instance
const authManager = new AuthManager();
