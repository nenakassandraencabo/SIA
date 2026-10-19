document.addEventListener('click', (event) => {
    const toggle = event.target.closest('[data-password-toggle]');
    if (toggle) {
        const input = document.getElementById(toggle.dataset.passwordToggle);
        if (!input) return;
        const visible = input.type === 'password';
        input.type = visible ? 'text' : 'password';
        toggle.textContent = visible ? 'Hide' : 'Show';
        toggle.setAttribute('aria-label', visible ? 'Hide password' : 'Show password');
    }

    const dismiss = event.target.closest('[data-dismiss]');
    if (dismiss) dismiss.closest('.message')?.remove();

    const menuButton = event.target.closest('[data-menu-toggle]');
    if (menuButton) {
        const sidebar = document.getElementById('sidebar');
        const open = sidebar.classList.toggle('is-open');
        menuButton.setAttribute('aria-expanded', String(open));
    }
});

document.addEventListener('submit', (event) => {
    const form = event.target.closest('[data-confirm]');
    if (form && !window.confirm(form.dataset.confirm)) event.preventDefault();
});
