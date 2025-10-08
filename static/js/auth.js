/**
 * Authentication form handlers and client-side validation
 * Borrowed from common Flask/Bootstrap patterns
 */

/**
 * Display message to user (error or success)
 */
function showMessage(message, type = 'error') {
    const messageEl = document.getElementById('auth-message');
    if (!messageEl) return;

    messageEl.textContent = message;
    messageEl.className = `auth-message auth-message-${type}`;
    messageEl.style.display = 'block';

    // Auto-hide after 5 seconds for success messages
    if (type === 'success') {
        setTimeout(() => {
            messageEl.style.display = 'none';
        }, 5000);
    }
}

/**
 * Clear all messages
 */
function clearMessage() {
    const messageEl = document.getElementById('auth-message');
    if (messageEl) {
        messageEl.style.display = 'none';
    }
}

/**
 * Validate email format
 */
function validateEmail(email) {
    const emailRegex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
    return emailRegex.test(email);
}

/**
 * Validate password strength
 */
function validatePassword(password) {
    if (password.length < 8) {
        return { valid: false, error: 'Password must be at least 8 characters long' };
    }

    if (!/[A-Z]/.test(password)) {
        return { valid: false, error: 'Password must contain at least one uppercase letter' };
    }

    if (!/[a-z]/.test(password)) {
        return { valid: false, error: 'Password must contain at least one lowercase letter' };
    }

    if (!/[0-9!@#$%^&*(),.?":{}|<>]/.test(password)) {
        return { valid: false, error: 'Password must contain at least one number or special character' };
    }

    return { valid: true };
}

/**
 * Initialize login form
 */
function initLoginForm() {
    const form = document.getElementById('login-form');
    if (!form) return;

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        clearMessage();

        const email = document.getElementById('email').value.trim().toLowerCase();
        const password = document.getElementById('password').value;
        const remember = document.getElementById('remember').checked;

        // Validate email
        if (!validateEmail(email)) {
            showMessage('Please enter a valid email address', 'error');
            return;
        }

        if (!password) {
            showMessage('Password is required', 'error');
            return;
        }

        // Show loading state
        const btn = document.getElementById('login-btn');
        const btnText = document.getElementById('login-btn-text');
        const spinner = document.getElementById('login-spinner');
        btn.disabled = true;
        btnText.style.display = 'none';
        spinner.style.display = 'inline-block';

        try {
            const response = await fetch('/auth/login-email', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ email, password, remember })
            });

            const data = await response.json();

            if (response.ok) {
                showMessage('Login successful! Redirecting...', 'success');
                // Redirect to home page after short delay
                setTimeout(() => {
                    window.location.href = '/';
                }, 1000);
            } else {
                showMessage(data.error || 'Login failed. Please try again.', 'error');
                // Reset button state
                btn.disabled = false;
                btnText.style.display = 'inline';
                spinner.style.display = 'none';
            }
        } catch (error) {
            console.error('Login error:', error);
            showMessage('Network error. Please check your connection and try again.', 'error');
            // Reset button state
            btn.disabled = false;
            btnText.style.display = 'inline';
            spinner.style.display = 'none';
        }
    });
}

/**
 * Initialize signup form
 */
function initSignupForm() {
    const form = document.getElementById('signup-form');
    if (!form) return;

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        clearMessage();

        const name = document.getElementById('name').value.trim() || null;
        const email = document.getElementById('email').value.trim().toLowerCase();
        const password = document.getElementById('password').value;
        const confirmPassword = document.getElementById('confirm-password').value;

        // Validate email
        if (!validateEmail(email)) {
            showMessage('Please enter a valid email address', 'error');
            return;
        }

        // Validate password
        const passwordValidation = validatePassword(password);
        if (!passwordValidation.valid) {
            showMessage(passwordValidation.error, 'error');
            return;
        }

        // Check password match
        if (password !== confirmPassword) {
            showMessage('Passwords do not match', 'error');
            return;
        }

        // Show loading state
        const btn = document.getElementById('signup-btn');
        const btnText = document.getElementById('signup-btn-text');
        const spinner = document.getElementById('signup-spinner');
        btn.disabled = true;
        btnText.style.display = 'none';
        spinner.style.display = 'inline-block';

        try {
            const response = await fetch('/auth/register', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ email, password, name })
            });

            const data = await response.json();

            if (response.ok) {
                showMessage('Account created successfully! Redirecting...', 'success');
                // Redirect to home page after short delay
                setTimeout(() => {
                    window.location.href = '/';
                }, 1000);
            } else {
                showMessage(data.error || 'Signup failed. Please try again.', 'error');
                // Reset button state
                btn.disabled = false;
                btnText.style.display = 'inline';
                spinner.style.display = 'none';
            }
        } catch (error) {
            console.error('Signup error:', error);
            showMessage('Network error. Please check your connection and try again.', 'error');
            // Reset button state
            btn.disabled = false;
            btnText.style.display = 'inline';
            spinner.style.display = 'none';
        }
    });

    // Real-time password validation feedback
    const passwordInput = document.getElementById('password');
    if (passwordInput) {
        passwordInput.addEventListener('input', () => {
            const validation = validatePassword(passwordInput.value);
            if (!validation.valid && passwordInput.value.length > 0) {
                passwordInput.setCustomValidity(validation.error);
            } else {
                passwordInput.setCustomValidity('');
            }
        });
    }
}
