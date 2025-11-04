// Auth Pages JavaScript - Modern Interactive Features

(function() {
  'use strict';

  // Initialize AOS animations
  if (typeof AOS !== 'undefined') {
    AOS.init({
      duration: 800,
      easing: 'ease-in-out',
      once: true
    });
  }

  // Theme toggle
  const themeToggle = document.getElementById('themeToggle');
  if (themeToggle) {
    themeToggle.addEventListener('click', () => {
      const currentTheme = document.documentElement.getAttribute('data-theme');
      const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
      document.documentElement.setAttribute('data-theme', newTheme);
      localStorage.setItem('theme', newTheme);
      updateThemeIcon(newTheme);
    });

    // Load saved theme
    const savedTheme = localStorage.getItem('theme') || 'light';
    document.documentElement.setAttribute('data-theme', savedTheme);
    updateThemeIcon(savedTheme);
  }

  function updateThemeIcon(theme) {
    const icon = themeToggle?.querySelector('i');
    if (icon) {
      icon.className = theme === 'dark' ? 'fas fa-sun' : 'fas fa-moon';
    }
  }

  // Password toggle - handles both .password-toggle and .registration-password-toggle
  document.querySelectorAll('.password-toggle, .registration-password-toggle').forEach(btn => {
    btn.addEventListener('click', function() {
      const selector = this.getAttribute('data-password-toggle') || '#password';
      const input = document.querySelector(selector);
      if (input) {
        const type = input.type === 'password' ? 'text' : 'password';
        input.type = type;
        
        // Update icon instead of text content
        const icon = this.querySelector('i');
        if (icon) {
          icon.className = type === 'password' ? 'fas fa-eye' : 'fas fa-eye-slash';
        } else {
          // Fallback for buttons without icon
          this.textContent = type === 'password' ? '👁️' : '🙈';
        }
      }
    });
  });

  // Password strength indicator - handles both .password-strength and .registration-password-strength
  const passwordInputs = document.querySelectorAll('input[type="password"]');
  passwordInputs.forEach(input => {
    const strengthIndicator = input.parentElement.querySelector('.password-strength, .registration-password-strength');
    if (strengthIndicator) {
      input.addEventListener('input', function() {
        const strength = calculatePasswordStrength(this.value);
        strengthIndicator.textContent = strength.text;
        strengthIndicator.className = `${strengthIndicator.className.split(' ')[0]} ${strength.class}`;
      });
    }
  });

  function calculatePasswordStrength(password) {
    if (!password) return { text: '', class: '' };
    
    let strength = 0;
    if (password.length >= 8) strength++;
    if (password.length >= 12) strength++;
    if (/[a-z]/.test(password)) strength++;
    if (/[A-Z]/.test(password)) strength++;
    if (/[0-9]/.test(password)) strength++;
    if (/[^A-Za-z0-9]/.test(password)) strength++;
    
    // Penalty for common passwords
    const commonPasswords = ['password', 'qwerty', '123456', 'abc123', 'admin', 'letmein'];
    if (commonPasswords.some(cp => password.toLowerCase().includes(cp))) {
      strength = Math.max(0, strength - 2);
    }

    const lang = document.documentElement.lang || 'en';
    if (strength <= 2) {
      return { text: lang === 'pl' ? 'Słabe' : 'Weak', class: 'weak' };
    } else if (strength <= 4) {
      return { text: lang === 'pl' ? 'Średnie' : 'Medium', class: 'medium' };
    } else {
      return { text: lang === 'pl' ? 'Silne' : 'Strong', class: 'strong' };
    }
  }

  // Form validation
  document.querySelectorAll('form').forEach(form => {
    form.addEventListener('submit', function(e) {
      const submitBtn = form.querySelector('button[type="submit"]');
      if (submitBtn) {
        submitBtn.classList.add('loading');
        submitBtn.disabled = true;
      }
    });
  });

  // Show error message
  function showError(message) {
    const errorDiv = document.createElement('div');
    errorDiv.className = 'auth-error fade-in';
    errorDiv.innerHTML = `<i class="fas fa-exclamation-circle"></i> ${message}`;
    
    const form = document.querySelector('.auth-form');
    if (form) {
      form.insertBefore(errorDiv, form.firstChild);
      setTimeout(() => errorDiv.remove(), 5000);
    }
  }

  // Show success message
  function showSuccess(message) {
    const successDiv = document.createElement('div');
    successDiv.className = 'auth-success fade-in';
    successDiv.innerHTML = `<i class="fas fa-check-circle"></i> ${message}`;
    
    const form = document.querySelector('.auth-form');
    if (form) {
      form.insertBefore(successDiv, form.firstChild);
      setTimeout(() => successDiv.remove(), 3000);
    }
  }

  // Login form handler
  const loginForm = document.querySelector('.login-form');
  if (loginForm) {
    loginForm.addEventListener('submit', async function(e) {
      e.preventDefault();
      
      const email = loginForm.querySelector('[name="email"]').value.trim();
      const password = loginForm.querySelector('[name="password"]').value;
      const submitBtn = loginForm.querySelector('button[type="submit"]');
      
      if (!email || !password) {
        showError(window.t?.('Please fill in all fields') || 'Please fill in all fields');
        submitBtn?.classList.remove('loading');
        submitBtn.disabled = false;
        return;
      }

      try {
        const response = await fetch('/api/auth/login', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCsrfToken()
          },
          body: JSON.stringify({ email, password })
        });

        const data = await response.json();

        if (!response.ok) {
          throw new Error(data.detail || data.message || 'Login failed');
        }

        // Check if 2FA is required
        if (data.requires_2fa) {
          showSuccess(window.t?.('Verification code sent to your email') || 'Verification code sent to your email');
          document.getElementById('2faSection')?.style.setProperty('display', 'block');
          loginForm.querySelector('.social-login')?.style.setProperty('display', 'none');
          loginForm.querySelector('.divider')?.style.setProperty('display', 'none');
          loginForm.querySelector('.button-group')?.style.setProperty('display', 'none');
          document.getElementById('token')?.focus();
        } else {
          // Successful login
          window.location.href = '/dashboard';
        }
      } catch (error) {
        showError(error.message);
        submitBtn?.classList.remove('loading');
        submitBtn.disabled = false;
      }
    });

    // 2FA verification
    const verify2FABtn = document.getElementById('verify2FA');
    if (verify2FABtn) {
      verify2FABtn.addEventListener('click', async function() {
        const token = document.getElementById('token')?.value.trim();
        if (!token) {
          showError(window.t?.('Please enter verification code') || 'Please enter verification code');
          return;
        }

        try {
          const response = await fetch('/api/auth/verify-2fa-login', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              'X-CSRFToken': getCsrfToken()
            },
            body: JSON.stringify({ token })
          });

          const data = await response.json();

          if (!response.ok) {
            throw new Error(data.detail || 'Verification failed');
          }

          window.location.href = '/dashboard';
        } catch (error) {
          showError(error.message);
        }
      });
    }
  }

  // Registration form handler
  const registerForm = document.querySelector('.registration-form');
  if (registerForm) {
    registerForm.addEventListener('submit', async function(e) {
      e.preventDefault();
      
      const firstName = registerForm.querySelector('[name="firstName"]')?.value.trim();
      const lastName = registerForm.querySelector('[name="lastName"]')?.value.trim();
      const email = registerForm.querySelector('[name="email"]')?.value.trim();
      const password = registerForm.querySelector('[name="password"]')?.value;
      const submitBtn = registerForm.querySelector('button[type="submit"]');
      
      if (!firstName || !lastName || !email || !password) {
        showError(window.t?.('Please fill in all fields') || 'Please fill in all fields');
        submitBtn?.classList.remove('loading');
        submitBtn.disabled = false;
        return;
      }

      // Validate password strength
      const strength = calculatePasswordStrength(password);
      if (strength.class === 'weak') {
        showError(window.t?.('Password is too weak') || 'Password is too weak');
        submitBtn?.classList.remove('loading');
        submitBtn.disabled = false;
        return;
      }

      try {
        const response = await fetch('/api/auth/register', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCsrfToken()
          },
          body: JSON.stringify({
            email,
            password,
            name: `${firstName} ${lastName}`.trim()
          })
        });

        const data = await response.json();

        if (!response.ok) {
          throw new Error(data.detail || data.message || 'Registration failed');
        }

        showSuccess(window.t?.('Registration successful! Redirecting...') || 'Registration successful! Redirecting...');
        setTimeout(() => {
          window.location.href = '/login';
        }, 1500);
      } catch (error) {
        showError(error.message);
        submitBtn?.classList.remove('loading');
        submitBtn.disabled = false;
      }
    });
  }

  // Magic Link login
  const magicLinkForm = document.querySelector('.magic-link-form');
  if (magicLinkForm) {
    magicLinkForm.addEventListener('submit', async function(e) {
      e.preventDefault();
      
      const email = magicLinkForm.querySelector('[name="email"]').value.trim();
      const submitBtn = magicLinkForm.querySelector('button[type="submit"]');
      
      if (!email) {
        showError(window.t?.('Please enter your email') || 'Please enter your email');
        return;
      }

      try {
        const response = await fetch('/api/auth/magic-link-login/', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCsrfToken()
          },
          body: JSON.stringify({ email })
        });

        const data = await response.json();

        if (!response.ok) {
          throw new Error(data.detail || 'Failed to send magic link');
        }

        showSuccess(window.t?.('Magic link sent to your email!') || 'Magic link sent to your email!');
      } catch (error) {
        showError(error.message);
        submitBtn?.classList.remove('loading');
        submitBtn.disabled = false;
      }
    });
  }

  // Get CSRF token
  function getCsrfToken() {
    const cookie = document.cookie.split(';').find(c => c.trim().startsWith('csrftoken='));
    return cookie ? cookie.split('=')[1] : '';
  }

  // Back button handler
  document.querySelectorAll('[data-action="back"], [data-action="cancel"]').forEach(btn => {
    btn.addEventListener('click', function(e) {
      e.preventDefault();
      if (document.referrer && !document.referrer.includes(window.location.host)) {
        window.location.href = '/welcome';
      } else {
        history.back();
      }
    });
  });

  // Welcome page action cards
  document.querySelectorAll('.welcome-card').forEach(card => {
    card.addEventListener('click', function(e) {
      const href = this.getAttribute('href');
      if (href) {
        e.preventDefault();
        // Add animation before navigation
        this.style.transform = 'scale(0.95)';
        setTimeout(() => {
          window.location.href = href;
        }, 150);
      }
    });
  });

  // Input focus animations
  document.querySelectorAll('.form-input').forEach(input => {
    input.addEventListener('focus', function() {
      this.parentElement.classList.add('focused');
    });
    
    input.addEventListener('blur', function() {
      this.parentElement.classList.remove('focused');
    });
  });

  // Auto-format email input
  document.querySelectorAll('input[type="email"]').forEach(input => {
    input.addEventListener('blur', function() {
      this.value = this.value.trim().toLowerCase();
    });
  });

})();

