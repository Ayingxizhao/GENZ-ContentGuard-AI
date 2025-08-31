// Development Helper for Hot Reloading
class ExtensionDevHelper {
    constructor() {
        this.watchInterval = null;
        this.lastModified = {};
        this.init();
    }

    init() {
        console.log('🛠️ Extension Dev Helper Loaded');
        this.startWatching();
        this.setupHotReload();
    }

    startWatching() {
        // Watch for changes in content script files
        this.watchInterval = setInterval(() => {
            this.checkForChanges();
        }, 1000); // Check every second
    }

    async checkForChanges() {
        try {
            // Get current tab
            const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
            if (!tab) return;

            // Check if we're on a supported page
            if (!tab.url.startsWith('http')) return;

            // Simulate a change detection (in real implementation, you'd check file timestamps)
            // For now, we'll use a simple approach with localStorage
            const lastReload = localStorage.getItem('lastContentReload') || '0';
            const now = Date.now();
            
            // Reload every 30 seconds during development (you can adjust this)
            if (now - parseInt(lastReload) > 30000) {
                this.reloadContentScript(tab.id);
                localStorage.setItem('lastContentReload', now.toString());
            }
        } catch (error) {
            console.error('Dev helper error:', error);
        }
    }

    async reloadContentScript(tabId) {
        try {
            console.log('🔄 Reloading content script...');
            
            // Remove existing content script
            await chrome.scripting.executeScript({
                target: { tabId: tabId },
                func: () => {
                    // Remove existing indicators
                    const existingIndicator = document.querySelector('[data-genz-extension]');
                    if (existingIndicator) {
                        existingIndicator.remove();
                    }
                    
                    // Clear any existing listeners
                    if (window.genzContentScriptLoaded) {
                        delete window.genzContentScriptLoaded;
                    }
                    
                    console.log('🧹 Cleaned up existing content script');
                }
            });

            // Inject fresh content script
            await chrome.scripting.executeScript({
                target: { tabId: tabId },
                files: ['content/content.js']
            });

            console.log('✅ Content script reloaded successfully');
        } catch (error) {
            console.error('Failed to reload content script:', error);
        }
    }

    setupHotReload() {
        // Add keyboard shortcut for manual reload
        document.addEventListener('keydown', (e) => {
            // Ctrl+Shift+R to reload content script
            if (e.ctrlKey && e.shiftKey && e.key === 'R') {
                e.preventDefault();
                this.manualReload();
            }
        });
    }

    async manualReload() {
        const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
        if (tab) {
            this.reloadContentScript(tab.id);
        }
    }

    stopWatching() {
        if (this.watchInterval) {
            clearInterval(this.watchInterval);
            this.watchInterval = null;
        }
    }
}

// Initialize dev helper
const devHelper = new ExtensionDevHelper();

// Export for use in other scripts
window.extensionDevHelper = devHelper;
