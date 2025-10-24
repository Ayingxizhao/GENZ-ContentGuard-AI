/**
 * Modern Animations with Motion (Framer Motion for Web)
 * 2025 Gen Z UX Enhancements
 */

// Safe Motion wrapper to handle errors
window.safeMotionAnimate = function(element, keyframes, options) {
    if (typeof Motion === 'undefined') return null;
    try {
        return Motion.animate(element, keyframes, options);
    } catch (e) {
        console.warn('Motion animation failed:', e);
        return null;
    }
};

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    initMotionAnimations();
    initMicroInteractions();
    initProgressAnimations();
    initBackToTop();
});

/**
 * Initialize Motion-powered animations
 */
function initMotionAnimations() {
    // Check if Motion library is loaded
    if (typeof Motion === 'undefined') {
        console.warn('Motion library not loaded, using fallback animations');
        return;
    }

    // Hero section entrance animation
    const heroLeft = document.querySelector('.hero-left');
    const heroRight = document.querySelector('.hero-right');

    if (heroLeft) {
        Motion.animate(heroLeft,
            { opacity: [0, 1], x: [-50, 0] },
            { duration: 0.8, easing: [0.22, 1, 0.36, 1] }
        );
    }

    if (heroRight) {
        Motion.animate(heroRight,
            { opacity: [0, 1], x: [50, 0] },
            { duration: 0.8, delay: 0.2, easing: [0.22, 1, 0.36, 1] }
        );
    }

    // Animate feature cards on scroll
    const featureCards = document.querySelectorAll('.feature-card');
    if (featureCards.length > 0 && Motion.inView) {
        featureCards.forEach((card, index) => {
            Motion.inView(card, () => {
                Motion.animate(card,
                    { opacity: [0, 1], y: [30, 0] },
                    { duration: 0.6, delay: index * 0.1, easing: [0.22, 1, 0.36, 1] }
                );
            }, { amount: 0.3 });
        });
    }

    // Animate stats on scroll
    const stats = document.querySelectorAll('.stat');
    if (stats.length > 0 && Motion.inView) {
        stats.forEach((stat, index) => {
            Motion.inView(stat, () => {
                Motion.animate(stat,
                    { opacity: [0, 1], scale: [0.8, 1] },
                    { duration: 0.5, delay: index * 0.15, easing: 'spring' }
                );

                // Animate numbers
                const statNumber = stat.querySelector('.stat-number');
                if (statNumber) {
                    const targetValue = parseFloat(statNumber.textContent);
                    Motion.animate(
                        (progress) => {
                            statNumber.textContent = (targetValue * progress).toFixed(1) + '%';
                        },
                        { duration: 1.5, delay: index * 0.15 + 0.2 }
                    );
                }
            }, { amount: 0.5 });
        });
    }

    // Animate input sections
    const inputSections = document.querySelectorAll('.input-section, .results-section');
    if (inputSections.length > 0 && Motion.inView) {
        inputSections.forEach((section) => {
            Motion.inView(section, () => {
                Motion.animate(section,
                    { opacity: [0, 1], y: [20, 0] },
                    { duration: 0.6, easing: [0.22, 1, 0.36, 1] }
                );
            }, { amount: 0.2 });
        });
    }
}

/**
 * Micro-interactions for enhanced UX
 */
