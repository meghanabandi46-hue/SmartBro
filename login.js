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

  // Standard Demo Fallback Accounts (for client-side preview before Flask server is launched)
  const fallbackAccounts = {
    'student1': { password: 'student123', role: 'student', name: 'Meghana', redirect: 'index.html' },
    'teacher_class': { password: 'class123', role: 'class_teacher', name: 'Dr. Raman', redirect: 'class_teacher.html' },
    'teacher_priya': { password: 'priya123', role: 'subject_teacher', name: 'Ms. Priya', redirect: 'subject_teacher.html' },
    'support_staff': { password: 'support123', role: 'support', name: 'Alex Patel', redirect: 'support.html' }
  };

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
          // Save in localStorage for static backup/state syncing
          localStorage.setItem('udaan_session', JSON.stringify(data.user));
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
      // 2. Client-side fallback authentication for static preview / testing before Flask starts
      const account = fallbackAccounts[username];
      if (!account || account.password !== password) {
        showAlert('Invalid username or password. Check demo credentials below.');
        submitBtn.disabled = false;
        submitBtn.innerHTML = 'Sign In to UDAAN <span>→</span>';
        return;
      }

      // Check role authorization
      if (account.role !== selectedRole) {
        const roleNames = {
          student: 'Student',
          class_teacher: 'Class Teacher',
          subject_teacher: 'Subject Teacher',
          support: 'Support Line'
        };
        showAlert(`Role mismatch: This account belongs to role "${roleNames[account.role]}", but you selected "${roleNames[selectedRole]}". Please select the matching role card.`);
        submitBtn.disabled = false;
        submitBtn.innerHTML = 'Sign In to UDAAN <span>→</span>';
        return;
      }

      // Successful simulated login
      showAlert('Signed in successfully! Redirecting...', 'success');
      localStorage.setItem('udaan_session', JSON.stringify({
        username: username,
        role: account.role,
        name: account.name
      }));

      const roleRouteMap = {
        student: '/student',
        class_teacher: '/class-teacher',
        subject_teacher: '/subject-teacher',
        support: '/support'
      };
      setTimeout(() => {
        if (window.location.protocol === 'file:') {
          window.location.href = account.redirect;
        } else {
          window.location.href = roleRouteMap[account.role] || '/student';
        }
      }, 450);
    }
  });
});
