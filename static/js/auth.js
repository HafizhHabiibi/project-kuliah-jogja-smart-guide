/**
 * Jogja Smart Guide — Auth JS
 * Form validation for login and register pages
 */

document.addEventListener('DOMContentLoaded', () => {
    initLoginForm();
    initRegisterForm();
    initPasswordToggles();
});


/**
 * Login form validation
 */
function initLoginForm() {
    const form = document.getElementById('login-form');
    if (!form) return;

    form.addEventListener('submit', (e) => {
        let isValid = true;

        const email = document.getElementById('email');
        const password = document.getElementById('password');

        // Email validation
        if (!email.value.trim() || !isValidEmail(email.value)) {
            showFieldError(email, 'email-error');
            isValid = false;
        } else {
            clearFieldError(email, 'email-error');
        }

        // Password validation
        if (!password.value) {
            showFieldError(password, 'password-error');
            isValid = false;
        } else {
            clearFieldError(password, 'password-error');
        }

        if (!isValid) {
            e.preventDefault();
        }
    });

    // Clear errors on input
    ['email', 'password'].forEach(id => {
        const el = document.getElementById(id);
        if (el) {
            el.addEventListener('input', () => clearFieldError(el, `${id}-error`));
        }
    });
}


/**
 * Register form validation
 */
/**
 * Slider value texts mapping
 */
const sliderTexts = {
    'pref_nature': {
        1: 'Benci Outdoor / Kapok',
        2: 'Kurang Suka',
        3: 'Netral / Biasa Saja',
        4: 'Suka Alam & Outdoor',
        5: 'Sangat Suka Petualangan'
    },
    'pref_culture': {
        1: 'Tidak Tertarik Budaya/Sejarah',
        2: 'Kurang Tertarik',
        3: 'Netral / Biasa Saja',
        4: 'Tertarik Sejarah & Budaya',
        5: 'Sangat Cinta Sejarah & Budaya'
    },
    'pref_culinary': {
        1: 'Sekadar Makan Saja',
        2: 'Kurang Berminat Kulineran',
        3: 'Netral / Biasa Saja',
        4: 'Suka Wisata Kuliner',
        5: 'Pemburu Kuliner Sejati (Foodie)'
    },
    'pref_crowd': {
        1: 'Suka Tempat Sangat Sepi',
        2: 'Lebih Suka Tempat Tenang',
        3: 'Netral / Tidak Masalah',
        4: 'Suka Suasana Ramai/Hidup',
        5: 'Sangat Nyaman di Keramaian'
    },
    'pref_effort': {
        1: 'Sangat Santai (Akses Mudah)',
        2: 'Santai (Jalan Kaki Sedikit)',
        3: 'Sedang (Jalan Kaki Normal)',
        4: 'Menantang (Perlu Trekking)',
        5: 'Sangat Ekstrem (Fisik Kuat)'
    }
};

/**
 * Register form validation & Wizard flow
 */