function initMicroInteractions() {
    // Enhanced button hover effects with Motion
    const buttons = document.querySelectorAll('.cta-primary, .cta-secondary, .example-btn, .toggle-btn');

    buttons.forEach(button => {
        button.addEventListener('mouseenter', function(e) {
            if (typeof Motion !== 'undefined') {
                Motion.animate(this,
                    { scale: 1.05 },
                    { duration: 0.2, easing: 'ease-out' }
                );
            }
        });

        button.addEventListener('mouseleave', function(e) {
            if (typeof Motion !== 'undefined') {
                Motion.animate(this,
                    { scale: 1 },
                    { duration: 0.2, easing: 'ease-out' }
                );
            }
        });

        button.addEventListener('mousedown', function(e) {
            if (typeof Motion !== 'undefined') {
                Motion.animate(this,
                    { scale: 0.95 },
                    { duration: 0.1 }
                );
            }
        });

        button.addEventListener('mouseup', function(e) {
            if (typeof Motion !== 'undefined') {
                Motion.animate(this,
                    { scale: 1.05 },
                    { duration: 0.1 }
                );
            }
        });
    });

    // Floating animation for blobs
    const blobs = document.querySelectorAll('.blob');
    blobs.forEach((blob, index) => {
        if (typeof Motion !== 'undefined') {
            Motion.animate(blob,
                {
                    x: [0, 20, -20, 0],
                    y: [0, -30, 30, 0],
                },
                {
                    duration: 8 + index * 2,
                    repeat: Infinity,
                    easing: 'ease-in-out'
                }
            );
        }
    });

    // Ripple effect for primary buttons (enhanced)
    const analyzeButtons = document.querySelectorAll('.analyze-btn, sl-button');
    analyzeButtons.forEach(btn => {
        btn.addEventListener('click', function(e) {
            createEnhancedRipple(e, this);
        });
    });

    // Input focus animations
    const inputs = document.querySelectorAll('sl-input, sl-textarea');
    inputs.forEach(input => {
        input.addEventListener('focus', function() {
            if (typeof Motion !== 'undefined') {
                const base = this.shadowRoot?.querySelector('.input__control') || this;
                Motion.animate(base,
                    { boxShadow: ['0 0 0 0 rgba(102, 126, 234, 0)', '0 0 0 4px rgba(102, 126, 234, 0.1)'] },
                    { duration: 0.3 }
                );
            }
        });
    });

    // Card hover effects
    const cards = document.querySelectorAll('.result-card, .url-result-card, .feature-card');
    cards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            if (typeof Motion !== 'undefined') {
                Motion.animate(this,
                    { y: -8, boxShadow: 'var(--neo-shadow-light-hover)' },
                    { duration: 0.3, easing: [0.22, 1, 0.36, 1] }
                );
            }
        });

        card.addEventListener('mouseleave', function() {
            if (typeof Motion !== 'undefined') {
                Motion.animate(this,
                    { y: 0, boxShadow: 'var(--neo-shadow-light)' },
                    { duration: 0.3, easing: [0.22, 1, 0.36, 1] }
                );
            }
        });
    });
}

/**
 * Enhanced ripple effect
 */
function createEnhancedRipple(e, element) {
    const ripple = document.createElement('span');
    ripple.className = 'ripple';

    const rect = element.getBoundingClientRect();
    const size = Math.max(rect.width, rect.height);
    const x = e.clientX - rect.left - size / 2;
    const y = e.clientY - rect.top - size / 2;

    ripple.style.width = ripple.style.height = size + 'px';
    ripple.style.left = x + 'px';
    ripple.style.top = y + 'px';

    element.style.position = 'relative';
    element.style.overflow = 'hidden';
    element.appendChild(ripple);

    if (typeof Motion !== 'undefined') {
        try {
            const animation = Motion.animate(ripple,
                { scale: [0, 4], opacity: [0.6, 0] },
                { duration: 0.6, easing: 'ease-out' }
            );
            // Check if animation has finished property
            if (animation && animation.finished) {
                animation.finished.then(() => ripple.remove());
            } else {
                setTimeout(() => ripple.remove(), 600);
            }
        } catch (e) {
            console.warn('Motion animation failed:', e);
            setTimeout(() => ripple.remove(), 600);
        }
    } else {
        setTimeout(() => ripple.remove(), 600);
    }
}

/**
 * Modern Progress Bar Animations (replacing Lottie)
 */
function initProgressAnimations() {
    const motionAnimation = document.getElementById('motionAnimation');
    if (!motionAnimation) return;

    console.log('Motion animation initialized');

    // Add entrance animation when element is shown
    const progressContainer = document.getElementById('progressContainer');
    if (progressContainer && typeof Motion !== 'undefined') {
        // Observe when progressContainer becomes visible
        const observer = new MutationObserver((mutations) => {
            mutations.forEach((mutation) => {
                if (mutation.type === 'attributes' && mutation.attributeName === 'style') {
                    const isVisible = progressContainer.style.display === 'block';
                    if (isVisible) {
                        // Animate entrance
                        Motion.animate(motionAnimation,
                            { opacity: [0, 1], scale: [0.8, 1] },
                            { duration: 0.5, easing: [0.22, 1, 0.36, 1] }
                        );
                    }
                }
            });
        });

        observer.observe(progressContainer, { attributes: true });
    }
}

/**
 * Update progress with Motion animation
 */
window.updateProgressWithMotion = function(percentage, text, phase) {
    const progressBar = document.getElementById('urlProgressBar');
    const progressText = document.getElementById('progressText');
    const progressPercentage = document.getElementById('progressPercentage');
    const motionCircle = document.querySelector('.motion-circle-progress');
    const motionIcon = document.querySelector('.motion-icon i');

    if (progressBar) progressBar.value = percentage;
    if (progressText) progressText.textContent = text;
    if (progressPercentage) progressPercentage.textContent = Math.round(percentage) + '%';

    // Animate circular progress
    if (motionCircle && typeof Motion !== 'undefined') {
        // Calculate circle circumference (2 * π * r, where r = 60)
        const circumference = 2 * Math.PI * 60; // 377
        const offset = circumference - (percentage / 100) * circumference;

        Motion.animate(motionCircle,
            { strokeDashoffset: offset },
            { duration: 0.8, easing: [0.22, 1, 0.36, 1] }
        );
    }

    // Change icon based on phase
    if (motionIcon) {
        const icons = {
            scraping: 'fa-globe',
            post: 'fa-file-alt',
            comments: 'fa-comments',
            complete: 'fa-check-circle'
        };

        const newIcon = icons[phase];
        if (newIcon && !motionIcon.classList.contains(newIcon)) {
            motionIcon.className = 'fas ' + newIcon;

            // Pulse animation on icon change
            if (typeof Motion !== 'undefined') {
                Motion.animate(motionIcon.parentElement,
                    { scale: [1, 1.3, 1] },
                    { duration: 0.5, easing: [0.22, 1, 0.36, 1] }
                );
            }
        }
    }
};


