/**
 * Jogja Smart Guide — Main JS
 * Shared utilities, navbar scroll effect, avatar dropdown toggle
 */

document.addEventListener('DOMContentLoaded', () => {
    initNavbarScroll();
    initAvatarDropdown();
    initFlashMessages();
});


/**
 * Navbar scroll effect — add 'scrolled' class on scroll
 */
function initNavbarScroll() {
    const navbar = document.getElementById('navbar');
    if (!navbar) return;

    // Skip if navbar already has 'solid' class (non-landing pages)
    if (navbar.classList.contains('solid')) return;

    function handleScroll() {
        if (window.scrollY > 50) {
            navbar.classList.add('scrolled');
        } else {
            navbar.classList.remove('scrolled');
        }
    }

    window.addEventListener('scroll', handleScroll, { passive: true });
    handleScroll(); // Initial check
}


/**
 * Avatar dropdown toggle
 */
function initAvatarDropdown() {
    const avatarBtn = document.getElementById('avatar-btn');
    const avatarDropdown = document.getElementById('avatar-dropdown');
    if (!avatarBtn || !avatarDropdown) return;

    avatarBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        avatarDropdown.classList.toggle('active');
    });

    // Close dropdown when clicking outside
    document.addEventListener('click', (e) => {
        if (!avatarDropdown.contains(e.target) && e.target !== avatarBtn) {
            avatarDropdown.classList.remove('active');
        }
    });

    // Close on Escape key
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
            avatarDropdown.classList.remove('active');
        }
    });
}


/**
 * Auto-dismiss flash messages after 5 seconds
 */
function initFlashMessages() {
    const flashMessages = document.querySelectorAll('.flash-message');
    flashMessages.forEach((msg, index) => {
        setTimeout(() => {
            msg.style.transition = 'opacity 0.3s ease, transform 0.3s ease';
            msg.style.opacity = '0';
            msg.style.transform = 'translateX(20px)';
            setTimeout(() => msg.remove(), 300);
        }, 5000 + (index * 500));
    });
}


/**
 * Format currency to Indonesian Rupiah
 */
function formatRupiah(amount) {
    if (amount === 0) return 'Gratis';
    return 'Rp ' + amount.toLocaleString('id-ID');
}
