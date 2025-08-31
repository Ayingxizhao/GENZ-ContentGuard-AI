document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('analysisForm');
    const resultsSection = document.getElementById('resultsSection');
    const loadingSection = document.getElementById('loadingSection');
    const errorSection = document.getElementById('errorSection');
    const analyzeBtn = document.querySelector('.analyze-btn');

    // Form submission handler
    form.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const title = document.getElementById('title').value.trim();
        const content = document.getElementById('content').value.trim();
        
        if (!content) {
            showError('Please enter some content to analyze.');
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
        
        // Disable button
        analyzeBtn.disabled = true;
        analyzeBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Analyzing...';
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
        if (data.is_malicious) {
            statusIndicator.classList.add('malicious');
            statusIndicator.innerHTML = '<i class="fas fa-exclamation-triangle"></i>';
            resultTitle.textContent = 'Malicious Content Detected';
            resultSubtitle.textContent = 'This content appears to contain harmful language';
        } else {
            statusIndicator.classList.add('safe');
            statusIndicator.innerHTML = '<i class="fas fa-check-circle"></i>';
            resultTitle.textContent = 'Content is Safe';
            resultSubtitle.textContent = 'No malicious content detected';
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
        analyzeBtn.innerHTML = '<i class="fas fa-search"></i> Analyze Content';
        
        // Scroll to results
        resultsSection.scrollIntoView({ behavior: 'smooth' });
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
        analyzeBtn.innerHTML = '<i class="fas fa-search"></i> Analyze Content';
        
        // Scroll to error
        errorSection.scrollIntoView({ behavior: 'smooth' });
    }

    // Add some interactive features
    const contentTextarea = document.getElementById('content');
    const titleInput = document.getElementById('title');
    
    // Auto-resize textarea
    contentTextarea.addEventListener('input', function() {
        this.style.height = 'auto';
        this.style.height = Math.max(120, this.scrollHeight) + 'px';
    });
    
    // Character counter for content
    contentTextarea.addEventListener('input', function() {
        const charCount = this.value.length;
        const maxChars = 5000; // Reasonable limit
        
        if (charCount > maxChars * 0.9) {
            this.style.borderColor = '#f56565';
        } else if (charCount > maxChars * 0.7) {
            this.style.borderColor = '#ed8936';
        } else {
            this.style.borderColor = '#e2e8f0';
        }
    });
    
    // Clear form when starting new analysis
    form.addEventListener('submit', function() {
        // Store values for potential retry
        window.lastAnalysis = {
            title: titleInput.value,
            content: contentTextarea.value
        };
    });
    
    // Add keyboard shortcuts
    document.addEventListener('keydown', function(e) {
        // Ctrl/Cmd + Enter to submit
        if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
            e.preventDefault();
            form.dispatchEvent(new Event('submit'));
        }
        
        // Escape to clear form
        if (e.key === 'Escape') {
            titleInput.value = '';
            contentTextarea.value = '';
            contentTextarea.style.height = '120px';
            contentTextarea.style.borderColor = '#e2e8f0';
            
            // Hide all sections
            resultsSection.style.display = 'none';
            loadingSection.style.display = 'none';
            errorSection.style.display = 'none';
        }
    });
    
    // Add helpful tooltips/info
    const contentLabel = document.querySelector('label[for="content"]');
    contentLabel.innerHTML += ' <span style="color: #718096; font-size: 0.8rem;">(Press Ctrl+Enter to analyze)</span>';
    
    // Add example button
    const exampleBtn = document.createElement('button');
    exampleBtn.type = 'button';
    exampleBtn.className = 'example-btn';
    exampleBtn.innerHTML = '<i class="fas fa-lightbulb"></i> Try Example';
    exampleBtn.style.cssText = `
        background: #edf2f7;
        color: #4a5568;
        border: 1px solid #e2e8f0;
        padding: 10px 20px;
        border-radius: 8px;
        font-size: 0.9rem;
        cursor: pointer;
        margin-top: 10px;
        transition: all 0.3s ease;
    `;
    
    exampleBtn.addEventListener('mouseenter', function() {
        this.style.background = '#e2e8f0';
    });
    
    exampleBtn.addEventListener('mouseleave', function() {
        this.style.background = '#edf2f7';
    });
    
    exampleBtn.addEventListener('click', function() {
        titleInput.value = 'Example Post';
        contentTextarea.value = 'This is an example of content that would be analyzed for malicious language. The AI will evaluate this text and provide a determination.';
        contentTextarea.style.height = 'auto';
        contentTextarea.style.height = Math.max(120, contentTextarea.scrollHeight) + 'px';
    });
    
    form.appendChild(exampleBtn);
});
