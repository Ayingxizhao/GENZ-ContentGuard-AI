/**
 * Explainability UI Module
 * Handles visualization of toxic phrase highlights and category breakdowns
 */

const ExplainabilityUI = {
    /**
     * Render highlighted text with toxic phrases marked
     * @param {string} text - Original text
     * @param {Array} phrases - Array of highlighted phrase objects
     * @param {string} containerId - ID of container element
     */
    renderHighlightedText(text, phrases, containerId) {
        const container = document.getElementById(containerId);
        if (!container) {
            console.error(`Container ${containerId} not found`);
            return;
        }

        if (!phrases || phrases.length === 0) {
            container.innerHTML = `<p class="text-muted">${this.escapeHtml(text)}</p>`;
            return;
        }

        let html = '';
        let lastIndex = 0;

        // Sort phrases by position
        const sortedPhrases = [...phrases].sort((a, b) => a.start_pos - b.start_pos);

        sortedPhrases.forEach(phrase => {
            // Add text before highlight
            html += this.escapeHtml(text.substring(lastIndex, phrase.start_pos));

            // Add highlighted phrase
            const severityClass = `highlight-${phrase.severity.toLowerCase()}`;
            const categoryDisplay = phrase.category_display || phrase.category;
            
            html += `<span class="toxic-highlight ${severityClass}" 
                           data-category="${phrase.category}"
                           data-severity="${phrase.severity}"
                           title="${categoryDisplay}: ${phrase.explanation}">
                      ${this.escapeHtml(phrase.text)}
                    </span>`;

            lastIndex = phrase.end_pos;
        });

        // Add remaining text
        html += this.escapeHtml(text.substring(lastIndex));

        container.innerHTML = `<div class="highlighted-text">${html}</div>`;
    },

    /**
     * Render category breakdown chart
     * @param {Object} categories - Category counts
     * @param {string} containerId - ID of container element
     */
    renderCategoryBreakdown(categories, containerId) {
        const container = document.getElementById(containerId);
        if (!container) {
            console.error(`Container ${containerId} not found`);
            return;
        }

        if (!categories || Object.keys(categories).length === 0) {
            container.innerHTML = '<p class="text-muted">No toxic categories detected</p>';
            return;
        }

        const categoryDisplayNames = {
            'suicide_self_harm': 'Suicide & Self-Harm',
            'hate_speech': 'Hate Speech',
            'harassment': 'Harassment',
            'threats': 'Threats',
            'body_shaming': 'Body Shaming',
            'sexual_content': 'Sexual Content',
            'general_toxicity': 'General Toxicity'
        };

        const categoryColors = {
            'suicide_self_harm': '#dc3545',
            'hate_speech': '#dc3545',
            'threats': '#dc3545',
            'harassment': '#ffc107',
            'body_shaming': '#ffc107',
            'sexual_content': '#ffc107',
            'general_toxicity': '#6c757d'
        };

        let html = '<div class="category-breakdown">';
        
        for (const [category, count] of Object.entries(categories)) {
            const displayName = categoryDisplayNames[category] || category;
            const color = categoryColors[category] || '#6c757d';
            
            html += `
                <div class="category-item mb-2">
                    <div class="d-flex justify-content-between align-items-center">
                        <span class="category-label">
                            <span class="category-dot" style="background-color: ${color}"></span>
                            ${displayName}
                        </span>
                        <span class="badge bg-secondary">${count}</span>
                    </div>
                </div>
            `;
        }
        
        html += '</div>';
        container.innerHTML = html;
    },

    /**
     * Render severity breakdown
     * @param {Object} severityBreakdown - Severity counts
     * @param {string} containerId - ID of container element
     */
    renderSeverityBreakdown(severityBreakdown, containerId) {
        const container = document.getElementById(containerId);
        if (!container) {
            console.error(`Container ${containerId} not found`);
            return;
        }

        const total = (severityBreakdown.HIGH || 0) + 
                     (severityBreakdown.MEDIUM || 0) + 
                     (severityBreakdown.LOW || 0);

        if (total === 0) {
            container.innerHTML = '<p class="text-muted">No toxic content detected</p>';
            return;
        }

        const highPct = ((severityBreakdown.HIGH || 0) / total * 100).toFixed(1);
        const mediumPct = ((severityBreakdown.MEDIUM || 0) / total * 100).toFixed(1);
        const lowPct = ((severityBreakdown.LOW || 0) / total * 100).toFixed(1);

        const html = `
            <div class="severity-breakdown">
                <div class="severity-item">
                    <span class="severity-label">
                        <span class="severity-dot severity-high"></span>
                        High Severity
                    </span>
                    <span class="badge bg-danger">${severityBreakdown.HIGH || 0} (${highPct}%)</span>
                </div>
                <div class="severity-item">
                    <span class="severity-label">
                        <span class="severity-dot severity-medium"></span>
                        Medium Severity
                    </span>
                    <span class="badge bg-warning">${severityBreakdown.MEDIUM || 0} (${mediumPct}%)</span>
                </div>
                <div class="severity-item">
                    <span class="severity-label">
                        <span class="severity-dot severity-low"></span>
                        Low Severity
                    </span>
                    <span class="badge bg-secondary">${severityBreakdown.LOW || 0} (${lowPct}%)</span>
                </div>
            </div>
        `;

        container.innerHTML = html;
    },

    /**
     * Render complete explainability panel
     * @param {Object} explainability - Explainability data from API
     * @param {string} originalText - Original analyzed text
     * @param {string} containerId - ID of container element
     */
    renderExplainabilityPanel(explainability, originalText, containerId) {
        const container = document.getElementById(containerId);
        if (!container) {
            console.error(`Container ${containerId} not found`);
            return;
        }

        if (!explainability || explainability.total_matches === 0) {
            container.innerHTML = `
                <div class="alert alert-success">
                    <i class="bi bi-check-circle"></i>
                    No toxic phrases detected in this content.
                </div>
            `;
            return;
        }

        const html = `
            <div class="explainability-panel">
                <h5 class="mb-3">Detected Toxic Content</h5>
                
                <div class="row">
                    <div class="col-md-6 mb-3">
                        <h6>Highlighted Text</h6>
                        <div id="${containerId}-text" class="highlighted-text-container"></div>
                    </div>
                    
                    <div class="col-md-6 mb-3">
                        <h6>Category Breakdown</h6>
                        <div id="${containerId}-categories"></div>
                        
                        <h6 class="mt-3">Severity Breakdown</h6>
                        <div id="${containerId}-severity"></div>
                    </div>
                </div>
                
                <div class="mt-3">
                    <small class="text-muted">
                        Total: ${explainability.total_matches} toxic phrase(s) detected
                    </small>
                </div>
            </div>
        `;

        container.innerHTML = html;

        // Render sub-components
        this.renderHighlightedText(
            originalText, 
            explainability.highlighted_phrases, 
            `${containerId}-text`
        );
        this.renderCategoryBreakdown(
            explainability.categories_detected, 
            `${containerId}-categories`
        );
        this.renderSeverityBreakdown(
            explainability.severity_breakdown, 
            `${containerId}-severity`
        );
    },

    /**
     * Escape HTML to prevent XSS
     * @param {string} text - Text to escape
     * @returns {string} Escaped text
     */
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
};

// Export for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ExplainabilityUI;
}
