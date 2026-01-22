/**
 * AquaTrace Authentication JavaScript
 * Client-side form validation for login and signup
 */

// =====================
// Validation Functions
// =====================

/**
 * Validate email format
 */
function validateEmail(email) {
  const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return regex.test(email);
}

/**
 * Validate password strength
 */
function validatePassword(password) {
  const checks = {
    length: password.length >= 8,
    uppercase: /[A-Z]/.test(password),
    lowercase: /[a-z]/.test(password),
    number: /[0-9]/.test(password),
    special: /[@$!%*?&#]/.test(password)
  };
  
  const score = Object.values(checks).filter(Boolean).length;
  
  return {
    valid: checks.length,
    score: score,
    checks: checks
  };
}

/**
 * Calculate password strength level
 */
function getPasswordStrength(password) {
  const result = validatePassword(password);
  
  if (result.score >= 5) return { level: 'strong', text: 'Very Strong', class: 'strength-strong' };
  if (result.score >= 4) return { level: 'good', text: 'Strong', class: 'strength-good' };
  if (result.score >= 3) return { level: 'fair', text: 'Good', class: 'strength-fair' };
  if (result.score >= 2) return { level: 'weak', text: 'Fair', class: 'strength-weak' };
  return { level: 'very-weak', text: 'Weak', class: 'strength-weak' };
}

// =====================
// UI Functions
// =====================

/**
 * Show error message
 */
function showError(message, formId = null) {
  // Remove existing error toasts
  const existingToasts = document.querySelectorAll('.error-toast');
  existingToasts.forEach(toast => toast.remove());
  
  // Create error toast
  const toast = document.createElement('div');
  toast.className = 'error-toast';
  toast.innerHTML = `
    <i class="fas fa-exclamation-circle"></i>
    <span>${message}</span>
  `;
  
  // Add custom styles for error toast
  toast.style.cssText = `
    position: fixed;
    bottom: 2rem;
    right: 2rem;
    background: #f44336;
    color: white;
    padding: 1rem 1.5rem;
    border-radius: 8px;
    box-shadow: 0 4px 16px rgba(0,0,0,0.2);
    z-index: 1000;
    display: flex;
    align-items: center;
    gap: 0.75rem;
    font-weight: 600;
    animation: slideUp 0.3s ease;
  `;
  
  document.body.appendChild(toast);
  
  // Remove after 5 seconds
  setTimeout(() => {
    toast.style.animation = 'fadeOut 0.3s ease forwards';
    setTimeout(() => toast.remove(), 300);
  }, 5000);
}

/**
 * Show success message
 */
function showSuccess(message) {
  const toast = document.createElement('div');
  toast.className = 'success-toast';
  toast.innerHTML = `
    <i class="fas fa-check-circle"></i>
    <span>${message}</span>
  `;
  
  toast.style.cssText = `
    position: fixed;
    bottom: 2rem;
    right: 2rem;
    background: #4caf50;
    color: white;
    padding: 1rem 1.5rem;
    border-radius: 8px;
    box-shadow: 0 4px 16px rgba(0,0,0,0.2);
    z-index: 1000;
    display: flex;
    align-items: center;
    gap: 0.75rem;
    font-weight: 600;
    animation: slideUp 0.3s ease;
  `;
  
  document.body.appendChild(toast);
  
  setTimeout(() => {
    toast.style.animation = 'fadeOut 0.3s ease forwards';
    setTimeout(() => toast.remove(), 300);
  }, 3000);
}

/**
 * Update password strength indicator
 */
function updatePasswordStrength(password) {
  const strengthIndicator = document.getElementById('passwordStrength');
  if (!strengthIndicator) return;
  
  const bar = strengthIndicator.querySelector('.password-strength-bar');
  if (!bar) return;
  
  if (password.length === 0) {
    bar.className = 'password-strength-bar';
    bar.style.width = '0';
    return;
  }
  
  const strength = getPasswordStrength(password);
  bar.className = `password-strength-bar ${strength.class}`;
}

/**
 * Add loading state to button
 */
function setButtonLoading(button, loading) {
  if (loading) {
    button.classList.add('loading');
    button.disabled = true;
    const icon = button.querySelector('i');
    if (icon) {
      icon.className = 'fas fa-spinner fa-spin';
    }
  } else {
    button.classList.remove('loading');
    button.disabled = false;
    const icon = button.querySelector('i');
    if (icon && button.id === 'loginForm') {
      icon.className = 'fas fa-sign-in-alt';
    } else if (icon) {
      icon.className = 'fas fa-user-plus';
    }
  }
}

// =====================
// Form Validation
// =====================

/**
 * Validate login form
 */
function validateLoginForm(event) {
  const form = event.target;
  const email = document.getElementById('email').value.trim();
  const password = document.getElementById('password').value;
  
  // Email validation
  if (!email) {
    showError('Please enter your email address');
    event.preventDefault();
    return false;
  }
  
  if (!validateEmail(email)) {
    showError('Please enter a valid email address');
    event.preventDefault();
    return false;
  }
  
  // Password validation
  if (!password) {
    showError('Please enter your password');
    event.preventDefault();
    return false;
  }
  
  // Show loading state
  const submitBtn = form.querySelector('button[type="submit"]');
  setButtonLoading(submitBtn, true);
  
  return true;
}

/**
 * Validate signup form
 */
function validateSignupForm(event) {
  const form = event.target;
  const email = document.getElementById('email').value.trim();
  const fullName = document.getElementById('full_name').value.trim();
  const password = document.getElementById('password').value;
  const confirmPassword = document.getElementById('confirm_password').value;
  
  // Email validation
  if (!email) {
    showError('Please enter your email address');
    event.preventDefault();
    return false;
  }
  
  if (!validateEmail(email)) {
    showError('Please enter a valid email address');
    event.preventDefault();
    return false;
  }
  
  // Name validation
  if (!fullName || fullName.length < 2) {
    showError('Please enter your full name (at least 2 characters)');
    event.preventDefault();
    return false;
  }
  
  // Password validation
  if (!password) {
    showError('Please enter a password');
    event.preventDefault();
    return false;
  }
  
  const passwordCheck = validatePassword(password);
  if (!passwordCheck.valid) {
    showError('Password must be at least 8 characters long');
    event.preventDefault();
    return false;
  }
  
  // Password match validation
  if (password !== confirmPassword) {
    showError('Passwords do not match');
    event.preventDefault();
    return false;
  }
  
  // Show loading state
  const submitBtn = form.querySelector('button[type="submit"]');
  setButtonLoading(submitBtn, true);
  
  return true;
}

// =====================
// Event Listeners
// =====================

/**
 * Initialize when DOM is ready
 */
document.addEventListener('DOMContentLoaded', function() {
  
  // Login form
  const loginForm = document.getElementById('loginForm');
  if (loginForm) {
    loginForm.addEventListener('submit', validateLoginForm);
  }
  
  // Signup form
  const signupForm = document.getElementById('signupForm');
  if (signupForm) {
    signupForm.addEventListener('submit', validateSignupForm);
  }
  
  // Password strength indicator
  const passwordField = document.getElementById('password');
  if (passwordField) {
    passwordField.addEventListener('input', function() {
      updatePasswordStrength(this.value);
    });
    
    // Show password strength feedback
    passwordField.addEventListener('focus', function() {
      const strengthIndicator = document.getElementById('passwordStrength');
      if (strengthIndicator) {
        strengthIndicator.style.display = 'block';
      }
    });
  }
  
  // Real-time password match validation
  const confirmPasswordField = document.getElementById('confirm_password');
  const originalPasswordField = document.getElementById('password');
  
  if (confirmPasswordField && originalPasswordField) {
    confirmPasswordField.addEventListener('input', function() {
      if (this.value && this.value !== originalPasswordField.value) {
        this.setCustomValidity('Passwords do not match');
      } else {
        this.setCustomValidity('');
      }
    });
    
    originalPasswordField.addEventListener('input', function() {
      if (confirmPasswordField.value) {
        if (confirmPasswordField.value !== this.value) {
          confirmPasswordField.setCustomValidity('Passwords do not match');
        } else {
          confirmPasswordField.setCustomValidity('');
        }
      }
    });
  }
  
  // Email field - convert to lowercase
  const emailField = document.getElementById('email');
  if (emailField) {
    emailField.addEventListener('blur', function() {
      this.value = this.value.trim().toLowerCase();
    });
  }
  
  // Auto-focus on first input
  const firstInput = document.querySelector('input[autofocus]');
  if (firstInput) {
    firstInput.focus();
  }
});

// =====================
// CSS Animations
// =====================

// Add animation styles if not already present
if (!document.getElementById('auth-animations')) {
  const style = document.createElement('style');
  style.id = 'auth-animations';
  style.textContent = `
    @keyframes slideUp {
      from {
        transform: translateY(100%);
        opacity: 0;
      }
      to {
        transform: translateY(0);
        opacity: 1;
      }
    }
    
    @keyframes fadeOut {
      to {
        opacity: 0;
        transform: translateY(20px);
      }
    }
  `;
  document.head.appendChild(style);
}

console.log('AquaTrace Authentication module loaded');