/**
 * Rate Limit Handler for Gemini API
 * Displays cooldown timer and manages button states
 */

class RateLimitHandler {
    constructor() {
        this.cooldownEndTime = null;
        this.timerInterval = null;
        this.analyzeBtn = document.querySelector('.analyze-btn');
        this.rateLimitDisplay = null;
        this.createRateLimitDisplay();
    }

    createRateLimitDisplay() {
        // Create rate limit display element if it doesn't exist
        const form = document.getElementById('analysisForm');
        if (!form) return;

        this.rateLimitDisplay = document.createElement('div');
        this.rateLimitDisplay.id = 'rateLimitDisplay';
        this.rateLimitDisplay.className = 'rate-limit-display';
        this.rateLimitDisplay.style.display = 'none';
        
        // Insert before the analyze button
        const buttonContainer = this.analyzeBtn.parentElement;
        buttonContainer.insertBefore(this.rateLimitDisplay, this.analyzeBtn);
    }

    handleRateLimitError(errorData) {
        if (errorData.seconds_remaining) {
            // Start cooldown timer
            this.startCooldown(errorData.seconds_remaining);
            
            // Show error message with timer
            const message = errorData.hint || errorData.error;
            this.showError(message, errorData);
        }
    }

    startCooldown(seconds) {
        this.cooldownEndTime = Date.now() + (seconds * 1000);
        
        // Disable button
        if (this.analyzeBtn) {
            this.analyzeBtn.disabled = true;
        }
        
        // Start timer
        this.updateTimer();
        this.timerInterval = setInterval(() => this.updateTimer(), 1000);
    }

    updateTimer() {
        if (!this.cooldownEndTime) return;

        const now = Date.now();
        const remaining = Math.max(0, Math.ceil((this.cooldownEndTime - now) / 1000));

        if (remaining <= 0) {
            // Cooldown finished
            this.endCooldown();
            return;
        }

        // Format time
        const minutes = Math.floor(remaining / 60);
        const seconds = remaining % 60;
        const timeStr = minutes > 0 
            ? `${minutes}m ${seconds}s` 
            : `${seconds}s`;

        // Update display
        if (this.rateLimitDisplay) {
            this.rateLimitDisplay.style.display = 'block';
            this.rateLimitDisplay.innerHTML = `
                <div class="cooldown-timer">
                    <i class="fas fa-clock"></i>
                    <span>Gemini API cooldown: <strong>${timeStr}</strong> remaining</span>
                    <small>Sign in to remove cooldowns</small>
                </div>
            `;
        }

        // Update button
        if (this.analyzeBtn) {
            this.analyzeBtn.innerHTML = `
                <i class="fas fa-clock"></i>
                <span>Cooldown: ${timeStr}</span>
            `;
        }
    }

    endCooldown() {
        // Clear timer
        if (this.timerInterval) {
            clearInterval(this.timerInterval);
            this.timerInterval = null;
        }
        this.cooldownEndTime = null;

        // Hide display
        if (this.rateLimitDisplay) {
            this.rateLimitDisplay.style.display = 'none';
        }

        // Re-enable button
        if (this.analyzeBtn) {
            this.analyzeBtn.disabled = false;
            this.analyzeBtn.innerHTML = `
                <i class="fas fa-shield-alt"></i>
                <span>Analyze Content</span>
            `;
        }
    }

    showError(message, errorData) {
        const errorSection = document.getElementById('errorSection');
        if (!errorSection) return;

        errorSection.style.display = 'block';
        errorSection.innerHTML = `
            <div class="error-content">
                <i class="fas fa-exclamation-circle"></i>
                <h3>Rate Limit Active</h3>
                <p>${message}</p>
                ${errorData.actions ? `
                    <div class="error-actions">
                        <a href="${errorData.actions.login}" class="btn btn-primary">Sign In</a>
                        <a href="${errorData.actions.signup}" class="btn btn-secondary">Sign Up</a>
                    </div>
                ` : ''}
            </div>
        `;
    }

    displayRateLimitInfo(rateLimitData) {
        if (!rateLimitData) return;

        // Display remaining calls info
        const info = [];
        
        if (rateLimitData.user_remaining !== undefined) {
            info.push(`${rateLimitData.user_remaining}/${rateLimitData.user_limit} calls remaining today`);
        }
        
        if (rateLimitData.global_remaining !== undefined) {
            info.push(`${rateLimitData.global_remaining}/${rateLimitData.global_limit} global calls remaining`);
        }

        if (info.length > 0 && this.rateLimitDisplay) {
            this.rateLimitDisplay.style.display = 'block';
            this.rateLimitDisplay.innerHTML = `
                <div class="rate-limit-info">
                    <i class="fas fa-info-circle"></i>
                    <span>${info.join(' • ')}</span>
                </div>
            `;
        }
    }
}

// Export for use in main script
window.RateLimitHandler = RateLimitHandler;
