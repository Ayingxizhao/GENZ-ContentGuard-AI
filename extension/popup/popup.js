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

        // Debug button
        document.getElementById('debugBtn').addEventListener('click', () => {
            console.log('Debug button clicked!');
            this.debugPage();
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

            console.log('Current tab URL:', tab.url);
            
            // Show loading state
            this.setLoading(true);
            this.hideError();
            
            // First, test if content script is loaded
            try {
                console.log('Testing content script connection...');
                const pingResponse = await chrome.tabs.sendMessage(tab.id, { action: 'ping' });
                console.log('Ping response:', pingResponse);
            } catch (pingError) {
                console.error('Ping failed:', pingError);
                
                // Try to inject the content script manually
                try {
                    console.log('Attempting to inject content script manually...');
                    await chrome.scripting.executeScript({
                        target: { tabId: tab.id },
                        files: ['content/content.js']
                    });
                    console.log('Content script injected manually');
                    
                    // Wait a moment for the script to initialize
                    await new Promise(resolve => setTimeout(resolve, 1000));
                    
                    // Test again
                    const retryPing = await chrome.tabs.sendMessage(tab.id, { action: 'ping' });
                    console.log('Retry ping response:', retryPing);
                } catch (injectionError) {
                    console.error('Manual injection failed:', injectionError);
                    this.showError('Content script not loaded. Please refresh the page and try again.');
                    this.setLoading(false);
                    return;
                }
            }
            
            // Now try the actual scan
            try {
                console.log('Sending manualScan message to tab:', tab.id);
                const response = await chrome.tabs.sendMessage(tab.id, { action: 'manualScan' });
                
                console.log('Received response:', response);
                console.log('Response type:', typeof response);
                console.log('Response keys:', response ? Object.keys(response) : 'null');
                
                if (response && response.scanned) {
                    console.log('✅ Scan completed successfully');
                    let message = `Scanned ${response.scanned} social media posts/comments`;
                    if (response.analyzed) {
                        message += `, analyzed ${response.analyzed} items`;
                    }
                    if (response.malicious > 0) {
                        console.log('🚨 Malicious content found:', response.malicious, 'items');
                        message += `, found ${response.malicious} potentially malicious posts/comments`;
                        this.showMaliciousResults(response.results);
                    } else {
                        console.log('✅ No malicious content detected');
                        message += ', no malicious content detected';
                    }
                    this.showSuccess(message);
                } else if (response && response.error) {
                    console.log('❌ Scan error:', response.error);
                    this.showError(`Scan failed: ${response.error}`);
                } else if (response && response.message) {
                    console.log('❌ Scan message:', response.message);
                    this.showError(response.message);
                } else {
                    console.log('❌ No valid response received');
                    this.showError('Failed to scan social media content. Make sure the content script is loaded.');
                }
            } catch (error) {
                console.error('Message sending failed:', error);
                this.showError('Failed to communicate with the page. Make sure you\'re on a supported website.');
            }
        } catch (error) {
            console.error('Scan error:', error);
            this.showError('Failed to scan page. Make sure you\'re on a supported website.');
        } finally {
            this.setLoading(false);
        }
    }

    showMaliciousResults(results) {
        if (!results || results.length === 0) return;
        
        const resultSection = document.getElementById('resultSection');
        const resultCard = document.getElementById('resultCard');
        const resultLabel = document.getElementById('resultLabel');
        const confidence = document.getElementById('confidence');
        const resultDetails = document.getElementById('resultDetails');
        const modelInfo = document.getElementById('modelInfo');

        // Show result section
        resultSection.style.display = 'block';

        // Update result card styling for malicious content
        resultCard.className = 'result-card malicious';

        // Update content
        resultLabel.textContent = 'MALICIOUS CONTENT FOUND';
        resultLabel.className = 'result-label malicious';
        
        confidence.textContent = `${results.length} items`;
        
        // Create detailed results
        let detailsHtml = '<p>⚠️ The following potentially malicious content was found:</p><ul>';
        results.forEach((item, index) => {
            detailsHtml += `<li><strong>${item.element}:</strong> "${item.text}" (${item.confidence})</li>`;
        });
        detailsHtml += '</ul><p><strong>Recommendation:</strong> Review the highlighted content on the page.</p>';
        
        resultDetails.innerHTML = detailsHtml;
        modelInfo.innerHTML = '<small>Page scan completed with Local ML Model</small>';
    }

    async debugPage() {
        try {
            const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
            
            if (!tab) {
                this.showError('No active tab found');
                return;
            }

            console.log('Debugging page:', tab.url);
            
            try {
                const response = await chrome.tabs.sendMessage(tab.id, { action: 'debug' });
                
                if (response && response.debug) {
                    const debug = response.debug;
                    console.log('Debug info:', debug);
                    
                    let debugMessage = `Page Debug Info:\n\n`;
                    debugMessage += `URL: ${debug.url}\n`;
                    debugMessage += `Hostname: ${debug.hostname}\n`;
                    debugMessage += `Total Elements: ${debug.totalElements}\n`;
                    debugMessage += `Text Elements: ${debug.textElements}\n`;
                    debugMessage += `Articles: ${debug.articles}\n`;
                    debugMessage += `Data Test IDs: ${debug.dataTestIds}\n\n`;
                    
                    if (debug.sampleTexts.length > 0) {
                        debugMessage += `Sample Texts:\n`;
                        debug.sampleTexts.forEach((item, index) => {
                            debugMessage += `${index + 1}. "${item.text}" (${item.tag})\n`;
                        });
                    } else {
                        debugMessage += `No sample texts found\n`;
                    }
                    
                    alert(debugMessage);
                } else {
                    this.showError('Debug failed - no response');
                }
            } catch (error) {
                console.error('Debug error:', error);
                this.showError('Debug failed: ' + error.message);
            }
        } catch (error) {
            console.error('Debug error:', error);
            this.showError('Debug failed: ' + error.message);
        }
    }

    showHelp() {
        const helpText = `
GenZ Content Detector Help:

1. Paste or type text in the input area
2. Click "Analyze" or press Ctrl+Enter
3. View the analysis result
4. Adjust sensitivity in settings
5. Use "Scan Social Media" to analyze social media content

The extension uses machine learning to detect:
- Hate speech and discrimination
- Suicide encouragement
- Online harassment
- Violent threats
- GenZ-specific malicious language

Social Media Scanner:
- Works on most social media platforms (Reddit, Twitter, Facebook, Instagram, TikTok, YouTube, LinkedIn, Discord)
- Scans posts and comments specifically
- Highlights malicious content with red borders
- Shows results in the popup

For best results, use the local model (faster) or OpenAI (more accurate).
        `;
        
        alert(helpText);
    }
}

// Initialize popup when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new GenZDetectorPopup();
});
