// Simple test content script
console.log('🎯 GenZ Content Script Loaded!');

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

// Listen for messages
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
