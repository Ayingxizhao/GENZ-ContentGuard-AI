// Background script for GenZ Content Detector
chrome.runtime.onInstalled.addListener(() => {
    console.log('GenZ Content Detector installed');
    
    // Set default settings
    chrome.storage.sync.set({
        sensitivity: 50,
        autoScan: false,
        useOpenAI: false
    });
});

// Handle extension icon click
chrome.action.onClicked.addListener((tab) => {
    // Open popup (handled by manifest)
    console.log('Extension icon clicked');
});

// Listen for messages from content scripts and popup
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    console.log('Background received message:', request);
    
    if (request.action === 'getTabInfo') {
        sendResponse({
            url: sender.tab?.url,
            title: sender.tab?.title
        });
    }
    
    if (request.action === 'openOptions') {
        chrome.runtime.openOptionsPage();
        sendResponse({ success: true });
    }
    
    return true;
});
