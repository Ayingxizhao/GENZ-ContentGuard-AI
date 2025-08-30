// Content script for automatic malicious content detection
class GenZContentScanner {
    constructor() {
        this.apiUrl = 'http://localhost:5001';
        this.scanning = false;
        this.settings = {};
        this.init();
    }

    async init() {
        await this.loadSettings();
        this.setupObserver();
        this.scanPage();
    }

    async loadSettings() {
        return new Promise((resolve) => {
            chrome.storage.sync.get({
                autoScan: false,
                sensitivity: 50,
                useOpenAI: false
            }, (settings) => {
                this.settings = settings;
                resolve(settings);
            });
        });
    }

    setupObserver() {
        // Watch for new content being added to the page
        const observer = new MutationObserver((mutations) => {
            if (this.settings.autoScan && !this.scanning) {
                mutations.forEach((mutation) => {
                    if (mutation.type === 'childList' && mutation.addedNodes.length > 0) {
                        this.scanNewContent(mutation.addedNodes);
                    }
                });
            }
        });

        observer.observe(document.body, {
            childList: true,
            subtree: true
        });
    }

    async scanPage() {
        if (!this.settings.autoScan) return;

        this.scanning = true;
        const textElements = this.findTextElements();
        
        for (const element of textElements) {
            await this.analyzeElement(element);
        }
        
        this.scanning = false;
    }

    async scanNewContent(nodes) {
        for (const node of nodes) {
            if (node.nodeType === Node.ELEMENT_NODE) {
                const textElements = node.querySelectorAll ? 
                    node.querySelectorAll('p, div, span, h1, h2, h3, h4, h5, h6, article, section') :
                    [node];
                
                for (const element of textElements) {
                    if (this.hasSignificantText(element)) {
                        await this.analyzeElement(element);
                    }
                }
            }
        }
    }

    findTextElements() {
        // Find elements that likely contain user-generated content
        const selectors = [
            'p', 'div', 'span', 'article', 'section',
            '[data-testid*="tweet"]', // Twitter
            '[data-testid*="post"]',  // Reddit
            '.post-content', '.comment-content',
            '.status-content', '.message-content'
        ];
        
        const elements = [];
        selectors.forEach(selector => {
            const found = document.querySelectorAll(selector);
            found.forEach(el => {
                if (this.hasSignificantText(el) && !el.hasAttribute('data-genz-scanned')) {
                    elements.push(el);
                }
            });
        });
        
        return elements;
    }

    hasSignificantText(element) {
        const text = element.textContent?.trim();
        return text && text.length > 20 && text.length < 1000;
    }

    async analyzeElement(element) {
        if (element.hasAttribute('data-genz-scanned')) return;

        const text = element.textContent?.trim();
        if (!text || text.length < 20) return;

        try {
            const response = await fetch(`${this.apiUrl}/analyze`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    title: '',
                    content: text,
                    use_openai: this.settings.useOpenAI
                })
            });

            if (!response.ok) return;

            const result = await response.json();
            
            if (result.is_malicious) {
                this.markElementAsMalicious(element, result);
            }

            // Mark as scanned to avoid re-scanning
            element.setAttribute('data-genz-scanned', 'true');

        } catch (error) {
            console.error('Content analysis failed:', error);
        }
    }

    markElementAsMalicious(element, result) {
        // Add visual indicator
        element.style.border = '2px solid #ef4444';
        element.style.backgroundColor = '#fef2f2';
        element.style.padding = '8px';
        element.style.borderRadius = '4px';
        element.style.position = 'relative';

        // Add warning icon
        const warningIcon = document.createElement('div');
        warningIcon.innerHTML = '⚠️';
        warningIcon.style.cssText = `
            position: absolute;
            top: -10px;
            right: -10px;
            background: #ef4444;
            color: white;
            border-radius: 50%;
            width: 20px;
            height: 20px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 12px;
            cursor: pointer;
            z-index: 1000;
        `;

        warningIcon.title = `Malicious content detected (${result.confidence} confidence)`;
        warningIcon.addEventListener('click', () => {
            this.showDetails(element, result);
        });

        element.appendChild(warningIcon);

        // Add hover effect
        element.addEventListener('mouseenter', () => {
            element.style.boxShadow = '0 0 10px rgba(239, 68, 68, 0.3)';
        });

        element.addEventListener('mouseleave', () => {
            element.style.boxShadow = 'none';
        });
    }

    showDetails(element, result) {
        // Create a popup with analysis details
        const popup = document.createElement('div');
        popup.style.cssText = `
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            background: white;
            border: 2px solid #ef4444;
            border-radius: 8px;
            padding: 20px;
            max-width: 400px;
            z-index: 10000;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        `;

        popup.innerHTML = `
            <h3 style="color: #ef4444; margin: 0 0 10px 0;">⚠️ Malicious Content Detected</h3>
            <p><strong>Confidence:</strong> ${result.confidence}</p>
            <p><strong>Analysis:</strong> ${result.analysis}</p>
            <p><strong>Model:</strong> ${result.model_type || 'Local ML Model'}</p>
            <div style="margin-top: 15px;">
                <button id="report-btn" style="background: #ef4444; color: white; border: none; padding: 8px 16px; border-radius: 4px; margin-right: 10px; cursor: pointer;">Report</button>
                <button id="dismiss-btn" style="background: #6b7280; color: white; border: none; padding: 8px 16px; border-radius: 4px; cursor: pointer;">Dismiss</button>
            </div>
        `;

        document.body.appendChild(popup);

        // Add event listeners
        popup.querySelector('#report-btn').addEventListener('click', () => {
            this.reportContent(element, result);
            document.body.removeChild(popup);
        });

        popup.querySelector('#dismiss-btn').addEventListener('click', () => {
            document.body.removeChild(popup);
        });

        // Close on outside click
        popup.addEventListener('click', (e) => {
            if (e.target === popup) {
                document.body.removeChild(popup);
            }
        });
    }

    reportContent(element, result) {
        // Implement reporting functionality
        console.log('Reporting malicious content:', {
            text: element.textContent,
            analysis: result,
            url: window.location.href,
            timestamp: new Date().toISOString()
        });

        // Show confirmation
        const notification = document.createElement('div');
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: #10b981;
            color: white;
            padding: 10px 20px;
            border-radius: 4px;
            z-index: 10001;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        `;
        notification.textContent = 'Content reported successfully';
        document.body.appendChild(notification);

        setTimeout(() => {
            if (document.body.contains(notification)) {
                document.body.removeChild(notification);
            }
        }, 3000);
    }

    // Manual scan function (called from popup)
    async manualScan() {
        this.scanning = true;
        const textElements = this.findTextElements();
        
        for (const element of textElements) {
            await this.analyzeElement(element);
        }
        
        this.scanning = false;
        return textElements.length;
    }
}

// Initialize content scanner
const scanner = new GenZContentScanner();

// Listen for messages from popup
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === 'manualScan') {
        scanner.manualScan().then(count => {
            sendResponse({ scanned: count });
        });
        return true; // Keep message channel open for async response
    }
    
    if (request.action === 'updateSettings') {
        scanner.loadSettings().then(() => {
            sendResponse({ success: true });
        });
        return true;
    }
});
