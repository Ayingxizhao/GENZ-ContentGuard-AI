document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('analysisForm');
    const resultsSection = document.getElementById('resultsSection');
    const loadingSection = document.getElementById('loadingSection');
    const errorSection = document.getElementById('errorSection');
    const analyzeBtn = document.querySelector('.analyze-btn');
    const exampleBtn = document.getElementById('exampleBtn');
    const contentTextarea = document.getElementById('content');
    const titleInput = document.getElementById('title');
    const charCounter = document.getElementById('content-counter');
    const charCount = charCounter.querySelector('.char-count');
    const progressBar = charCounter.querySelector('.progress-bar');
    const charLimit = charCounter.querySelector('.char-limit');

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
                body: JSON.stringify({ title, content })
            });
            
            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.error || 'Analysis failed');
            }
            
            // Show results
            showResults(data);
            
        } catch (error) {
            console.error('Error:', error);
            showError(error.message || 'An error occurred during analysis. Please try again.');
        }
    });

    function showLoading() {
        // Hide other sections
        resultsSection.style.display = 'none';
        errorSection.style.display = 'none';
        
        // Show loading
        loadingSection.style.display = 'block';
        
        // Disable button and update text
        analyzeBtn.disabled = true;
        analyzeBtn.innerHTML = '<i class="fas fa-spinner fa-spin" aria-hidden="true"></i><span>Analyzing...</span>';
        
        // Announce to screen readers
        announceToScreenReader('Analysis in progress. Please wait.');
    }

    function showResults(data) {
        // Hide loading and error sections
        loadingSection.style.display = 'none';
        errorSection.style.display = 'none';
        
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
        } else {
            statusIndicator.classList.add('safe');
            statusIndicator.innerHTML = '<i class="fas fa-check-circle" aria-hidden="true"></i>';
            resultTitle.textContent = 'Content is Safe';
            resultSubtitle.textContent = 'No malicious content detected';
            statusMessage = 'Content is safe';
        }
        
        // Update basic details
        analysisText.textContent = data.analysis;
        confidenceText.textContent = data.confidence;
        timestampText.textContent = data.timestamp;
        
        // Update detailed analysis info if available
        if (data.detailed_analysis) {
            riskLevelText.textContent = data.detailed_analysis.risk_level;
            elementsScannedText.textContent = data.detailed_analysis.elements_scanned;
            
            // Show detailed analysis section
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
        // Hide other sections
        resultsSection.style.display = 'none';
        loadingSection.style.display = 'none';
        
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
        this.style.height = 'auto';
        this.style.height = Math.max(140, this.scrollHeight) + 'px';
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

    // Example button functionality
    exampleBtn.addEventListener('click', function() {
        titleInput.value = 'Example Post';
        contentTextarea.value = 'This is an example of content that would be analyzed for malicious language. The AI will evaluate this text and provide a determination.';
        contentTextarea.style.height = 'auto';
        contentTextarea.style.height = Math.max(140, contentTextarea.scrollHeight) + 'px';
        updateCharCounter();
        
        // Focus on content textarea
        contentTextarea.focus();
        
        // Announce to screen readers
        announceToScreenReader('Example content loaded');
    });

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
            contentTextarea.style.height = '140px';
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

    // Add retry button to error section
    const errorCard = document.querySelector('.error-card');
    const retryBtn = addRetryButton();
    errorCard.appendChild(retryBtn);

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

    // Add loading state for better UX
    let loadingTimeout;
    form.addEventListener('submit', function() {
        // Set a minimum loading time for better UX
        loadingTimeout = setTimeout(() => {
            if (loadingSection.style.display === 'block') {
                loadingSection.querySelector('p').textContent = 'This may take a few moments...';
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

    // Bug Report Form Functionality
    const bugReportForm = document.getElementById('bugReportForm');
    const bugReportMessages = document.getElementById('bugReportMessages');
    const bugMessageCard = document.getElementById('bugMessageCard');
    const bugMessageText = document.getElementById('bugMessageText');
    const clearBugFormBtn = document.getElementById('clearBugForm');
    const bugDescriptionTextarea = document.getElementById('bugDescription');
    const bugDescCounter = document.getElementById('bug-desc-counter');
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
            
            const response = await fetch('/api/bug-reports/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(bugData)
            });
            
            const result = await response.json();
            
            if (response.ok) {
                showBugMessage('Bug report submitted successfully! Thank you for helping us improve.', 'success');
                bugReportForm.reset();
                updateBugCharCounter();
            } else {
                showBugMessage(`Error: ${result.error || 'Failed to submit bug report'}`, 'error');
            }
        } catch (error) {
            showBugMessage('Network error. Please check your connection and try again.', 'error');
        }
    });

    // Clear bug report form
    clearBugFormBtn.addEventListener('click', function() {
        bugReportForm.reset();
        updateBugCharCounter();
        hideBugMessage();
    });

    // Show bug report message
    function showBugMessage(message, type) {
        bugMessageText.textContent = message;
        bugMessageCard.className = `message-card ${type}`;
        
        // Update icon based on type
        const icon = bugMessageCard.querySelector('i');
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
        bugReportMessages.style.display = 'none';
    }

    // Add event listener for bug description character counter
    bugDescriptionTextarea.addEventListener('input', updateBugCharCounter);
});
