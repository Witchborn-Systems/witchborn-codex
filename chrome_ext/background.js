/**
 * Witchborn Codex: Unified Resolution Brain
 * Handles both Omnibox commands and Search Interception via API lookup.
 */

const API_ROOT = "https://witchbornsystems.ai/codex/resolve/mcp";
const PROFILE_FALLBACK = "https://witchbornsystems.ai/#home?query=";

// Central Logic: The "Smart" Resolver
async function handleResolution(identity, tabId) {
    if (!identity) return;

    console.log(`[Brain] Resolving: ${identity}`);

    try {
        // 1. Query the Root Authority API
        const response = await fetch(`${API_ROOT}/${encodeURIComponent(identity)}`);

        let targetUrl = `${PROFILE_FALLBACK}${identity}`; // Default to profile

        if (response.ok) {
            const data = await response.json();

            // 2. Check for App Interface (Sovereign) or Direct URL (Legacy)
            if (data.mode === "sovereign_app" && data.record?.endpoint?.interface) {
                targetUrl = data.record.endpoint.interface;
            } else if (data.mode === "legacy_mcp" && data.endpoint.startsWith('http')) {
                targetUrl = data.endpoint;
            }
        }

        // 3. Execute the Redirect
        console.log(`[Brain] Routing to: ${targetUrl}`);

        if (tabId) {
            chrome.tabs.update(tabId, { url: targetUrl });
        } else {
            chrome.tabs.update({ url: targetUrl });
        }

    } catch (error) {
        console.error("[Brain] Error, falling back to profile:", error);
        // Fallback ensures the user at least sees the 'Not Found' UI
        const fallbackUrl = `${PROFILE_FALLBACK}${identity}`;
        if (tabId) chrome.tabs.update(tabId, { url: fallbackUrl });
        else chrome.tabs.update({ url: fallbackUrl });
    }
}

// TRIGGER 1: Omnibox (User types 'wb' + Space)
chrome.omnibox.onInputEntered.addListener((text) => {
    handleResolution(text.trim().toLowerCase(), null);
});

// TRIGGER 2: Interceptor (User clicked 'ai://' or search hijacked)
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === "resolve_identity") {
        // sender.tab.id ensures we redirect the specific tab that did the search
        handleResolution(request.identity, sender.tab.id);
    }
});