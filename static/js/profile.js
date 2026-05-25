/**
 * Jogja Smart Guide — Profile JS
 * Profile form handling and preference toggle
 */

document.addEventListener('DOMContentLoaded', () => {
    initProfileForm();
    initPasswordToggles();
    initProfileSliders();
});


/**
 * Profile form validation
 */
function initProfileForm() {
    const form = document.getElementById('profile-form');
    if (!form) return;

    form.addEventListener('submit', (e) => {
        const newPassword = document.getElementById('new_password');
        const confirmPassword = document.getElementById('confirm_password');

        if (newPassword.value) {
            // Only validate if user is trying to change password
            if (newPassword.value.length < 6) {
                e.preventDefault();
                alert('Password baru minimal 6 karakter.');
                newPassword.focus();
                return;
            }

            if (newPassword.value !== confirmPassword.value) {
                e.preventDefault();
                const errorEl = document.getElementById('confirm-password-error');
                if (errorEl) errorEl.classList.add('visible');
                confirmPassword.classList.add('error');
                confirmPassword.focus();
                return;
            }
        }
    });

    // Clear confirm password error on input
    const confirmPassword = document.getElementById('confirm_password');
    if (confirmPassword) {
        confirmPassword.addEventListener('input', () => {
            confirmPassword.classList.remove('error');
            const errorEl = document.getElementById('confirm-password-error');
            if (errorEl) errorEl.classList.remove('visible');
        });
    }
}


/**
 * Password visibility toggle (re-used from auth.js)
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
 * Initialize slider interactions in user profile
 */
function initProfileSliders() {
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

    // Attach event listeners & render initial values
    ['pref_nature', 'pref_culture', 'pref_culinary', 'pref_crowd', 'pref_effort'].forEach(id => {
        const slider = document.getElementById(id);
        if (slider) {
            slider.addEventListener('input', updateSliderBadges);
        }
    });

    updateSliderBadges();
}