function initRegisterForm() {
    const form = document.getElementById('register-form');
    if (!form) return;

    const btnNext = document.getElementById('btn-next-step');
    const btnBack = document.getElementById('btn-back-step');
    const step1 = document.getElementById('step-1');
    const step2 = document.getElementById('step-2');
    const ind1 = document.getElementById('indicator-1');
    const ind2 = document.getElementById('indicator-2');

    // Update slider badges dynamically
    function updateSliderBadges() {
        ['pref_nature', 'pref_culture', 'pref_culinary', 'pref_crowd', 'pref_effort'].forEach(id => {
            const slider = document.getElementById(id);
            const badge = document.getElementById(`val-${id.replace(/_/g, '-')}`);
            if (slider && badge) {
                const val = slider.value;
                badge.textContent = sliderTexts[id][val] || 'Netral';
            }
        });
    }

    // Attach real-time slide events
    ['pref_nature', 'pref_culture', 'pref_culinary', 'pref_crowd', 'pref_effort'].forEach(id => {
        const slider = document.getElementById(id);
        if (slider) {
            slider.addEventListener('input', updateSliderBadges);
        }
    });

    // Step 1 -> Step 2 Navigation with validation
    if (btnNext && btnBack && step1 && step2) {
        btnNext.addEventListener('click', () => {
            let isValid = true;

            const username = document.getElementById('username');
            const email = document.getElementById('email');
            const password = document.getElementById('password');
            const confirmPassword = document.getElementById('confirm_password');

            // Username validation
            if (!username.value.trim()) {
                showFieldError(username, 'username-error');
                isValid = false;
            } else {
                clearFieldError(username, 'username-error');
            }

            // Email validation
            if (!email.value.trim() || !isValidEmail(email.value)) {
                showFieldError(email, 'email-error');
                isValid = false;
            } else {
                clearFieldError(email, 'email-error');
            }

            // Password validation
            if (!password.value || password.value.length < 6) {
                showFieldError(password, 'password-error');
                isValid = false;
            } else {
                clearFieldError(password, 'password-error');
            }

            // Confirm password
            if (password.value !== confirmPassword.value) {
                showFieldError(confirmPassword, 'confirm-password-error');
                isValid = false;
            } else {
                clearFieldError(confirmPassword, 'confirm-password-error');
            }

            if (isValid) {
                // Transition steps
                step1.style.display = 'none';
                step2.style.display = 'block';
                step1.classList.remove('active');
                step2.classList.add('active');

                // Update indicators
                if (ind1 && ind2) {
                    ind1.classList.remove('active');
                    ind1.classList.add('completed');
                    ind2.classList.add('active');
                }

                // Render badges
                updateSliderBadges();
            }
        });

        // Step 2 -> Step 1 Navigation
        btnBack.addEventListener('click', () => {
            step2.style.display = 'none';
            step1.style.display = 'block';
            step2.classList.remove('active');
            step1.classList.add('active');

            if (ind1 && ind2) {
                ind2.classList.remove('active');
                ind1.classList.remove('completed');
                ind1.classList.add('active');
            }
        });
    }

    form.addEventListener('submit', (e) => {
        let isValid = true;

        const username = document.getElementById('username');
        const email = document.getElementById('email');
        const password = document.getElementById('password');
        const confirmPassword = document.getElementById('confirm_password');

        // Username validation
        if (!username.value.trim()) {
            showFieldError(username, 'username-error');
            isValid = false;
        }

        // Email validation
        if (!email.value.trim() || !isValidEmail(email.value)) {
            showFieldError(email, 'email-error');
            isValid = false;
        }

        // Password validation
        if (!password.value || password.value.length < 6) {
            showFieldError(password, 'password-error');
            isValid = false;
        }

        // Confirm password
        if (password.value !== confirmPassword.value) {
            showFieldError(confirmPassword, 'confirm-password-error');
            isValid = false;
        }

        if (!isValid) {
            e.preventDefault();
            // If validation failed on final submit, snap back to Step 1
            if (step1 && step2) {
                step2.style.display = 'none';
                step1.style.display = 'block';
                step2.classList.remove('active');
                step1.classList.add('active');

                if (ind1 && ind2) {
                    ind2.classList.remove('active');
                    ind1.classList.remove('completed');
                    ind1.classList.add('active');
                }
            }
        }
    });

    // Clear errors on input
    ['username', 'email', 'password', 'confirm_password'].forEach(id => {
        const el = document.getElementById(id);
        if (el) {
            const errorId = id.replace('_', '-') + '-error';
            el.addEventListener('input', () => clearFieldError(el, errorId));
        }
    });
}


/**
 * Password visibility toggle
 */
function initPasswordToggles() {
    document.querySelectorAll('.password-toggle').forEach(btn => {
        btn.addEventListener('click', () => {
            const input = btn.parentElement.querySelector('input');
            const icon = btn.querySelector('.material-icons');
            if (!input || !icon) return;

            if (input.type === 'password') {
                input.type = 'text';
                icon.textContent = 'visibility_off';
            } else {
                input.type = 'password';
                icon.textContent = 'visibility';
            }
        });
    });
}


/**
 * Show field error
 */
function showFieldError(input, errorId) {
    input.classList.add('error');
    const errorEl = document.getElementById(errorId);
    if (errorEl) errorEl.classList.add('visible');
}


/**
 * Clear field error
 */
function clearFieldError(input, errorId) {
    input.classList.remove('error');
    const errorEl = document.getElementById(errorId);
    if (errorEl) errorEl.classList.remove('visible');
}


/**
 * Email validation regex
 */
function isValidEmail(email) {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
}
