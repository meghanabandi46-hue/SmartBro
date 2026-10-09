// UDAAN Unified Authentication Client

document.addEventListener('DOMContentLoaded', () => {
  const roleCards = document.querySelectorAll('.role-card');
  const roleInput = document.getElementById('selectedRole');
  const loginForm = document.getElementById('loginForm');
  const usernameInput = document.getElementById('username');
  const passwordInput = document.getElementById('password');
  const togglePasswordBtn = document.getElementById('togglePassword');
  const alertBox = document.getElementById('alertBox');
  const submitBtn = document.getElementById('submitBtn');
  const demoPills = document.querySelectorAll('.demo-pill');

  // Role Selection Logic
  roleCards.forEach(card => {
    card.addEventListener('click', () => {
      roleCards.forEach(c => c.classList.remove('active'));
      card.classList.add('active');
      const role = card.dataset.role;
      roleInput.value = role;
      clearAlert();
    });
  });

  // Password Visibility Toggle
  if (togglePasswordBtn) {
    togglePasswordBtn.addEventListener('click', () => {
      const isPassword = passwordInput.getAttribute('type') === 'password';
      passwordInput.setAttribute('type', isPassword ? 'text' : 'password');
      togglePasswordBtn.textContent = isPassword ? 'Hide' : 'Show';
    });
  }

  // Demo Credentials Quick-Fill helper
  demoPills.forEach(pill => {
    pill.addEventListener('click', () => {
      const role = pill.dataset.role;
      const user = pill.dataset.user;
      const pass = pill.dataset.pass;

      // Select matching role card
      roleCards.forEach(c => {
        if (c.dataset.role === role) {
          c.classList.add('active');
          roleInput.value = role;
        } else {
          c.classList.remove('active');
        }
      });

      usernameInput.value = user;
      passwordInput.value = pass;
      clearAlert();
    });
  });

  // Helper Alerts
  function showAlert(message, type = 'danger') {
    alertBox.textContent = message;
    alertBox.className = `alert-box alert-${type} show`;
  }

  function clearAlert() {
    alertBox.textContent = '';
    alertBox.className = 'alert-box';
  }

  // Form Submission
  loginForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    clearAlert();

    const selectedRole = roleInput.value;
    const username = usernameInput.value.trim();
    const password = passwordInput.value;

    if (!selectedRole) {
      showAlert('Please choose a role from the role selector above.');
      return;
    }
    if (!username) {
      showAlert('Please enter your username or email.');
      usernameInput.focus();
      return;
    }
    if (!password) {
      showAlert('Please enter your password.');
      passwordInput.focus();
      return;
    }

    submitBtn.disabled = true;
    submitBtn.innerHTML = 'Signing in...';

    try {
      // 1. Try real Flask Backend authentication
      const response = await fetch('/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          role: selectedRole,
          username: username,
          password: password
        })
      });

      if (response.ok) {
        const data = await response.json();
        if (data.success) {
          showAlert('Signed in successfully! Redirecting...', 'success');
          const roleRouteMap = {
            student: '/student',
            class_teacher: '/class-teacher',
            subject_teacher: '/subject-teacher',
            support: '/support'
          };
          setTimeout(() => {
            window.location.href = data.redirect_url || roleRouteMap[selectedRole] || '/student';
          }, 450);
          return;
        } else {
          showAlert(data.message || 'Invalid username or password.');
          submitBtn.disabled = false;
          submitBtn.innerHTML = 'Sign In to UDAAN <span>→</span>';
          return;
        }
      } else if (response.status === 401 || response.status === 403 || response.status === 400) {
        const err = await response.json();
        showAlert(err.message || 'Invalid credentials or role mismatch.');
        submitBtn.disabled = false;
        submitBtn.innerHTML = 'Sign In to UDAAN <span>→</span>';
        return;
      }
      throw new Error('Backend offline or static mode');
    } catch (networkErr) {
      // Authentication must always be verified by Flask; never simulate a login in the browser.
      showAlert('Cannot reach the login server. Start the Flask application and try again.');
      submitBtn.disabled = false;
      submitBtn.innerHTML = 'Sign In to UDAAN <span>→</span>';
    }
  });
});
