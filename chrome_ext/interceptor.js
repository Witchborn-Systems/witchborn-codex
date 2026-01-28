// Witchborn Codex: Search Interceptor (The Spotter)
// Detects ai:// search results and offloads resolution to the background brain.

(function() {
    const params = new URLSearchParams(window.location.search);
    const query = params.get('q') || '';

    const cleanQuery = decodeURIComponent(query).trim();

    if (cleanQuery.toLowerCase().startsWith('ai://')) {
        // 1. Stop the Google/Bing page from rendering further
        window.stop();

        // 2. Extract Identity
        const identity = cleanQuery.substring(5); // Remove 'ai://'

        // 3. Hand off to the Brain (background.js)
        // We use runtime.sendMessage so the Service Worker can use its
        // high-privilege fetch() to find the App Interface.
        chrome.runtime.sendMessage({
            action: "resolve_identity",
            identity: identity
        });
    }
})();