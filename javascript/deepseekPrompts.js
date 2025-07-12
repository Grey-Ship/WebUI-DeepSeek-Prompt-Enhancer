// Initialize the Deepseek Prompts tab with debug logging
function initDeepseekPrompts() {
    console.debug("[Deepseek] Initializing plugin");
    
    const onUiUpdate = function() {
        const tab = gradioApp().querySelector('#tab_deepseek');
        if (!tab) {
            console.debug("[Deepseek] Tab not found yet, waiting...");
            return;
        }
        
        console.debug("[Deepseek] Found tab, setting up UI");
        
        // Add logo if not already present
        if (!tab.querySelector('.deepseek-logo')) {
            console.debug("[Deepseek] Adding logo");
            const logo = document.createElement('img');
            logo.src = `${extensionsPath}/deepseek-webui-plugin/static/images/deepseek-logo.png`;
            logo.className = 'deepseek-logo';
            logo.onerror = function() {
                console.error("[Deepseek] Failed to load logo image");
            };
            tab.insertBefore(logo, tab.firstChild);
        }
        
        // Add event listeners
        const outputTextarea = gradioApp().querySelector('#deepseek_output textarea');
        if (outputTextarea) {
            console.debug("[Deepseek] Adding event listeners");
            outputTextarea.addEventListener('dblclick', function() {
                console.debug("[Deepseek] Prompt output double-clicked, selecting text");
                this.select();
            });
            
            // Monitor for changes in the output
            const observer = new MutationObserver(function(mutations) {
                mutations.forEach(function(mutation) {
                    if (mutation.type === 'characterData' || mutation.type === 'childList') {
                        console.debug("[Deepseek] Prompt output changed:", mutation.target.value?.substring(0, 100));
                    }
                });
            });
            
            observer.observe(outputTextarea, {
                characterData: true,
                childList: true,
                subtree: true
            });
        } else {
            console.warn("[Deepseek] Could not find output textarea");
        }
        
        // Log button clicks
        const buttons = ['generate', 'enhance', 'use', 'clear'];
        buttons.forEach(function(btn) {
            const element = gradioApp().querySelector(`#deepseek_${btn}_btn`);
            if (element) {
                element.addEventListener('click', function() {
                    console.log(`[Deepseek] ${btn.charAt(0).toUpperCase() + btn.slice(1)} button clicked`);
                });
            } else {
                console.warn(`[Deepseek] Could not find ${btn} button`);
            }
        });
        
        console.debug("[Deepseek] UI setup complete");
        clearInterval(timer);
    };
    
    // Check periodically until the UI is ready
    const timer = setInterval(onUiUpdate, 500);
    
    // Log when the script is loaded
    console.info("[Deepseek] Plugin script loaded");
}

// Error handling for initialization
try {
    document.addEventListener('DOMContentLoaded', function() {
        console.debug("[Deepseek] DOM content loaded, initializing");
        initDeepseekPrompts();
    });
    
    // Also try to initialize if DOM is already loaded
    if (document.readyState === 'complete' || document.readyState === 'interactive') {
        console.debug("[Deepseek] DOM already loaded, initializing immediately");
        initDeepseekPrompts();
    }
} catch (e) {
    console.error("[Deepseek] Initialization error:", e);
}
