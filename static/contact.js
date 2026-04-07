function submitContactForm() {
    const name  = document.getElementById('c-name').value.trim();
    const email = document.getElementById('c-email').value.trim();
    const msg   = document.getElementById('c-msg').value.trim();

    setCError('c-field-name',  !name);
    setCError('c-field-email', !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email));
    setCError('c-field-msg',   !msg);

    if (!name || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email) || !msg) return;

    document.getElementById('contactForm').submit();
}

function setCError(id, hasError) {
    document.getElementById(id).classList.toggle('error', hasError);
}

function resetContactForm() {
    ['c-field-name', 'c-field-email', 'c-field-msg'].forEach(id =>
        document.getElementById(id).classList.remove('error')
    );
    document.getElementById('contactForm').classList.remove('hidden');
    document.getElementById('successBox').classList.remove('show');
}

['c-name', 'c-email', 'c-msg'].forEach(id => {
    document.getElementById(id).addEventListener('input', () => {
        document.getElementById('c-field-' + id.replace('c-', '')).classList.remove('error');
    });
});
