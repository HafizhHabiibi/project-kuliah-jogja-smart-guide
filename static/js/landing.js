/**
 * Jogja Smart Guide — Landing Page JS
 * Intersection Observer for scroll reveal animations
 */

document.addEventListener('DOMContentLoaded', () => {
    initScrollReveal();
    initParallaxHero();
});


/**
 * Scroll reveal animations using Intersection Observer
 */
function initScrollReveal() {
    const revealElements = document.querySelectorAll('.reveal');

    if (!revealElements.length) return;

    const observer = new IntersectionObserver((entries) => {
        entries.forEach((entry, index) => {
            if (entry.isIntersecting) {
                // Add staggered delay
                setTimeout(() => {
                    entry.target.classList.add('revealed');
                }, index * 100);
                observer.unobserve(entry.target);
            }
        });
    }, {
        threshold: 0.15,
        rootMargin: '0px 0px -50px 0px'
    });

    revealElements.forEach((el) => {
        observer.observe(el);
    });
}


/**
 * Subtle parallax effect on hero background
 */
function initParallaxHero() {
    const heroBg = document.querySelector('.hero-bg img');
    if (!heroBg) return;

    window.addEventListener('scroll', () => {
        const scrollY = window.scrollY;
        const heroHeight = document.querySelector('.hero').offsetHeight;

        if (scrollY < heroHeight) {
            const translateY = scrollY * 0.3;
            heroBg.style.transform = `translateY(${translateY}px) scale(1.1)`;
        }
    }, { passive: true });

    // Set initial scale
    heroBg.style.transform = 'scale(1.1)';
    heroBg.style.transition = 'transform 0.1s linear';
}
