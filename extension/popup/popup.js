// Popup functionality for GenZ Content Detector
class GenZDetectorPopup {
    constructor() {
        this.apiUrl = 'http://localhost:5001';
        this.init();
    }

    init() {
        this.bindEvents();
        this.loadSettings();
        this.updateStatus();
    }

    bindEvents() {
        // Analyze button
        document.getElementById('analyzeBtn').addEventListener('click', () => {
            this.analyzeText();
        });

        // Clear button
        document.getElementById('clearBtn').addEventListener('click', () => {
            this.clearText();
        });

        // Settings
        document.getElementById('sensitivitySlider').addEventListener('input', (e) => {
            this.updateSensitivity(e.target.value);
        });

        document.getElementById('autoScanToggle').addEventListener('change', (e) => {
            this.updateAutoScan(e.target.checked);
        });

        document.getElementById('useOpenAIToggle').addEventListener('change', (e) => {
            this.updateUseOpenAI(e.target.checked);
        });

        // Footer buttons
        document.getElementById('optionsBtn').addEventListener('click', () => {
            chrome.runtime.openOptionsPage();
        });

        document.getElementById('helpBtn').addEventListener('click', () => {
            this.showHelp();
        });

        // Enter key in textarea
        document.getElementById('textInput').addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && e.ctrlKey) {
                this.analyzeText();
            }
        });
    }

    async analyzeText() {
        const textInput = document.getElementById('textInput');
        const text = textInput.value.trim();
        
        if (!text) {
            this.showError('Please enter some text to analyze');
            return;
        }

        this.setLoading(true);
        this.hideError();

        try {
            const settings = await this.getSettings();
            const response = await fetch(`${this.apiUrl}/analyze`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    title: '',
                    content: text,
                    use_openai: settings.useOpenAI
                })
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const result = await response.json();
            this.displayResult(result);

        } catch (error) {
            console.error('Analysis error:', error);
            this.showError(`Analysis failed: ${error.message}`);
        } finally {
            this.setLoading(false);
        }
    }

    displayResult(result) {
        const resultSection = document.getElementById('resultSection');
        const resultCard = document.getElementById('resultCard');
        const resultLabel = document.getElementById('resultLabel');
        const confidence = document.getElementById('confidence');
        const resultDetails = document.getElementById('resultDetails');
        const modelInfo = document.getElementById('modelInfo');

        // Show result section
        resultSection.style.display = 'block';

        // Update result card styling
        resultCard.className = result.is_malicious ? 'result-card malicious' : 'result-card';

        // Update content
        resultLabel.textContent = result.analysis;
        resultLabel.className = result.is_malicious ? 'result-label malicious' : 'result-label';
        
        confidence.textContent = result.confidence;
        
        if (result.is_malicious) {
            resultDetails.innerHTML = `
                <p>⚠️ This content appears to be potentially harmful or malicious.</p>
                <p><strong>Recommendation:</strong> Consider reporting or avoiding this content.</p>
            `;
        } else {
            resultDetails.innerHTML = `
                <p>✅ This content appears to be safe.</p>
                <p><strong>Analysis:</strong> No harmful content detected.</p>
            `;
        }

        modelInfo.innerHTML = `<small>Analyzed with: ${result.model_type || 'Local ML Model'}</small>`;

        // Update badge
        this.updateBadge(result.is_malicious);
    }

    clearText() {
        document.getElementById('textInput').value = '';
        document.getElementById('resultSection').style.display = 'none';
        this.hideError();
    }

    async getSettings() {
        return new Promise((resolve) => {
            chrome.storage.sync.get({
                sensitivity: 50,
                autoScan: false,
                useOpenAI: false
            }, resolve);
        });
    }

    async loadSettings() {
        const settings = await this.getSettings();
        
        document.getElementById('sensitivitySlider').value = settings.sensitivity;
        document.getElementById('sensitivityValue').textContent = `${settings.sensitivity}%`;
        document.getElementById('autoScanToggle').checked = settings.autoScan;
        document.getElementById('useOpenAIToggle').checked = settings.useOpenAI;
    }

    updateSensitivity(value) {
        document.getElementById('sensitivityValue').textContent = `${value}%`;
        chrome.storage.sync.set({ sensitivity: parseInt(value) });
    }

    updateAutoScan(enabled) {
        chrome.storage.sync.set({ autoScan: enabled });
    }

    updateUseOpenAI(enabled) {
        chrome.storage.sync.set({ useOpenAI: enabled });
    }

    async updateStatus() {
        try {
            const response = await fetch(`${this.apiUrl}/model-info`);
            const modelInfo = await response.json();
            
            const statusDot = document.getElementById('statusDot');
            const statusText = document.getElementById('statusText');
            
            if (modelInfo.local_model.status === 'loaded') {
                statusDot.style.background = '#4ade80';
                statusText.textContent = 'Ready';
            } else {
                statusDot.style.background = '#ef4444';
                statusText.textContent = 'Model Error';
            }
        } catch (error) {
            console.error('Status check failed:', error);
            const statusDot = document.getElementById('statusDot');
            const statusText = document.getElementById('statusText');
            statusDot.style.background = '#f59e0b';
            statusText.textContent = 'Connecting...';
        }
    }

    updateBadge(isMalicious) {
        chrome.action.setBadgeText({
            text: isMalicious ? '!' : ''
        });
        chrome.action.setBadgeBackgroundColor({
            color: isMalicious ? '#ef4444' : '#4ade80'
        });
    }

    setLoading(loading) {
        const analyzeBtn = document.getElementById('analyzeBtn');
        const textInput = document.getElementById('textInput');
        
        if (loading) {
            analyzeBtn.textContent = 'Analyzing...';
            analyzeBtn.disabled = true;
            textInput.classList.add('loading');
        } else {
            analyzeBtn.textContent = 'Analyze';
            analyzeBtn.disabled = false;
            textInput.classList.remove('loading');
        }
    }

    showError(message) {
        let errorDiv = document.querySelector('.error');
        if (!errorDiv) {
            errorDiv = document.createElement('div');
            errorDiv.className = 'error';
            document.querySelector('.input-section').appendChild(errorDiv);
        }
        errorDiv.textContent = message;
        errorDiv.style.display = 'block';
    }

    hideError() {
        const errorDiv = document.querySelector('.error');
        if (errorDiv) {
            errorDiv.style.display = 'none';
        }
    }

    showHelp() {
        const helpText = `
GenZ Content Detector Help:

1. Paste or type text in the input area
2. Click "Analyze" or press Ctrl+Enter
3. View the analysis result
4. Adjust sensitivity in settings
5. Enable auto-scan for automatic detection

The extension uses machine learning to detect:
- Hate speech and discrimination
- Suicide encouragement
- Online harassment
- Violent threats
- GenZ-specific malicious language

For best results, use the local model (faster) or OpenAI (more accurate).
        `;
        
        alert(helpText);
    }
}

// Initialize popup when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new GenZDetectorPopup();
});
