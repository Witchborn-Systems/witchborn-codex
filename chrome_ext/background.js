/**
 * Witchborn Codex: Sovereign Bridge
 * Routes ai:// requests to the Server-Side Redirector.
 */

const JUMP_ROOT = "https://witchbornsystems.ai/codex/go";

function handleResolution(identity, tabId) {
    if (!identity) return;

    // Remove protocol prefixes and whitespace
    const cleanId = identity.replace(/^ai:\/\/|^mcp:\/\//i, "").trim();

    // Construct the direct Jump URL
    const targetUrl = `${JUMP_ROOT}/${encodeURIComponent(cleanId)}`;

    console.log(`[Brain] Routing to Server: ${targetUrl}`);

    if (tabId) {
        chrome.tabs.update(tabId, { url: targetUrl });
    } else {
        chrome.tabs.query({active: true, currentWindow: true}, function(tabs) {
            if (tabs[0]) chrome.tabs.update(tabs[0].id, { url: targetUrl });
        });
    }
}

// Listen for messages from popup.js or interceptor.js
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === "resolve_identity") {
        const tabId = sender.tab ? sender.tab.id : null;
        handleResolution(request.identity, tabId);

        // Acknowledge receipt to prevent "Receiving end does not exist"
        sendResponse({ status: "resolving" });
    }
    return true; // Keep channel open for async work
});

// Omnibox support
chrome.omnibox.onInputEntered.addListener((text) => {
    handleResolution(text.trim().toLowerCase(), null);
});