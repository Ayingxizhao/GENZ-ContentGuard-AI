// GenZ Content Script for scanning social media content
console.log('🎯 GenZ Content Script Loaded!');
console.log('📍 Current URL:', window.location.href);
console.log('🌐 Hostname:', window.location.hostname);

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
    display: none;
`;
indicator.textContent = '🛡️ GenZ Extension Active';
document.body.appendChild(indicator);

// Show indicator briefly on load to confirm script is running
setTimeout(() => {
    indicator.style.display = 'block';
    indicator.textContent = '🛡️ GenZ Extension Loaded';
    setTimeout(() => {
        indicator.style.display = 'none';
    }, 3000);
}, 1000);

// Function to extract text from social media content
function extractSocialMediaContent() {
    const texts = [];
    const hostname = window.location.hostname.toLowerCase();
    
    console.log('🔍 Starting content extraction on:', hostname);
    
    // More comprehensive and general selectors that work on most sites
    const allSelectors = [
        // Common social media content selectors
        'article p',
        'article div[dir="auto"]',
        'article span[dir="auto"]',
        'article div',
        'article span',
        
        // Data testid selectors (common in modern web apps)
        '[data-testid*="post"]',
        '[data-testid*="comment"]',
        '[data-testid*="tweet"]',
        '[data-testid*="message"]',
        '[data-testid*="content"]',
        '[data-testid*="text"]',
        '[data-testid*="description"]',
        
        // Common class names
        '.post-content',
        '.comment-content',
        '.message-content',
        '.content-text',
        '.description-text',
        '.text-content',
        '.post-text',
        '.comment-text',
        '.message-text',
        
        // Generic content selectors
        'p',
        'div[role="article"]',
        'div[role="main"]',
        'main p',
        'main div',
        
        // Reddit specific
        '[data-testid="post-container"] [data-testid="post-content"]',
        '[data-testid="post-container"] .RichTextJSON-root',
        '[data-testid="post-container"] .Post__content',
        '[data-testid="post-container"] .entry .usertext-body',
        '[data-testid="post-container"] .md',
        '[data-testid="post-container"] h1',
        '[data-testid="post-container"] .title',
        '[data-testid="comment"] .RichTextJSON-root',
        '[data-testid="comment"] .md',
        '.thing.link .entry .title',
        '.thing.link .entry .usertext-body',
        '.thing.comment .entry .usertext-body',
        
        // Twitter/X specific
        '[data-testid="tweetText"]',
        '[data-testid="tweet"] [data-testid="tweetText"]',
        'article[data-testid="tweet"] div[lang]',
        '[data-testid="reply"] [data-testid="tweetText"]',
        
        // Facebook specific
        '[data-testid="post_message"]',
        '[data-testid="post_message"] div',
        '.userContent',
        '.userContent div',
        '[data-testid="comment"] div[dir="auto"]',
        
        // Instagram specific
        'article div[dir="auto"]',
        '[data-testid="post-caption"]',
        '[data-testid="comment"] div[dir="auto"]',
        'article span[dir="auto"]',
        
        // YouTube specific
        '#content-text',
        '#description-text',
        '#content-text span',
        '#description-text span',
        '#content-text yt-formatted-string',
        '#description-text yt-formatted-string',
        
        // LinkedIn specific
        '.feed-shared-update-v2__description',
        '.feed-shared-text',
        '.comments-comment-item__main-content',
        '.comments-comment-item__inline-show-more-text'
    ];
    
    console.log('🔍 Using', allSelectors.length, 'selectors');
    
    // Try each selector and collect text
    allSelectors.forEach((selector, index) => {
        try {
            const elements = document.querySelectorAll(selector);
            console.log(`Selector ${index + 1}/${allSelectors.length}: "${selector}" found ${elements.length} elements`);
            
            elements.forEach(element => {
                const text = element.textContent.trim();
                
                // More lenient text filtering
                if (text.length > 5 && text.length < 3000) { // Allow shorter texts
                    // Less restrictive filtering - only skip obvious UI elements
                    const skipKeywords = [
                        '•', 'points', 'comments', 'share', 'save', 'hide', 'report',
                        'block', 'reply', 'like', 'follow', 'subscribe', 'sort by',
                        'best', 'top', 'new', 'old', 'q&a', 'edit', 'delete', 'more',
                        'menu', 'settings', 'profile', 'search', 'login', 'sign up',
                        'loading', 'error', 'success', 'warning', 'info'
                    ];
                    
                    const shouldSkip = skipKeywords.some(keyword => 
                        text.toLowerCase().includes(keyword.toLowerCase())
                    );
                    
                    if (!shouldSkip) {
                        // Additional check: make sure it's not just whitespace or single characters
                        const cleanText = text.replace(/\s+/g, ' ').trim();
                        if (cleanText.length > 5 && /[a-zA-Z]/.test(cleanText)) {
                            texts.push({
                                text: text,
                                element: element,
                                tagName: element.tagName.toLowerCase(),
                                selector: selector,
                                platform: hostname
                            });
                        }
                    }
                }
            });
        } catch (error) {
            console.log(`Error with selector ${selector}:`, error);
        }
    });
    
    console.log('📊 Total texts found before deduplication:', texts.length);
    
    // Remove duplicates based on text content
    const uniqueTexts = [];
    const seenTexts = new Set();
    
    texts.forEach(item => {
        const normalizedText = item.text.toLowerCase().trim().replace(/\s+/g, ' ');
        if (!seenTexts.has(normalizedText) && normalizedText.length > 5) {
            seenTexts.add(normalizedText);
            uniqueTexts.push(item);
        }
    });
    
    console.log('📊 Unique texts after deduplication:', uniqueTexts.length);
    
    // Log some examples of what was found
    if (uniqueTexts.length > 0) {
        console.log('📝 Sample texts found:');
        uniqueTexts.slice(0, 3).forEach((item, index) => {
            console.log(`${index + 1}. "${item.text.substring(0, 100)}..." (selector: ${item.selector})`);
        });
    }
    
    return uniqueTexts;
}

// Function to analyze text using the API
async function analyzeText(text) {
    try {
        const response = await fetch('http://localhost:5001/analyze', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                title: '',
                content: text
            })
        });
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        return await response.json();
    } catch (error) {
        console.error('Analysis error:', error);
        return null;
    }
}

// Function to highlight malicious content
function highlightMaliciousContent(element, result) {
    element.style.backgroundColor = '#fee2e2';
    element.style.border = '2px solid #ef4444';
    element.style.borderRadius = '4px';
    element.style.padding = '4px';
    
    // Add a warning icon
    const warning = document.createElement('span');
    warning.innerHTML = ' ⚠️';
    warning.style.color = '#ef4444';
    warning.style.fontWeight = 'bold';
    element.appendChild(warning);
}

// Function to scan social media content
async function scanSocialMediaContent() {
    console.log('🔍 Starting social media content scan...');
    
    const texts = extractSocialMediaContent();
    console.log(`📊 Found ${texts.length} social media posts/comments to analyze`);
    
    if (texts.length === 0) {
        console.log('No social media content found on this page');
        return {
            scanned: 0,
            analyzed: 0,
            malicious: 0,
            results: [],
            message: 'No social media content found on this page'
        };
    }
    
    let analyzed = 0;
    let malicious = 0;
    const results = [];
    
    // Show indicator during scan
    indicator.style.display = 'block';
    indicator.textContent = '🔍 Scanning social media content...';
    
            // Analyze each text element
        for (const item of texts) {
            try {
                const result = await analyzeText(item.text);
                analyzed++;
                
                console.log(`Analyzing item ${analyzed}/${texts.length}:`, {
                    text: item.text.substring(0, 50) + '...',
                    result: result
                });
                
                if (result && result.is_malicious) {
                    malicious++;
                    console.log('🚨 MALICIOUS CONTENT FOUND:', {
                        text: item.text.substring(0, 100) + '...',
                        confidence: result.confidence,
                        element: item.tagName
                    });
                    highlightMaliciousContent(item.element, result);
                    results.push({
                        text: item.text.substring(0, 100) + '...',
                        confidence: result.confidence,
                        element: item.tagName,
                        type: item.selector.includes('comment') ? 'Comment' : 'Post',
                        platform: item.platform
                    });
                }
                
                // Update indicator
                indicator.textContent = `🔍 Scanning... (${analyzed}/${texts.length})`;
                
            } catch (error) {
                console.error('Error analyzing text:', error);
            }
        }
    
    // Update indicator with results
    if (malicious > 0) {
        indicator.textContent = `⚠️ Found ${malicious} malicious posts/comments`;
        indicator.style.background = '#ef4444';
    } else {
        indicator.textContent = '✅ Social media content appears safe';
        indicator.style.background = '#10b981';
    }
    
    // Hide indicator after 5 seconds
    setTimeout(() => {
        indicator.style.display = 'none';
    }, 5000);
    
    return {
        scanned: texts.length,
        analyzed: analyzed,
        malicious: malicious,
        results: results
    };
}

// Listen for messages from popup
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    console.log('📨 Received message:', request);
    
    if (request.action === 'manualScan') {
        console.log('🔍 Manual scan requested');
        console.log('📍 Current URL:', window.location.href);
        console.log('🌐 Hostname:', window.location.hostname);
        
        console.log('✅ Starting social media scan...');
        
        // Perform the scan asynchronously with timeout
        const scanPromise = scanSocialMediaContent();
        const timeoutPromise = new Promise((_, reject) => 
            setTimeout(() => reject(new Error('Scan timeout after 30 seconds')), 30000)
        );
        
        Promise.race([scanPromise, timeoutPromise])
            .then(result => {
                console.log('📊 Scan completed:', result);
                sendResponse(result);
            })
            .catch(error => {
                console.error('❌ Scan failed:', error);
                sendResponse({ error: error.message });
            });
        
        return true; // Keep message channel open for async response
    }
    
    if (request.action === 'showIndicator') {
        indicator.style.display = 'block';
        sendResponse({ success: true });
    }
    
    if (request.action === 'hideIndicator') {
        indicator.style.display = 'none';
        sendResponse({ success: true });
    }
    
    // Add a simple ping response for testing
    if (request.action === 'ping') {
        console.log('🏓 Ping received');
        sendResponse({ success: true, message: 'Content script is running' });
        return true;
    }
    
    // Add debug function to see what's on the page
    if (request.action === 'debug') {
        console.log('🔍 Debug requested');
        
        // Count all elements on the page
        const allElements = document.querySelectorAll('*');
        const textElements = document.querySelectorAll('p, div, span, h1, h2, h3, h4, h5, h6');
        const articles = document.querySelectorAll('article');
        const dataTestIds = document.querySelectorAll('[data-testid]');
        
        // Get some sample text content
        const sampleTexts = [];
        textElements.forEach((el, index) => {
            if (index < 10) { // Only first 10
                const text = el.textContent.trim();
                if (text.length > 5 && text.length < 200) {
                    sampleTexts.push({
                        text: text.substring(0, 100),
                        tag: el.tagName,
                        classes: el.className,
                        testId: el.getAttribute('data-testid')
                    });
                }
            }
        });
        
        sendResponse({
            success: true,
            debug: {
                totalElements: allElements.length,
                textElements: textElements.length,
                articles: articles.length,
                dataTestIds: dataTestIds.length,
                sampleTexts: sampleTexts,
                url: window.location.href,
                hostname: window.location.hostname
            }
        });
        return true;
    }
});

console.log('✅ Reddit content script setup complete');