/**
 * Animate result cards entrance
 */
window.animateResultsEntrance = function() {
    const resultsSection = document.getElementById('resultsSection') || document.getElementById('urlResultsSection');
    if (!resultsSection) return;

    if (typeof Motion !== 'undefined') {
        Motion.animate(resultsSection,
            { opacity: [0, 1], y: [30, 0] },
            { duration: 0.6, easing: [0.22, 1, 0.36, 1] }
        );

        // Animate individual cards with stagger
        const cards = resultsSection.querySelectorAll('.result-card, .url-result-card');
        cards.forEach((card, index) => {
            Motion.animate(card,
                { opacity: [0, 1], y: [20, 0] },
                { duration: 0.5, delay: index * 0.1, easing: [0.22, 1, 0.36, 1] }
            );
        });
    }
};

/**
 * Smooth theme transition
 */
const themeToggle = document.getElementById('themeToggle');
if (themeToggle) {
    themeToggle.addEventListener('click', function() {
        if (typeof Motion !== 'undefined') {
            const root = document.documentElement;
            Motion.animate(root,
                { opacity: [1, 0.95, 1] },
                { duration: 0.3 }
            );
        }
    });
}

/**
 * Back to Top Button and Navigation Links
 */
function initBackToTop() {
    const backToTopBtn = document.getElementById('backToTop');

    // Show/hide button based on scroll position
    function updateBackToTopVisibility() {
        if (!backToTopBtn) return;
        // Show button if scrolled more than 300px (lowered from 500px)
        if (window.scrollY > 300) {
            backToTopBtn.classList.add('show');
        } else {
            backToTopBtn.classList.remove('show');
        }
    }

    // Scroll to top function for back-to-top button only
    function scrollToTop(e) {
        if (e) e.preventDefault();

        console.log('Back to top clicked');

        // Simple scroll to top
        window.scrollTo({
            top: 0,
            behavior: 'smooth'
        });

        // Add click animation
        if (backToTopBtn && typeof Motion !== 'undefined') {
            Motion.animate(backToTopBtn,
                { scale: [1, 0.9, 1] },
                { duration: 0.2 }
            );
        }
    }

    // Attach to back-to-top button
    if (backToTopBtn) {
        backToTopBtn.addEventListener('click', scrollToTop);
        // Listen to scroll events
        window.addEventListener('scroll', updateBackToTopVisibility, { passive: true });
        // Initial check
        updateBackToTopVisibility();
    }

    // Attach to all Home/hero-section navigation links
    // NOTE: Let browser handle the scroll natively, just close drawer if needed
    const heroLinks = document.querySelectorAll('a[href="#hero-section"]');
    heroLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            console.log('Home link clicked');

            // Close mobile drawer if open, but DON'T prevent default scroll
            const mobileNav = document.getElementById('mobileNav');
            if (mobileNav && typeof mobileNav.hide === 'function') {
                mobileNav.hide();
            }

            // Let the browser handle the scroll natively (don't preventDefault)
        });
    });

    // Handle "See Examples" link - add a back link
    const seeExamplesLink = document.querySelector('a[href="#examples"]');
    if (seeExamplesLink) {
        console.log('See Examples link found:', seeExamplesLink);

        // Add event to show back-to-top button immediately when clicking See Examples
        seeExamplesLink.addEventListener('click', function(e) {
            console.log('See Examples clicked');

            // Show back-to-top button immediately
            setTimeout(() => {
                if (backToTopBtn) {
                    backToTopBtn.classList.add('show');
                }

                // Add a helper tooltip
                if (backToTopBtn && !backToTopBtn.dataset.tooltipShown) {
                    backToTopBtn.dataset.tooltipShown = 'true';

                    // Pulse animation to draw attention
                    if (typeof Motion !== 'undefined') {
                        Motion.animate(backToTopBtn,
                            { scale: [1, 1.2, 1, 1.2, 1] },
                            { duration: 1, delay: 0.5 }
                        );
                    }
                }
            }, 800); // After scroll completes
        });
    }
}
