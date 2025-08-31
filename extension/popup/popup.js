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
            alert('Options page not available yet. All settings can be configured in this popup.');
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

        // Scan current page button
        document.getElementById('scanPageBtn').addEventListener('click', () => {
            console.log('Scan button clicked!');
            this.scanCurrentPage();
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

    showSuccess(message) {
        let successDiv = document.querySelector('.success');
        if (!successDiv) {
            successDiv = document.createElement('div');
            successDiv.className = 'success';
            successDiv.style.cssText = 'color: #10b981; margin-top: 10px; font-size: 14px;';
            document.querySelector('.input-section').appendChild(successDiv);
        }
        successDiv.textContent = message;
        successDiv.style.display = 'block';
        
        setTimeout(() => {
            successDiv.style.display = 'none';
        }, 3000);
    }

    async scanCurrentPage() {
        try {
            console.log('Starting page scan...');
            const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
            
            if (!tab) {
                console.log('No active tab found');
                this.showError('No active tab found');
                return;
            }

            console.log('Injecting content script into tab:', tab.id);
            
            // First, try to inject the content script if it's not already there
            try {
                await chrome.scripting.executeScript({
                    target: { tabId: tab.id },
                    func: () => {
                        // Check if content script is already loaded
                        if (window.genzContentScriptLoaded) {
                            return { alreadyLoaded: true };
                        }
                        
                        // Mark as loaded
                        window.genzContentScriptLoaded = true;
                        
                        console.log('🎯 GenZ Content Script Injected!');
                        
                        // Create a visible indicator
                        const indicator = document.createElement('div');
                        indicator.style.cssText = `
                            position: fixed;
                            top: 20px;
                            right: 20px;
                            background: #3b82f6;
                            color: white;
                            padding: 10px;
                            border-radius: 5px;
                            font-family: Arial, sans-serif;
                            font-size: 14px;
                            z-index: 10000;
                            box-shadow: 0 2px 10px rgba(0,0,0,0.2);
                        `;
                        indicator.textContent = '🛡️ GenZ Extension Active';
                        document.body.appendChild(indicator);
                        
                        // Set up message listener
                        chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
                            console.log('📨 Received message:', request);
                            
                            if (request.action === 'manualScan') {
                                console.log('🔍 Manual scan requested');
                                const elements = document.querySelectorAll('p, div, span, h1, h2, h3, h4, h5, h6');
                                console.log(`📊 Found ${elements.length} text elements`);
                                sendResponse({ scanned: elements.length });
                            }
                            
                            return true;
                        });
                        
                        console.log('✅ Content script setup complete');
                        return { success: true };
                    }
                });
            } catch (injectionError) {
                console.log('Content script injection failed:', injectionError);
            }

            // Now try to send the message
            console.log('Sending manualScan message to tab:', tab.id);
            const response = await chrome.tabs.sendMessage(tab.id, { action: 'manualScan' });
            
            console.log('Received response:', response);
            if (response && response.scanned) {
                let message = `Scanned ${response.scanned} elements on the page`;
                if (response.analyzed) {
                    message += `, analyzed ${response.analyzed} text elements`;
                }
                if (response.malicious > 0) {
                    message += `, found ${response.malicious} potentially malicious elements`;
                    this.showMaliciousResults(response.results);
                } else {
                    message += ', no malicious content detected';
                }
                this.showSuccess(message);
            } else {
                this.showError('Failed to scan page. Make sure you\'re on a supported website.');
            }
        } catch (error) {
            console.error('Scan error:', error);
            this.showError('Failed to scan page. Make sure you\'re on a supported website.');
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
