    const skeletonCard = document.getElementById('skeletonCard');
    const resultCard = document.getElementById('resultCard');

// Helper function to get or create rate limit handler
function getRateLimitHandler() {
    if (!window.rateLimitHandler && typeof RateLimitHandler !== 'undefined') {
        console.log('Creating rateLimitHandler on-demand...');
        window.rateLimitHandler = new RateLimitHandler();
    }
    return window.rateLimitHandler;
}

document.addEventListener('DOMContentLoaded', function() {
    // Initialize rate limit handler globally
    if (typeof RateLimitHandler !== 'undefined') {
        window.rateLimitHandler = new RateLimitHandler();
        console.log('✅ rateLimitHandler initialized:', window.rateLimitHandler);
    } else {
        console.error('❌ RateLimitHandler class not found!');
    }
    // Sticky nav blur on scroll
    const navEl = document.querySelector('.nav');
    function updateNavOnScroll() {
        if (!navEl) return;
        if (window.scrollY > 8) {
            navEl.classList.add('scrolled');
        } else {
            navEl.classList.remove('scrolled');
        }
    }
    updateNavOnScroll();
    window.addEventListener('scroll', updateNavOnScroll, { passive: true });
    // Theme toggle logic
    const themeToggle = document.getElementById('themeToggle');
    const root = document.documentElement;

    function applyTheme(theme) {
        if (theme === 'dark') {
            root.classList.add('dark');
            if (themeToggle) themeToggle.innerHTML = '<i class="fas fa-sun" aria-hidden="true"></i>';
        } else {
            root.classList.remove('dark');
            if (themeToggle) themeToggle.innerHTML = '<i class="fas fa-moon" aria-hidden="true"></i>';
        }
    }

    const savedTheme = localStorage.getItem('theme');
    if (savedTheme) {
        applyTheme(savedTheme);
    } else {
        const prefersDark = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
        applyTheme(prefersDark ? 'dark' : 'light');
    }

    if (themeToggle) {
        themeToggle.addEventListener('click', () => {
            const next = root.classList.contains('dark') ? 'light' : 'dark';
            localStorage.setItem('theme', next);
            applyTheme(next);
        });
    }

    const form = document.getElementById('analysisForm');
    const resultsSection = document.getElementById('resultsSection');
    const loadingSection = document.getElementById('loadingSection'); // may be null (removed)
    const errorSection = document.getElementById('errorSection');
    const analyzeBtn = document.querySelector('.analyze-btn');
    const exampleSafeBtn = document.getElementById('exampleSafeBtn');
    const exampleMaliciousBtn = document.getElementById('exampleMaliciousBtn');
    const contentTextarea = document.getElementById('content');
    const titleInput = document.getElementById('title');
    const charCounter = document.getElementById('content-counter');
    const charCount = charCounter.querySelector('.char-count');
    const progressBar = charCounter.querySelector('.progress-bar');
    const charLimit = charCounter.querySelector('.char-limit');
    // Skeleton/result cards (must be queried after DOM is ready)
    const skeletonCard = document.getElementById('skeletonCard');
    const resultCard = document.getElementById('resultCard');
    // Results UI elements
    const riskBadge = document.getElementById('riskBadge');
    const safeBar = document.getElementById('safeBar');
    const maliciousBar = document.getElementById('maliciousBar');
    const safeValue = document.getElementById('safeValue');
    const maliciousValue = document.getElementById('maliciousValue');
    const detailsToggle = document.getElementById('detailsToggle');
    const detailedAnalysisSection = document.getElementById('detailedAnalysis');
    // Third-party UI libs
    const aboutLink = document.getElementById('aboutLink');
    const aboutDialog = document.getElementById('aboutDialog');
    const menuToggle = document.getElementById('menuToggle');
    const mobileNav = document.getElementById('mobileNav');
    const aboutLinkDrawer = document.getElementById('aboutLinkDrawer');
    // Hero elements
    const heroCanvas = document.getElementById('heroCanvas');
    const demoSafeBar = document.getElementById('heroDemoSafe');
    const demoMalBar = document.getElementById('heroDemoMal');
    const demoSafeVal = document.getElementById('heroDemoSafeVal');
    const demoMalVal = document.getElementById('heroDemoMalVal');
    const demoBadge = document.getElementById('heroDemoBadge');

    // Ripple helper for buttons
    function createRipple(e, el) {
        if (!el) return;
        const rect = el.getBoundingClientRect();
        const ripple = document.createElement('span');
        ripple.className = 'ripple';
        ripple.style.left = `${e.clientX - rect.left}px`;
        ripple.style.top = `${e.clientY - rect.top}px`;
        el.appendChild(ripple);
        ripple.addEventListener('animationend', () => ripple.remove());
    }

    // Attach ripple to primary buttons
    [analyzeBtn, exampleSafeBtn, exampleMaliciousBtn].forEach(btn => {
        if (btn) {
            btn.addEventListener('click', (e) => createRipple(e, btn));
        }
    });

    // Initialize AOS (scroll animations) if available (basic init; full init on window load below)
    if (window.AOS) {
        AOS.init({ duration: 600, once: true, easing: 'ease-out-cubic' });
    }

    // Initialize Tippy tooltips if available
    if (window.tippy) {
        tippy('[data-tippy-content], [data-tippy]', { theme: 'light', delay: [100, 50], maxWidth: 260 });
    }

    // About link should scroll to the section at the end of the page. No dialog.
    // Desktop About link uses default anchor behavior; no JS needed.
    // Mobile drawer wiring
    if (menuToggle && mobileNav && typeof mobileNav.show === 'function') {
        menuToggle.addEventListener('click', () => mobileNav.show());
        // Close drawer on any nav link click
        mobileNav.addEventListener('click', (e) => {
            const a = e.target.closest('a');
            if (a) {
                if (typeof mobileNav.hide === 'function') mobileNav.hide();
            }
        });
    }
    if (aboutLinkDrawer && mobileNav) {
        aboutLinkDrawer.addEventListener('click', () => {
            // Let the anchor navigate to #about and close the drawer immediately after
            if (typeof mobileNav?.hide === 'function') setTimeout(() => mobileNav.hide(), 0);
        });
    }

    // Strengthen AOS init on full load to ensure layout settled (top-level, not inside other handlers)
    window.addEventListener('load', () => {
        if (window.AOS) {
            AOS.init({
                duration: 700,
                offset: 120,
                once: false,
                easing: 'ease-out-cubic'
            });
            setTimeout(() => AOS.refreshHard && AOS.refreshHard(), 50);
        }
    });

    // Details toggle behavior: click to show/hide the detailedAnalysis section
    if (detailsToggle && detailedAnalysisSection) {
        detailsToggle.addEventListener('click', () => {
            const isOpen = detailsToggle.getAttribute('aria-expanded') === 'true';
            const nextOpen = !isOpen;
            detailsToggle.setAttribute('aria-expanded', String(nextOpen));
            const label = detailsToggle.querySelector('span');
            if (label) label.textContent = nextOpen ? 'Hide details' : 'Show details';
            detailedAnalysisSection.style.display = nextOpen ? 'block' : 'none';
            if (window.AOS && typeof AOS.refresh === 'function') AOS.refresh();
        });
    }

    // =============================
    // Hero Canvas Particles (lightweight)
    // =============================
    const reduceMotion = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    if (heroCanvas && !reduceMotion) {
        const ctx = heroCanvas.getContext('2d');
        let width, height, particles, rafId;
        function resize() {
            width = heroCanvas.width = heroCanvas.offsetWidth;
            height = heroCanvas.height = heroCanvas.offsetHeight;
            initParticles();
        }
        function initParticles() {
            const count = Math.max(50, Math.floor(width * height / 25000));
            particles = new Array(count).fill(0).map(() => makeParticle());
        }
        function makeParticle() {
            const dark = root.classList.contains('dark') || (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches && !localStorage.getItem('theme'));
            const colors = dark ? ['#22d3ee55','#60a5fa55','#a78bfa55'] : ['#ffffff40','#93c5fd55','#fbbf2455'];
            return {
                x: Math.random() * width,
                y: Math.random() * height,
                r: Math.random() * 2 + 0.5,
                vx: (Math.random() - 0.5) * 0.25,
                vy: (Math.random() - 0.5) * 0.25,
                color: colors[Math.floor(Math.random()*colors.length)]
            };
        }
        function step() {
            ctx.clearRect(0,0,width,height);
            // draw
            particles.forEach(p => {
                p.x += p.vx;
                p.y += p.vy;
                if (p.x < -5) p.x = width+5; if (p.x > width+5) p.x = -5;
                if (p.y < -5) p.y = height+5; if (p.y > height+5) p.y = -5;
                ctx.beginPath();
                ctx.fillStyle = p.color;
                ctx.arc(p.x, p.y, p.r, 0, Math.PI*2);
                ctx.fill();
            });
            rafId = requestAnimationFrame(step);
        }
        const ro = new ResizeObserver(resize);
        ro.observe(heroCanvas);
        resize();
        step();
        // Update particle colors on theme toggle
        const applyThemeOriginal = applyTheme;
        applyTheme = function(theme) {
            applyThemeOriginal(theme);
            initParticles();
        };
        // Cleanup on unload
        window.addEventListener('beforeunload', () => cancelAnimationFrame(rafId));
    }

    // =============================
    // API Code Snippet Showcase
    // =============================
    const codeTabs = document.querySelectorAll('.code-tab');
    const codePanels = document.querySelectorAll('.code-panel');
    const copyCodeBtn = document.getElementById('copyCodeBtn');

    // Tab switching functionality
    codeTabs.forEach(tab => {
        tab.addEventListener('click', () => {
            const targetLang = tab.dataset.lang;
            
            // Update tabs
            codeTabs.forEach(t => {
                t.classList.remove('active');
                t.setAttribute('aria-selected', 'false');
            });
            tab.classList.add('active');
            tab.setAttribute('aria-selected', 'true');
            
            // Update panels with smooth transition
            codePanels.forEach(panel => {
                const panelLang = panel.id.replace('code-', '');
                if (panelLang === targetLang) {
                    panel.classList.add('active');
                    panel.removeAttribute('hidden');
                    // Re-highlight code with Prism if available
                    if (window.Prism) {
                        const codeBlock = panel.querySelector('code');
                        if (codeBlock) {
                            window.Prism.highlightElement(codeBlock);
                        }
                    }
                } else {
                    panel.classList.remove('active');
                    panel.setAttribute('hidden', '');
                }
            });
            
            // Announce to screen readers
            announceToScreenReader(`Switched to ${targetLang} code example`);
        });
    });

    // Copy to clipboard functionality
    if (copyCodeBtn) {
        copyCodeBtn.addEventListener('click', async () => {
            const activePanel = document.querySelector('.code-panel.active');
            if (!activePanel) return;
            
            const codeElement = activePanel.querySelector('code');
            if (!codeElement) return;
            
            const codeText = codeElement.textContent;
            
            try {
                // Use Clipboard API
                await navigator.clipboard.writeText(codeText);
                
                // Visual feedback with animation
                const originalHTML = copyCodeBtn.innerHTML;
                copyCodeBtn.innerHTML = '<i class="fas fa-check"></i>';
                copyCodeBtn.style.background = 'rgba(74, 222, 128, 0.3)';
                copyCodeBtn.classList.add('copied');
                
                // Show toast notification
                if (window.showToast) {
                    window.showToast('success', 'Code copied to clipboard!');
                }
                
                // Reset after 2 seconds
                setTimeout(() => {
                    copyCodeBtn.innerHTML = originalHTML;
                    copyCodeBtn.style.background = '';
                    copyCodeBtn.classList.remove('copied');
                }, 2000);
                
                // Announce to screen readers
                announceToScreenReader('Code copied to clipboard');
            } catch (err) {
                console.error('Failed to copy code:', err);
                if (window.showToast) {
                    window.showToast('danger', 'Failed to copy code');
                }
            }
        });
    }

    // Initialize Prism syntax highlighting on page load
    if (window.Prism) {
        window.addEventListener('load', () => {
            window.Prism.highlightAll();
        });
    }

    // =============================
    // Toast helper using Shoelace alerts
    // =============================
    window.showToast = function(type = 'primary', message = '') {
        const container = document.getElementById('toastContainer');
        if (!container || typeof customElements.get('sl-alert') === 'undefined') return;
        const alert = document.createElement('sl-alert');
        alert.variant = type; // 'primary' | 'success' | 'warning' | 'danger' | 'neutral'
        alert.closable = true;
        alert.innerHTML = `<sl-icon slot="icon" name="info-circle"></sl-icon>${message}`;
        container.appendChild(alert);
        // Show with animation
        requestAnimationFrame(() => alert.show());
        // Auto-hide after 4s
        setTimeout(() => { try { alert.hide(); } catch(e) {} }, 4000);
    };

    // Character counter functionality
    function updateCharCounter() {
        const count = contentTextarea.value.length;
        const maxChars = 5000;
        const percentage = (count / maxChars) * 100;
        
        charCount.textContent = `${count} character${count !== 1 ? 's' : ''}`;
        progressBar.style.width = `${percentage}%`;
        
        // Update counter styling based on usage
        charCounter.className = 'char-counter';
        if (percentage >= 90) {
            charCounter.classList.add('danger');
        } else if (percentage >= 70) {
            charCounter.classList.add('warning');
        }
        
        // Update aria-live for screen readers
        charCounter.setAttribute('aria-label', `${count} of ${maxChars} characters used`);
    }

    // Initialize character counter
    updateCharCounter();

    // Form submission handler
    form.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const title = titleInput.value.trim();
        const content = contentTextarea.value.trim();
        
        // Get selected model
        const modelSelect = document.getElementById('modelSelect');
        const selectedModel = modelSelect ? modelSelect.value : 'gemini';
        
        if (!content) {
            showError('Please enter some content to analyze.');
            return;
        }
        
        if (content.length > 5000) {
            showError('Content exceeds the maximum length of 5000 characters.');
            return;
        }
        
        // Show loading state
        showLoading();
        
        try {
            const response = await fetch('/analyze', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ 
                    title, 
                    content,
                    model: selectedModel
                })
            });
            
            const data = await response.json();
            
            if (!response.ok) {
                // Check if it's a rate limit error
                if (response.status === 429 && data.seconds_remaining) {
                    const handler = getRateLimitHandler();
                    if (handler) {
                        handler.handleRateLimitError(data);
                    } else {
                        console.error('rateLimitHandler not available!');
                        showError(data.hint || data.error);
                    }
                    return;
                }
                throw new Error(data.error || 'Analysis failed');
            }
            
            // Display rate limit info if available
            if (data.rate_limit) {
                const handler = getRateLimitHandler();
                if (handler) {
                    handler.displayRateLimitInfo(data.rate_limit);
                }
            }
            
            // Show results
            showResults(data);
            
        } catch (error) {
            console.error('Error:', error);
            showError(error.message || 'An error occurred during analysis. Please try again.');
        }
    });

    function showLoading() {
        // Hide error
        errorSection.style.display = 'none';
        // Show results shell and skeleton
        resultsSection.style.display = 'block';
        if (skeletonCard) skeletonCard.style.display = 'block';
        if (resultCard) resultCard.style.display = 'none';

        // Also keep global loading minimal or hidden (if present)
        if (loadingSection) loadingSection.style.display = 'none';

        // Disable button and update text
        analyzeBtn.disabled = true;
        analyzeBtn.innerHTML = '<i class="fas fa-spinner fa-spin" aria-hidden="true"></i><span>Analyzing...</span>';

        // Announce to screen readers
        announceToScreenReader('Analysis in progress. Please wait.');
    }

    function showResults(data) {
        // Hide loading, skeleton, and error sections
        if (loadingSection) loadingSection.style.display = 'none';
        errorSection.style.display = 'none';
        if (skeletonCard) skeletonCard.style.display = 'none';
        if (resultCard) {
            resultCard.style.display = 'block';
            // Trigger reveal animation
            resultCard.classList.remove('reveal-in');
            // force reflow for restart animation
            // eslint-disable-next-line no-unused-expressions
            resultCard.offsetHeight;
            resultCard.classList.add('reveal-in');
        }
        // Refresh AOS after DOM changes
        if (window.AOS && typeof AOS.refresh === 'function') {
            AOS.refresh();
        }
        
        // Update result elements
        const statusIndicator = document.getElementById('statusIndicator');
        const resultTitle = document.getElementById('resultTitle');
        const resultSubtitle = document.getElementById('resultSubtitle');
        const analysisText = document.getElementById('analysisText');
        const confidenceText = document.getElementById('confidenceText');
        const timestampText = document.getElementById('timestampText');
        const riskLevelText = document.getElementById('riskLevelText');
        const elementsScannedText = document.getElementById('elementsScannedText');
        
        // Set status indicator
        statusIndicator.className = 'status-indicator';
        let statusMessage = '';
        
        if (data.is_malicious) {
            statusIndicator.classList.add('malicious');
            statusIndicator.innerHTML = '<i class="fas fa-exclamation-triangle" aria-hidden="true"></i>';
            resultTitle.textContent = 'Malicious Content Detected';
            resultSubtitle.textContent = 'This content appears to contain harmful language';
            statusMessage = 'Malicious content detected';
            if (riskBadge) {
                riskBadge.className = 'badge malicious';
                riskBadge.textContent = 'Malicious';
            }
        } else {
            statusIndicator.classList.add('safe');
            statusIndicator.innerHTML = '<i class="fas fa-check-circle" aria-hidden="true"></i>';
            resultTitle.textContent = 'Content is Safe';
            resultSubtitle.textContent = 'No malicious content detected';
            statusMessage = 'Content is safe';
            if (riskBadge) {
                riskBadge.className = 'badge safe';
                riskBadge.textContent = 'Safe';
            }
        }
        
        // Update basic details
        analysisText.textContent = data.analysis;
        confidenceText.textContent = data.confidence;
        timestampText.textContent = data.timestamp;
        
        // Update detailed analysis info if available
        if (data.detailed_analysis && data.detailed_analysis.keyword_analysis) {
            riskLevelText.textContent = data.detailed_analysis.risk_level || 'N/A';
            elementsScannedText.textContent = data.detailed_analysis.elements_scanned || 'N/A';
            // Show detailed analysis section only when keyword_analysis exists
            showDetailedAnalysis(data.detailed_analysis);
        } else {
            riskLevelText.textContent = 'N/A';
            elementsScannedText.textContent = 'N/A';
            hideDetailedAnalysis();
        }
        
        // Show results
        resultsSection.style.display = 'block';
        
        // Re-enable button
        analyzeBtn.disabled = false;
        analyzeBtn.innerHTML = '<i class="fas fa-search" aria-hidden="true"></i><span>Analyze Content</span>';
        
        // Scroll to results
        resultsSection.scrollIntoView({ behavior: 'smooth' });
        
        // Announce to screen readers
        announceToScreenReader(`Analysis complete. ${statusMessage}. Confidence: ${data.confidence}`);

        // Update probability bars if available
        if (data.probabilities) {
            const parsePercent = (val) => {
                if (typeof val === 'number') return Math.max(0, Math.min(100, val));
                if (!val) return 0;
                const num = parseFloat(String(val).replace('%',''));
                return isNaN(num) ? 0 : Math.max(0, Math.min(100, num));
            };
            const safePct = parsePercent(data.probabilities.safe);
            const malPct = parsePercent(data.probabilities.malicious);
            if (safeBar) {
                if (safeBar.tagName && safeBar.tagName.toLowerCase() === 'sl-progress-bar') {
                    safeBar.value = safePct;
                } else {
                    safeBar.style.width = `${safePct}%`;
                }
            }
            if (maliciousBar) {
                if (maliciousBar.tagName && maliciousBar.tagName.toLowerCase() === 'sl-progress-bar') {
                    maliciousBar.value = malPct;
                } else {
                    maliciousBar.style.width = `${malPct}%`;
                }
            }
            // Count-up labels
            if (safeValue) animateValue(safeValue, 0, safePct, 700, '%');
            if (maliciousValue) animateValue(maliciousValue, 0, malPct, 700, '%');
        }

        // Optionally animate confidence number if formatted like "85.3%"
        const confNum = parseFloat(String(data.confidence).replace('%',''));
        if (!isNaN(confNum) && confidenceText) {
            animateValue(confidenceText, 0, confNum, 800, '%');
        }

        // Update risk badge variant/text if Shoelace badge is used
        if (riskBadge) {
            const isMal = data.is_malicious;
            try {
                const isSl = riskBadge.tagName && riskBadge.tagName.toLowerCase() === 'sl-badge';
                if (isMal === true) {
                    riskBadge.textContent = 'Malicious';
                    if (isSl) riskBadge.variant = 'danger';
                } else if (isMal === false) {
                    riskBadge.textContent = 'Safe';
                    if (isSl) riskBadge.variant = 'success';
                } else {
                    riskBadge.textContent = 'Pending';
                    if (isSl) riskBadge.variant = 'neutral';
                }
            } catch (e) { /* noop */ }
        }
        
        // Display explainability if available
        if (data.explainability && typeof ExplainabilityUI !== 'undefined') {
            const explainabilityContainer = document.getElementById('explainabilityContainer');
            if (explainabilityContainer) {
                const originalText = (titleInput.value + ' ' + contentTextarea.value).trim();
                ExplainabilityUI.renderExplainabilityPanel(
                    data.explainability,
                    originalText,
                    'explainabilityContainer'
                );
            }
        }
    }

    // Generic count-up animation
    function animateValue(el, start, end, duration, suffix = '') {
        const startTime = performance.now();
        function frame(now) {
            const t = Math.min(1, (now - startTime) / duration);
            // easeOutCubic
            const eased = 1 - Math.pow(1 - t, 3);
            const val = start + (end - start) * eased;
            el.textContent = `${val.toFixed(1)}${suffix}`;
            if (t < 1) requestAnimationFrame(frame);
        }
        requestAnimationFrame(frame);
    }

    function showDetailedAnalysis(detailedAnalysis) {
        const detailedAnalysisSection = document.getElementById('detailedAnalysis');
        const riskCategoriesList = document.getElementById('riskCategoriesList');
        const positiveElementsList = document.getElementById('positiveElementsList');
        const explanationText = document.getElementById('explanationText');
        
        // Clear previous content
        riskCategoriesList.innerHTML = '';
        positiveElementsList.innerHTML = '';
        
        // Populate risk categories
        const maliciousKeywords = detailedAnalysis.keyword_analysis.malicious_keywords;
        if (Object.keys(maliciousKeywords).length > 0) {
            Object.entries(maliciousKeywords).forEach(([category, keywords]) => {
                const categoryItem = createCategoryItem(category, keywords, 'risk');
                riskCategoriesList.appendChild(categoryItem);
            });
        } else {
            const noRiskItem = document.createElement('div');
            noRiskItem.className = 'category-item positive';
            noRiskItem.setAttribute('role', 'listitem');
            noRiskItem.innerHTML = '<div class="category-name">No risk categories detected</div>';
            riskCategoriesList.appendChild(noRiskItem);
        }
        
        // Populate positive elements
        const safeKeywords = detailedAnalysis.keyword_analysis.safe_keywords;
        if (Object.keys(safeKeywords).length > 0) {
            Object.entries(safeKeywords).forEach(([category, keywords]) => {
                const categoryItem = createCategoryItem(category, keywords, 'positive');
                positiveElementsList.appendChild(categoryItem);
            });
        } else {
            const noPositiveItem = document.createElement('div');
            noPositiveItem.className = 'category-item';
            noPositiveItem.setAttribute('role', 'listitem');
            noPositiveItem.innerHTML = '<div class="category-name">No positive elements detected</div>';
            positiveElementsList.appendChild(noPositiveItem);
        }
        
        // Set explanation text
        explanationText.innerHTML = detailedAnalysis.explanation.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
        
        // Show detailed analysis section
        detailedAnalysisSection.style.display = 'block';
    }

    function createCategoryItem(category, keywords, type) {
        const categoryItem = document.createElement('div');
        categoryItem.className = `category-item ${type}`;
        categoryItem.setAttribute('role', 'listitem');
        
        const categoryName = category.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
        const keywordsText = keywords.slice(0, 3).join(', ');
        const additionalCount = keywords.length > 3 ? keywords.length - 3 : 0;
        
        let keywordsDisplay = keywordsText;
        if (additionalCount > 0) {
            keywordsDisplay += ` (and ${additionalCount} more)`;
        }
        
        categoryItem.innerHTML = `
            <div class="category-name">${categoryName}</div>
            <div class="category-keywords">Keywords: ${keywordsDisplay}</div>
        `;
        
        return categoryItem;
    }

    function hideDetailedAnalysis() {
        const detailedAnalysisSection = document.getElementById('detailedAnalysis');
        detailedAnalysisSection.style.display = 'none';
    }

    function showError(message) {
        // Hide skeleton and loading, keep results shell hidden
        if (skeletonCard) skeletonCard.style.display = 'none';
        if (resultCard) resultCard.style.display = 'none';
        if (loadingSection) loadingSection.style.display = 'none';
        
        // Update error message
        document.getElementById('errorMessage').textContent = message;
        
        // Show error
        errorSection.style.display = 'block';
        
        // Re-enable button
        analyzeBtn.disabled = false;
        analyzeBtn.innerHTML = '<i class="fas fa-search" aria-hidden="true"></i><span>Analyze Content</span>';
        
        // Scroll to error
        errorSection.scrollIntoView({ behavior: 'smooth' });
        
        // Announce to screen readers
        announceToScreenReader(`Error: ${message}`);
    }

    // Screen reader announcement function
    function announceToScreenReader(message) {
        const announcement = document.createElement('div');
        announcement.setAttribute('aria-live', 'polite');
        announcement.setAttribute('aria-atomic', 'true');
        announcement.className = 'sr-only';
        announcement.textContent = message;
        
        document.body.appendChild(announcement);
        
        // Remove after announcement
        setTimeout(() => {
            document.body.removeChild(announcement);
        }, 1000);
    }

    // Auto-resize textarea
    contentTextarea.addEventListener('input', function() {
        // Skip direct height manipulation for Shoelace sl-textarea
        if (!this.tagName || this.tagName.toLowerCase() !== 'sl-textarea') {
            this.style.height = 'auto';
            this.style.height = Math.max(140, this.scrollHeight) + 'px';
        }
        updateCharCounter();
    });

    // Character counter for content
    contentTextarea.addEventListener('input', function() {
        updateCharCounter();
    });

    // Clear form when starting new analysis
    form.addEventListener('submit', function() {
        // Store values for potential retry
        window.lastAnalysis = {
            title: titleInput.value,
            content: contentTextarea.value
        };
    });

    // Example buttons functionality
    if (exampleSafeBtn) {
        exampleSafeBtn.addEventListener('click', function() {
            titleInput.value = 'Positive Community Post';
            contentTextarea.value = 'Hey everyone! Just a reminder to be kind to each other. If you need help or support, please reach out. We are here for you and we will get through this together.';
            if (!contentTextarea.tagName || contentTextarea.tagName.toLowerCase() !== 'sl-textarea') {
                contentTextarea.style.height = 'auto';
                contentTextarea.style.height = Math.max(140, contentTextarea.scrollHeight) + 'px';
            }
            updateCharCounter();
            contentTextarea.focus();
            announceToScreenReader('Safe example content loaded');
        });
    }

    if (exampleMaliciousBtn) {
        exampleMaliciousBtn.addEventListener('click', function() {
            titleInput.value = 'Toxic Comment';
            contentTextarea.value = "This post is full of insults and harassment. You're such an idiot—just leave and stop bothering people.";
            contentTextarea.style.height = 'auto';
            contentTextarea.style.height = Math.max(140, contentTextarea.scrollHeight) + 'px';
            updateCharCounter();
            contentTextarea.focus();
            announceToScreenReader('Malicious example content loaded');
        });
    }

    // Add keyboard shortcuts
    document.addEventListener('keydown', function(e) {
        // Ctrl/Cmd + Enter to submit
        if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
            e.preventDefault();
            if (!analyzeBtn.disabled) {
                form.dispatchEvent(new Event('submit'));
            }
        }
        
        // Escape to clear form
        if (e.key === 'Escape') {
            titleInput.value = '';
            contentTextarea.value = '';
            if (!contentTextarea.tagName || contentTextarea.tagName.toLowerCase() !== 'sl-textarea') {
                contentTextarea.style.height = '140px';
            }
            updateCharCounter();
            
            // Hide all sections
            resultsSection.style.display = 'none';
            loadingSection.style.display = 'none';
            errorSection.style.display = 'none';
            
            // Focus on content textarea
            contentTextarea.focus();
        }
    });

    // Add retry functionality
    function addRetryButton() {
        const retryBtn = document.createElement('button');
        retryBtn.type = 'button';
        retryBtn.className = 'example-btn';
        retryBtn.innerHTML = '<i class="fas fa-redo" aria-hidden="true"></i><span>Retry Analysis</span>';
        retryBtn.setAttribute('aria-label', 'Retry the last analysis');
        
        retryBtn.addEventListener('click', function() {
            if (window.lastAnalysis) {
                titleInput.value = window.lastAnalysis.title;
                contentTextarea.value = window.lastAnalysis.content;
                contentTextarea.style.height = 'auto';
                contentTextarea.style.height = Math.max(140, contentTextarea.scrollHeight) + 'px';
                updateCharCounter();
                
                // Submit form
                form.dispatchEvent(new Event('submit'));
            }
        });
        
        return retryBtn;
    }

    // Add retry button to error section (guard if legacy .error-card is missing)
    const errorCard = document.querySelector('.error-card');
    const retryBtn = addRetryButton();
    if (errorCard) {
        errorCard.appendChild(retryBtn);
    } else {
        // Fallback: append to errorSection if using <sl-alert>
        if (errorSection) errorSection.appendChild(retryBtn);
    }

    // Initialize focus management
    contentTextarea.focus();
    
    // Add form validation feedback
    form.addEventListener('invalid', function(e) {
        e.preventDefault();
        const invalidElement = e.target;
        invalidElement.focus();
        
        if (invalidElement === contentTextarea) {
            showError('Please enter content to analyze.');
        }
    }, true);

    // Add loading state for better UX (skeleton only). Keep timeout logic safe if loadingSection is absent
    let loadingTimeout;
    form.addEventListener('submit', function() {
        loadingTimeout = setTimeout(() => {
            if (loadingSection && loadingSection.style.display === 'block') {
                const p = loadingSection.querySelector('p');
                if (p) p.textContent = 'This may take a few moments...';
            }
        }, 2000);
    });

    // Clear timeout when results are shown
    const originalShowResults = showResults;
    showResults = function(data) {
        clearTimeout(loadingTimeout);
        originalShowResults(data);
    };

    const originalShowError = showError;
    showError = function(message) {
        clearTimeout(loadingTimeout);
        originalShowError(message);
    };

    // Smooth scrolling for navigation links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });

    // Add intersection observer for animations
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    }, observerOptions);

    // Observe elements for animation
    document.querySelectorAll('.feature-card, .result-card, .breakdown-section').forEach(el => {
        el.style.opacity = '0';
        el.style.transform = 'translateY(20px)';
        el.style.transition = 'opacity 0.6s ease-out, transform 0.6s ease-out';
        observer.observe(el);
    });

    // (removed legacy inner-sections toggle; replaced by container-level toggle above)

    // Bug Report Form Functionality (only if form exists on page)
    const bugReportForm = document.getElementById('bugReportForm');
    const bugReportMessages = document.getElementById('bugReportMessages');
    const bugMessageCard = document.getElementById('bugMessageCard');
    const bugMessageText = document.getElementById('bugMessageText');
    const clearBugFormBtn = document.getElementById('clearBugForm');
    const bugDescriptionTextarea = document.getElementById('bugDescription');
    const bugDescCounter = document.getElementById('bug-desc-counter');

    if (bugReportForm && bugDescriptionTextarea && bugDescCounter) {
        const bugDescCharCount = bugDescCounter.querySelector('.char-count');
        const bugDescProgressBar = bugDescCounter.querySelector('.progress-bar');

        // Bug report character counter
        function updateBugCharCounter() {
            const count = bugDescriptionTextarea.value.length;
            const maxChars = 10000;
            const percentage = (count / maxChars) * 100;
            
            bugDescCharCount.textContent = `${count} character${count !== 1 ? 's' : ''}`;
            bugDescProgressBar.style.width = `${percentage}%`;
            
            // Update counter styling based on usage
            bugDescCounter.className = 'char-counter';
            if (percentage >= 90) {
                bugDescCounter.classList.add('danger');
            } else if (percentage >= 70) {
                bugDescCounter.classList.add('warning');
            }
            
            // Update aria-live for screen readers
            bugDescCounter.setAttribute('aria-label', `${count} of ${maxChars} characters used`);
        }

        // Initialize bug report character counter
        updateBugCharCounter();

        // Bug report form submission
        bugReportForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const formData = new FormData(bugReportForm);
            const bugData = Object.fromEntries(formData.entries());
            
            // Add browser info automatically
            bugData.browser_info = bugData.browser_info || navigator.userAgent;
            bugData.user_agent = navigator.userAgent;
            bugData.url_where_bug_occurred = window.location.href;
            
            try {
                showBugMessage('Submitting bug report...', 'info');
                const response = await fetch('/api/bug-report', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(bugData)
                });
                if (response.ok) {
                    showBugMessage('Bug report submitted successfully! Thank you for helping us improve.', 'success');
                    bugReportForm.reset();
                    updateBugCharCounter();
                } else {
                    showBugMessage('Failed to submit bug report.', 'error');
                }
            } catch (error) {
                showBugMessage('Network error. Please check your connection and try again.', 'error');
            }
        });

        // Clear bug report form
        if (clearBugFormBtn) {
            clearBugFormBtn.addEventListener('click', function() {
                bugReportForm.reset();
                updateBugCharCounter();
                hideBugMessage();
            });
        }

        // Show bug report message
        function showBugMessage(message, type) {
            if (!bugMessageText || !bugMessageCard || !bugReportMessages) return;
            
            bugMessageText.textContent = message;
            bugMessageCard.className = `message-card ${type}`;
            
            // Update icon based on type
            const icon = bugMessageCard.querySelector('i');
            if (icon) {
                icon.className = 'fas';
                switch(type) {
                    case 'success':
                        icon.classList.add('fa-check-circle');
                        break;
                    case 'error':
                        icon.classList.add('fa-exclamation-triangle');
                        break;
                    case 'info':
                    default:
                        icon.classList.add('fa-info-circle');
                        break;
                }
            }
            
            bugReportMessages.style.display = 'block';
            
            // Auto-hide success messages after 5 seconds
            if (type === 'success') {
                setTimeout(() => {
                    hideBugMessage();
                }, 5000);
            }
        }

        // Hide bug report message
        function hideBugMessage() {
            if (bugReportMessages) {
                bugReportMessages.style.display = 'none';
            }
        }

        // Add event listener for bug description character counter
        bugDescriptionTextarea.addEventListener('input', updateBugCharCounter);
    }

    // =============================
    // Authentication State Management
    // =============================
    const loginBtn = document.getElementById('loginBtn');
    const loginDialog = document.getElementById('loginDialog');
    const userDropdown = document.getElementById('userDropdown');
    const userAvatar = document.getElementById('userAvatar');
    const userName = document.getElementById('userName');
    const usageCount = document.getElementById('usageCount');
    const usageLimit = document.getElementById('usageLimit');
    const logoutMenuItem = document.getElementById('logoutMenuItem');

    // Drawer elements
    const drawerLoginBtn = document.getElementById('drawerLoginBtn');
    const drawerAccount = document.getElementById('drawerAccount');
    const drawerUserAvatar = document.getElementById('drawerUserAvatar');
    const drawerUserName = document.getElementById('drawerUserName');
    const drawerUsageCount = document.getElementById('drawerUsageCount');
    const drawerUsageLimit = document.getElementById('drawerUsageLimit');
    const drawerLogoutBtn = document.getElementById('drawerLogoutBtn');
    const drawerThemeToggle = document.getElementById('drawerThemeToggle');

    // Check authentication status on page load
    async function checkAuthStatus() {
        try {
            const response = await fetch('/auth/user');
            const data = await response.json();
            
            if (data.authenticated && data.user) {
                // User is logged in
                showUserProfile(data.user);
                updateDrawerAuth(data.user);
                // Start polling for usage stats
                startUsageStatsPolling();
            } else {
                // User is not logged in
                showLoginButton();
                updateDrawerAuth(null);
                // Stop polling if it was running
                stopUsageStatsPolling();
            }
        } catch (error) {
            console.error('Failed to check auth status:', error);
            showLoginButton();
            stopUsageStatsPolling();
        }
    }

    function showLoginButton() {
        if (loginBtn) {
            loginBtn.style.display = 'inline-flex';
        }
        if (userDropdown) {
            userDropdown.style.display = 'none';
        }
        // Show and update anonymous usage banner
        showAnonymousUsageBanner();
        fetchAndUpdateAnonymousUsage();
    }

    function showUserProfile(user) {
        if (loginBtn) {
            loginBtn.style.display = 'none';
        }
        if (userDropdown) {
            userDropdown.style.display = 'inline-block';
        }

        // Update user info
        if (userAvatar) {
            if (user.avatar_url) {
                userAvatar.src = user.avatar_url;
                userAvatar.alt = user.name || user.email;
            } else {
                // Generate avatar from initials for email/password users
                const initials = (user.name || user.email).charAt(0).toUpperCase();
                userAvatar.src = `https://ui-avatars.com/api/?name=${encodeURIComponent(user.name || user.email)}&background=18181b&color=fafafa&size=128`;
                userAvatar.alt = user.name || user.email;
            }
        }
        if (userName) {
            userName.textContent = user.name || user.email.split('@')[0];
        }
        
        // Hide anonymous banner when logged in
        hideAnonymousUsageBanner();
        // Stop any running anonymous timers
        stopGeminiCooldownTimer();
        
        // Fetch and display detailed usage stats
        fetchAndUpdateUsageStats();
    }
    
    // Fetch detailed usage stats from API
    async function fetchAndUpdateUsageStats() {
        try {
            const response = await fetch('/api/usage');
            const data = await response.json();
            
            if (data.authenticated && data.stats) {
                updateDetailedUsageDisplay(data.stats);
            }
        } catch (error) {
            console.error('Failed to fetch usage stats:', error);
        }
    }
    
    // Update the detailed usage panel with stats
    function updateDetailedUsageDisplay(stats) {
        // Update HuggingFace stats
        const hfUsageCount = document.getElementById('hfUsageCount');
        const hfUsageLimit = document.getElementById('hfUsageLimit');
        const hfUsagePercentage = document.getElementById('hfUsagePercentage');
        const hfProgressFill = document.getElementById('hfProgressFill');
        const hfRemaining = document.getElementById('hfRemaining');
        
        if (stats.huggingface) {
            const hf = stats.huggingface;
            if (hfUsageCount) hfUsageCount.textContent = hf.calls_today;
            if (hfUsageLimit) hfUsageLimit.textContent = hf.daily_limit;
            if (hfUsagePercentage) hfUsagePercentage.textContent = `${hf.percentage_used}%`;
            if (hfRemaining) hfRemaining.textContent = hf.remaining;
            
            if (hfProgressFill) {
                hfProgressFill.style.width = `${hf.percentage_used}%`;
                // Update color based on usage
                hfProgressFill.className = 'usage-progress-fill';
                if (hf.percentage_used >= 90) {
                    hfProgressFill.classList.add('danger');
                } else if (hf.percentage_used >= 70) {
                    hfProgressFill.classList.add('warning');
                }
            }
        }
        
        // Update Gemini stats
        const geminiUsageCount = document.getElementById('geminiUsageCount');
        const geminiUsageLimit = document.getElementById('geminiUsageLimit');
        const geminiUsagePercentage = document.getElementById('geminiUsagePercentage');
        const geminiProgressFill = document.getElementById('geminiProgressFill');
        const geminiRemaining = document.getElementById('geminiRemaining');
        
        if (stats.gemini) {
            const gemini = stats.gemini;
            if (geminiUsageCount) geminiUsageCount.textContent = gemini.calls_today;
            if (geminiUsageLimit) geminiUsageLimit.textContent = gemini.daily_limit;
            if (geminiUsagePercentage) geminiUsagePercentage.textContent = `${gemini.percentage_used}%`;
            if (geminiRemaining) geminiRemaining.textContent = gemini.remaining;
            
            if (geminiProgressFill) {
                geminiProgressFill.style.width = `${gemini.percentage_used}%`;
                // Update color based on usage
                geminiProgressFill.className = 'usage-progress-fill';
                if (gemini.percentage_used >= 90) {
                    geminiProgressFill.classList.add('danger');
                } else if (gemini.percentage_used >= 70) {
                    geminiProgressFill.classList.add('warning');
                }
            }
        }
        
        // Update reset timer
        if (stats.seconds_until_reset) {
            updateResetTimer(stats.seconds_until_reset);
        }
        
        // Update total lifetime usage
        const totalLifetimeUsage = document.getElementById('totalLifetimeUsage');
        if (totalLifetimeUsage && stats.huggingface && stats.gemini) {
            const total = stats.huggingface.total_calls + stats.gemini.total_calls;
            totalLifetimeUsage.textContent = total.toLocaleString();
        }
    }
    
    // Update reset timer display
    function updateResetTimer(secondsRemaining) {
        const resetTimer = document.getElementById('resetTimer');
        if (!resetTimer) return;
        
        const hours = Math.floor(secondsRemaining / 3600);
        const minutes = Math.floor((secondsRemaining % 3600) / 60);
        const seconds = secondsRemaining % 60;
        
        const timeStr = `${String(hours).padStart(2, '0')}:${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;
        resetTimer.textContent = `Resets in ${timeStr}`;
    }
    
    // Start periodic polling for usage stats (every 30 seconds)
    let usageStatsInterval = null;
    function startUsageStatsPolling() {
        // Clear any existing interval
        if (usageStatsInterval) {
            clearInterval(usageStatsInterval);
        }
        
        // Poll every 30 seconds
        usageStatsInterval = setInterval(() => {
            fetchAndUpdateUsageStats();
        }, 30000);
    }
    
    // Stop polling when user logs out
    function stopUsageStatsPolling() {
        if (usageStatsInterval) {
            clearInterval(usageStatsInterval);
            usageStatsInterval = null;
        }
    }
    
    // =============================
    // Anonymous User Usage Tracking
    // =============================
    const anonymousUsageBanner = document.getElementById('anonymousUsageBanner');
    const closeBannerBtn = document.getElementById('closeBannerBtn');
    
    // Show anonymous usage banner
    function showAnonymousUsageBanner() {
        // Check if user has closed the banner before (localStorage)
        const bannerClosed = localStorage.getItem('anonBannerClosed');
        if (!bannerClosed && anonymousUsageBanner) {
            anonymousUsageBanner.style.display = 'block';
        }
    }
    
    // Hide anonymous usage banner
    function hideAnonymousUsageBanner() {
        if (anonymousUsageBanner) {
            anonymousUsageBanner.style.display = 'none';
        }
    }
    
    // Close banner button handler
    if (closeBannerBtn) {
        closeBannerBtn.addEventListener('click', () => {
            hideAnonymousUsageBanner();
            // Stop any running timers
            stopGeminiCooldownTimer();
            // Remember user preference
            localStorage.setItem('anonBannerClosed', 'true');
        });
    }
    
    // Fetch and update anonymous usage stats
    async function fetchAndUpdateAnonymousUsage() {
        try {
            const response = await fetch('/api/usage');
            const data = await response.json();
            
            console.log('[Anonymous Usage] API Response:', data);
            
            if (!data.authenticated && data.stats) {
                console.log('[Anonymous Usage] Updating display with stats:', data.stats);
                updateAnonymousUsageDisplay(data.stats);
            } else {
                console.log('[Anonymous Usage] User is authenticated, skipping anonymous display');
            }
        } catch (error) {
            console.error('[Anonymous Usage] Failed to fetch:', error);
        }
    }
    
    // Gemini cooldown timer management
    let geminiCooldownInterval = null;
    let geminiCooldownEndTime = null;
    
    // Start Gemini cooldown countdown timer
    function startGeminiCooldownTimer(secondsRemaining) {
        // Stop any existing timer
        stopGeminiCooldownTimer();
        
        // Calculate end time
        geminiCooldownEndTime = Date.now() + (secondsRemaining * 1000);
        
        // Update immediately
        updateGeminiCooldownDisplay();
        
        // Update every second
        geminiCooldownInterval = setInterval(() => {
            updateGeminiCooldownDisplay();
        }, 1000);
        
        console.log('[Gemini Cooldown] Timer started, ends in', secondsRemaining, 'seconds');
    }
    
    // Stop Gemini cooldown timer
    function stopGeminiCooldownTimer() {
        if (geminiCooldownInterval) {
            clearInterval(geminiCooldownInterval);
            geminiCooldownInterval = null;
            geminiCooldownEndTime = null;
            console.log('[Gemini Cooldown] Timer stopped');
        }
    }
    
    // Update Gemini cooldown display
    function updateGeminiCooldownDisplay() {
        const anonCooldownTime = document.getElementById('anonCooldownTime');
        
        if (!geminiCooldownEndTime || !anonCooldownTime) {
            return;
        }
        
        const now = Date.now();
        const remaining = Math.max(0, Math.floor((geminiCooldownEndTime - now) / 1000));
        
        if (remaining <= 0) {
            // Cooldown expired
            stopGeminiCooldownTimer();
            // Refresh usage to show "available" state
            fetchAndUpdateAnonymousUsage();
            return;
        }
        
        const minutes = Math.floor(remaining / 60);
        const seconds = remaining % 60;
        anonCooldownTime.textContent = `${minutes}m ${seconds}s`;
    }
    
    // Update anonymous usage display
    function updateAnonymousUsageDisplay(stats) {
        console.log('[Anonymous Usage] Updating display...');
        
        // Update HuggingFace stats
        const anonHfUsed = document.getElementById('anonHfUsed');
        const anonHfLimit = document.getElementById('anonHfLimit');
        const anonHfRemaining = document.getElementById('anonHfRemaining');
        const anonHfProgressFill = document.getElementById('anonHfProgressFill');
        
        if (stats.huggingface) {
            const hf = stats.huggingface;
            console.log('[Anonymous Usage] HF Stats:', hf);
            
            if (anonHfUsed) anonHfUsed.textContent = hf.calls_today;
            if (anonHfLimit) anonHfLimit.textContent = hf.daily_limit;
            if (anonHfRemaining) anonHfRemaining.textContent = `${hf.remaining} remaining`;
            
            if (anonHfProgressFill) {
                const percentage = hf.percentage_used || 0;
                anonHfProgressFill.style.width = `${percentage}%`;
                
                // Update color based on usage
                anonHfProgressFill.className = 'anon-progress-fill';
                if (percentage >= 90) {
                    anonHfProgressFill.classList.add('danger');
                } else if (percentage >= 70) {
                    anonHfProgressFill.classList.add('warning');
                }
                
                console.log('[Anonymous Usage] Progress bar updated:', percentage + '%');
            }
        }
        
        // Update Gemini cooldown info
        const anonGeminiInfo = document.getElementById('anonGeminiInfo');
        const anonGeminiCooldown = document.getElementById('anonGeminiCooldown');
        
        if (stats.gemini) {
            const gemini = stats.gemini;
            console.log('[Anonymous Usage] Gemini Stats:', gemini);
            
            if (gemini.cooldown_active) {
                // Show cooldown with countdown timer
                if (anonGeminiInfo) anonGeminiInfo.style.display = 'none';
                if (anonGeminiCooldown) anonGeminiCooldown.style.display = 'flex';
                
                // Start countdown timer
                if (gemini.seconds_remaining > 0) {
                    startGeminiCooldownTimer(gemini.seconds_remaining);
                }
            } else {
                // Show available
                if (anonGeminiInfo) anonGeminiInfo.style.display = 'flex';
                if (anonGeminiCooldown) anonGeminiCooldown.style.display = 'none';
                
                // Stop countdown timer if running
                stopGeminiCooldownTimer();
                
                console.log('[Anonymous Usage] Gemini available');
            }
        }
    }

    function updateDrawerAuth(user) {
        if (user && drawerAccount && drawerLoginBtn) {
            drawerLoginBtn.style.display = 'none';
            drawerAccount.style.display = 'block';
            if (drawerUserAvatar) {
                if (user.avatar_url) {
                    drawerUserAvatar.src = user.avatar_url;
                    drawerUserAvatar.alt = user.name || user.email;
                } else {
                    // Generate avatar from initials for email/password users
                    drawerUserAvatar.src = `https://ui-avatars.com/api/?name=${encodeURIComponent(user.name || user.email)}&background=18181b&color=fafafa&size=128`;
                    drawerUserAvatar.alt = user.name || user.email;
                }
            }
            if (drawerUserName) drawerUserName.textContent = user.name || (user.email ? user.email.split('@')[0] : 'User');
            if (drawerUsageCount) drawerUsageCount.textContent = user.api_calls_today || 0;
            if (drawerUsageLimit) drawerUsageLimit.textContent = user.daily_limit || 200;
        } else {
            if (drawerLoginBtn) drawerLoginBtn.style.display = 'flex';
            if (drawerAccount) drawerAccount.style.display = 'none';
        }
    }

    // Open login page
    if (loginBtn) {
        loginBtn.addEventListener('click', () => {
            window.location.href = '/auth/login';
        });
    }

    // Drawer: open login page
    if (drawerLoginBtn) {
        drawerLoginBtn.addEventListener('click', () => {
            window.location.href = '/auth/login';
        });
    }

    // Logout handler
    if (logoutMenuItem) {
        logoutMenuItem.addEventListener('click', async () => {
            stopUsageStatsPolling();
            try {
                const response = await fetch('/auth/logout');
                if (response.redirected) {
                    window.location.href = response.url;
                } else {
                    window.location.reload();
                }
            } catch (error) {
                console.error('Logout failed:', error);
                window.location.href = '/auth/logout';
            }
        });
    }

    // Drawer: logout
    if (drawerLogoutBtn) {
        drawerLogoutBtn.addEventListener('click', async () => {
            stopUsageStatsPolling();
            try {
                const response = await fetch('/auth/logout');
                if (typeof mobileNav?.hide === 'function') mobileNav.hide();
                if (response.redirected) {
                    window.location.href = response.url;
                } else {
                    window.location.reload();
                }
            } catch (error) {
                console.error('Logout failed:', error);
                window.location.href = '/auth/logout';
            }
        });
    }

    // Drawer: theme toggle mirrors main toggle
    if (drawerThemeToggle) {
        drawerThemeToggle.addEventListener('click', () => {
            const next = root.classList.contains('dark') ? 'light' : 'dark';
            localStorage.setItem('theme', next);
            applyTheme(next);
            if (typeof mobileNav?.hide === 'function') mobileNav.hide();
        });
    }

    // Check for auth errors in URL
    const urlParams = new URLSearchParams(window.location.search);
    if (urlParams.get('error') === 'auth_failed') {
        if (window.showToast) {
            window.showToast('danger', 'Authentication failed. Please try again.');
        }
        // Clean up URL
        window.history.replaceState({}, document.title, window.location.pathname);
    }

    // Initialize auth state
    checkAuthStatus();

    // Refresh usage stats after each analysis
    if (typeof showResults === 'function') {
        const authOriginalShowResults = showResults;
        showResults = function(data) {
            authOriginalShowResults(data);
            
            console.log('[Usage Stats] Refreshing after API call');
            
            // Fetch fresh usage stats after analysis
            // The endpoint will return appropriate data based on auth status
            fetchAndUpdateUsageStats();
            fetchAndUpdateAnonymousUsage();
        };
    }

    // ========================================
    // URL ANALYSIS FUNCTIONALITY
    // ========================================

    // Input mode toggle
    const urlModeBtn = document.getElementById('urlModeBtn');
    const manualModeBtn = document.getElementById('manualModeBtn');
    const urlInputSection = document.getElementById('urlInputSection');
    const manualInputSection = document.getElementById('manualInputSection');
    const urlAnalysisForm = document.getElementById('urlAnalysisForm');
    const urlResultsSection = document.getElementById('urlResultsSection');

    // Toggle between URL and Manual input modes
    if (urlModeBtn && manualModeBtn) {
        urlModeBtn.addEventListener('click', function() {
            // Activate URL mode
            urlModeBtn.classList.add('active');
            urlModeBtn.setAttribute('aria-selected', 'true');
            manualModeBtn.classList.remove('active');
            manualModeBtn.setAttribute('aria-selected', 'false');

            urlInputSection.style.display = 'block';
            urlInputSection.classList.add('active');
            manualInputSection.style.display = 'none';
            manualInputSection.classList.remove('active');

            // Hide results sections
            if (resultsSection) resultsSection.style.display = 'none';
            if (urlResultsSection) urlResultsSection.style.display = 'none';
        });

        manualModeBtn.addEventListener('click', function() {
            // Activate Manual mode
            manualModeBtn.classList.add('active');
            manualModeBtn.setAttribute('aria-selected', 'true');
            urlModeBtn.classList.remove('active');
            urlModeBtn.setAttribute('aria-selected', 'false');

            manualInputSection.style.display = 'block';
            manualInputSection.classList.add('active');
            urlInputSection.style.display = 'none';
            urlInputSection.classList.remove('active');

            // Hide results sections
            if (resultsSection) resultsSection.style.display = 'none';
            if (urlResultsSection) urlResultsSection.style.display = 'none';
        });
    }

    // URL Analysis Form Submission
    if (urlAnalysisForm) {
        urlAnalysisForm.addEventListener('submit', async function(e) {
            e.preventDefault();

            const urlInput = document.getElementById('url');
            const url = urlInput.value.trim();

            if (!url) {
                showError('Please enter a URL to analyze.');
                return;
            }

            // Show loading state
            showURLLoading();

            try {
                const response = await fetch('/analyze-url', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ url })
                });

                const data = await response.json();

                if (!response.ok) {
                    throw new Error(data.error || 'URL analysis failed');
                }

                // Show URL results
                showURLResults(data);

            } catch (error) {
                console.error('Error:', error);
                showError(error.message || 'An error occurred during URL analysis. Please try again.');
                hideURLLoading();
            }
        });
    }

    // Example Reddit button
    const exampleRedditBtn = document.getElementById('exampleRedditBtn');
    if (exampleRedditBtn) {
        exampleRedditBtn.addEventListener('click', function() {
            const urlInput = document.getElementById('url');
            // Use a safe example Reddit post
            urlInput.value = 'https://reddit.com/r/wholesomememes/comments/1234567/example/';
            createRipple(event, exampleRedditBtn);
        });
    }

    function showURLLoading() {
        // Hide error and regular results
        if (errorSection) errorSection.style.display = 'none';
        if (resultsSection) resultsSection.style.display = 'none';

        // Show URL results section in loading state
        if (urlResultsSection) {
            urlResultsSection.style.display = 'block';

            // Show progress bar
            const progressContainer = document.getElementById('progressContainer');
            if (progressContainer) {
                progressContainer.style.display = 'block';

                // Debug: Check if Lottie player exists
                const lottieAnimation = document.getElementById('lottieAnimation');
                console.log('Lottie player element:', lottieAnimation);
                if (lottieAnimation) {
                    console.log('Lottie player src:', lottieAnimation.getAttribute('src'));
                }

                updateProgress(0, 'Scraping URL...', 'scraping');

                // Smooth scroll to progress bar after a tiny delay (so it's visible first)
                setTimeout(() => {
                    progressContainer.scrollIntoView({
                        behavior: 'smooth',
                        block: 'center'
                    });
                }, 100);
            }

            // Hide summary and cards during loading
            const summaryBanner = document.getElementById('summaryBanner');
            const postCard = document.getElementById('postCard');
            const commentsSection = document.getElementById('commentsSection');
            if (summaryBanner) summaryBanner.style.display = 'none';
            if (postCard) postCard.style.display = 'none';
            if (commentsSection) commentsSection.style.display = 'none';
        }

        // Disable submit button
        const urlSubmitBtn = urlAnalysisForm.querySelector('.analyze-btn');
        if (urlSubmitBtn) {
            urlSubmitBtn.disabled = true;
            urlSubmitBtn.innerHTML = '<i class="fas fa-spinner fa-spin" aria-hidden="true"></i><span>Analyzing...</span>';
        }

        // Simulate progress updates
        simulateProgress();

        announceToScreenReader('URL analysis in progress. Please wait.');
    }

    function updateProgress(percentage, text, phase) {
        // Use Motion-powered progress if available
        if (typeof updateProgressWithMotion !== 'undefined') {
            updateProgressWithMotion(percentage, text, phase);
        }

        const progressBar = document.getElementById('urlProgressBar');
        const progressText = document.getElementById('progressText');
        const progressPercentage = document.getElementById('progressPercentage');
        const scrapingStatus = document.getElementById('scrapingStatus');
        const postStatus = document.getElementById('postStatus');
        const commentsStatus = document.getElementById('commentsStatus');

        if (progressBar) progressBar.value = percentage;
        if (progressText) progressText.textContent = text;
        if (progressPercentage) progressPercentage.textContent = `${Math.round(percentage)}%`;

        // Update phase-specific statuses
        if (phase === 'scraping') {
            if (scrapingStatus) {
                scrapingStatus.textContent = 'In Progress';
                scrapingStatus.className = 'status-active';
            }
        } else if (phase === 'post') {
            if (scrapingStatus) {
                scrapingStatus.textContent = 'Complete';
                scrapingStatus.className = 'status-complete';
            }
            if (postStatus) {
                postStatus.textContent = 'Analyzing';
                postStatus.className = 'status-active';
            }
        } else if (phase === 'comments') {
            if (postStatus) {
                postStatus.textContent = 'Complete';
                postStatus.className = 'status-complete';
            }
        } else if (phase === 'complete') {
            if (commentsStatus) {
                commentsStatus.className = 'status-complete';
            }
        }
    }

    function simulateProgress() {
        // Simulate scraping phase (0-30%)
        let progress = 0;
        const scrapingInterval = setInterval(() => {
            progress += Math.random() * 10;
            if (progress >= 30) {
                progress = 30;
                clearInterval(scrapingInterval);
                updateProgress(progress, 'Analyzing post...', 'post');

                // Simulate post analysis (30-60%)
                const postInterval = setInterval(() => {
                    progress += Math.random() * 8;
                    if (progress >= 60) {
                        progress = 60;
                        clearInterval(postInterval);
                        updateProgress(progress, 'Analyzing comments...', 'comments');

                        // Simulate comment counting (60-95%)
                        let commentCount = 0;
                        const commentInterval = setInterval(() => {
                            progress += Math.random() * 5;
                            commentCount += Math.floor(Math.random() * 3);
                            const commentsStatus = document.getElementById('commentsStatus');
                            if (commentsStatus) {
                                commentsStatus.textContent = `${commentCount}/~20`;
                                commentsStatus.className = 'status-active';
                            }
                            if (progress >= 95) {
                                clearInterval(commentInterval);
                                updateProgress(95, 'Finalizing...', 'comments');
                            } else {
                                updateProgress(progress, 'Analyzing comments...', 'comments');
                            }
                        }, 300);
                    } else {
                        updateProgress(progress, 'Analyzing post...', 'post');
                    }
                }, 200);
            } else {
                updateProgress(progress, 'Scraping URL...', 'scraping');
            }
        }, 150);
    }

    function hideURLLoading() {
        const urlSubmitBtn = urlAnalysisForm.querySelector('.analyze-btn');
        if (urlSubmitBtn) {
            urlSubmitBtn.disabled = false;
            urlSubmitBtn.innerHTML = '<i class="fas fa-search" aria-hidden="true"></i><span>Analyze URL</span>';
        }
    }

    function showURLResults(data) {
        if (!urlResultsSection) return;

        // Display analysis status if available
        if (data.analysis_status && typeof displayAnalysisStatus === 'function') {
            displayAnalysisStatus(data.analysis_status);
        }

        // Complete progress to 100%
        const commentsStatus = document.getElementById('commentsStatus');
        if (commentsStatus) {
            commentsStatus.textContent = `${data.comments.length}/${data.summary.total_comments}`;
        }
        updateProgress(100, 'Analysis complete!', 'complete');

        // Wait a moment before hiding progress bar
        setTimeout(() => {
            const progressContainer = document.getElementById('progressContainer');
            if (progressContainer) {
                progressContainer.style.display = 'none';
            }

            // Show summary and cards
            const summaryBanner = document.getElementById('summaryBanner');
            const postCard = document.getElementById('postCard');
            const commentsSection = document.getElementById('commentsSection');
            if (summaryBanner) summaryBanner.style.display = 'flex';
            if (postCard) postCard.style.display = 'block';
            if (commentsSection) commentsSection.style.display = 'block';
        }, 800);

        // Hide loading state
        hideURLLoading();

        // Remove loading class
        const postCard = document.getElementById('postCard');
        if (postCard) {
            postCard.classList.remove('loading');
        }

        // Update summary banner
        document.getElementById('totalAnalyzed').textContent = data.summary.total_analyzed;
        document.getElementById('safeCount').textContent = data.summary.safe_count;
        document.getElementById('maliciousCount').textContent = data.summary.malicious_count;

        // Show cache indicator if cached
        const cacheIndicator = document.getElementById('cacheIndicator');
        if (cacheIndicator) {
            cacheIndicator.style.display = data.cached ? 'flex' : 'none';
        }

        // Update post card
        updatePostCard(data.post);

        // Update comments section
        updateCommentsSection(data.comments, data.summary);

        // Show truncated notice if needed
        const truncatedNotice = document.getElementById('truncatedNotice');
        if (truncatedNotice && data.summary.comments_truncated) {
            truncatedNotice.style.display = 'flex';
            document.getElementById('extractedCount').textContent = data.summary.extracted_comments;
            document.getElementById('totalCommentsCount').textContent = data.summary.total_comments;
        } else if (truncatedNotice) {
            truncatedNotice.style.display = 'none';
        }

        // Show results section
        urlResultsSection.style.display = 'block';

        // Scroll to results
        urlResultsSection.scrollIntoView({ behavior: 'smooth' });

        // Announce to screen readers
        const maliciousCount = data.summary.malicious_count;
        const statusMessage = maliciousCount > 0
            ? `Found ${maliciousCount} malicious item${maliciousCount > 1 ? 's' : ''}`
            : 'All content appears safe';
        announceToScreenReader(`Analysis complete. ${statusMessage}.`);

        // Refresh AOS animations
        if (window.AOS && typeof AOS.refresh === 'function') {
            AOS.refresh();
        }
    }

    function updatePostCard(post) {
        const postTitle = document.getElementById('postTitle');
        const postContent = document.getElementById('postContent');
        const postAuthor = document.getElementById('postAuthor');
        const postScore = document.getElementById('postScore');
        const postRiskBadge = document.getElementById('postRiskBadge');
        const postConfidence = document.getElementById('postConfidence');
        const postAnalysis = document.getElementById('postAnalysis');
        const postCard = document.getElementById('postCard');

        if (postTitle) postTitle.textContent = post.title || 'No title';
        if (postContent) postContent.textContent = post.content || '[No content]';
        if (postAuthor) postAuthor.textContent = post.author || '[deleted]';
        if (postScore) postScore.textContent = post.score || 0;

        // Update analysis
        const analysis = post.analysis;
        if (analysis) {
            if (postConfidence) postConfidence.textContent = analysis.confidence || 'N/A';
            if (postAnalysis) postAnalysis.textContent = analysis.analysis || 'N/A';

            // Update risk badge
            if (postRiskBadge) {
                if (analysis.is_malicious) {
                    postRiskBadge.variant = 'danger';
                    postRiskBadge.textContent = 'Malicious';
                    if (postCard) postCard.classList.add('malicious');
                } else {
                    postRiskBadge.variant = 'success';
                    postRiskBadge.textContent = 'Safe';
                    if (postCard) postCard.classList.remove('malicious');
                }
            }
        }
    }

    function updateCommentsSection(comments, summary) {
        const commentsList = document.getElementById('commentsList');
        const commentsCount = document.getElementById('commentsCount');

        if (commentsCount) {
            commentsCount.textContent = comments.length;
        }

        if (!commentsList) return;

        // Clear existing comments
        commentsList.innerHTML = '';

        if (comments.length === 0) {
            commentsList.innerHTML = '<div class="no-comments"><i class="fas fa-inbox"></i><p>No comments found</p></div>';
            return;
        }

        // Create comment cards
        comments.forEach((comment, index) => {
            const commentCard = createCommentCard(comment, index);
            commentsList.appendChild(commentCard);
        });

        // Setup filter button
        setupCommentFilter(comments);
    }

    function createCommentCard(comment, index) {
        const card = document.createElement('div');
        card.className = 'comment-card';
        card.dataset.index = index;
        card.dataset.isMalicious = comment.analysis.is_malicious;

        // Add depth indicator
        const depthClass = `depth-${Math.min(comment.depth, 3)}`;
        card.classList.add(depthClass);

        if (comment.analysis.is_malicious) {
            card.classList.add('malicious');
        }

        card.innerHTML = `
            <div class="comment-header">
                <div class="comment-author">
                    <i class="fas fa-user"></i>
                    <span>${comment.author || '[deleted]'}</span>
                    ${comment.depth > 0 ? `<span class="depth-badge">Depth ${comment.depth}</span>` : ''}
                </div>
                <sl-badge variant="${comment.analysis.is_malicious ? 'danger' : 'success'}">
                    ${comment.analysis.is_malicious ? 'Malicious' : 'Safe'}
                </sl-badge>
            </div>
            <div class="comment-content">
                <p>${escapeHtml(comment.content)}</p>
            </div>
            <div class="comment-analysis">
                <span class="analysis-label">Confidence:</span>
                <span class="analysis-value">${comment.analysis.confidence || 'N/A'}</span>
                ${comment.score ? `<span class="comment-score"><i class="fas fa-arrow-up"></i> ${comment.score}</span>` : ''}
            </div>
        `;

        return card;
    }

    function setupCommentFilter(comments) {
        const filterBtn = document.getElementById('filterMaliciousBtn');
        if (!filterBtn) return;

        let showMaliciousOnly = false;

        filterBtn.addEventListener('click', function() {
            showMaliciousOnly = !showMaliciousOnly;
            filterBtn.setAttribute('aria-pressed', showMaliciousOnly);

            const commentCards = document.querySelectorAll('.comment-card');
            commentCards.forEach(card => {
                if (showMaliciousOnly) {
                    const isMalicious = card.dataset.isMalicious === 'true';
                    card.style.display = isMalicious ? 'block' : 'none';
                } else {
                    card.style.display = 'block';
                }
            });

            // Update button text
            const btnText = filterBtn.querySelector('span');
            if (btnText) {
                btnText.textContent = showMaliciousOnly ? 'Show all comments' : 'Show malicious only';
            }

            // Update icon
            const icon = filterBtn.querySelector('i');
            if (icon) {
                icon.className = showMaliciousOnly ? 'fas fa-filter-circle-xmark' : 'fas fa-filter';
            }
        });
    }

    function escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    function announceToScreenReader(message) {
        // Create or use existing live region for screen readers
        let liveRegion = document.getElementById('sr-live-region');
        if (!liveRegion) {
            liveRegion = document.createElement('div');
            liveRegion.id = 'sr-live-region';
            liveRegion.className = 'sr-only';
            liveRegion.setAttribute('aria-live', 'polite');
            liveRegion.setAttribute('aria-atomic', 'true');
            document.body.appendChild(liveRegion);
        }
        liveRegion.textContent = message;
    }
});
