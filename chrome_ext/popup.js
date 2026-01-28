document.addEventListener('DOMContentLoaded', function() {
    const identInput = document.getElementById('ident');
    const traceBtn = document.getElementById('traceBtn');

    identInput.addEventListener('focus', function() {
        if (['', 'name@authority', 'witchborn@webai'].includes(this.value.toLowerCase())) {
            this.value = '';
        }
    });

    traceBtn.addEventListener('click', () => {
        const id = identInput.value.trim().toLowerCase();
        if (id) {
            // Attempt to contact background script
            chrome.runtime.sendMessage({
                action: "resolve_identity",
                identity: id
            }, (response) => {
                if (chrome.runtime.lastError) {
                    console.warn("Connection failed: Background script might be reloading.");
                }
            });
        }
    });
});