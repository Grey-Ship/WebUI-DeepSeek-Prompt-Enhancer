// Initialize the Deepseek Prompts tab
function initDeepseekPrompts() {
    // Wait for the UI to be ready
    const onUiUpdate = function() {
        const tab = gradioApp().querySelector('#tab_deepseek');
        if (!tab) return;
        
        // Add logo if not already present
        if (!tab.querySelector('.deepseek-logo')) {
            const logo = document.createElement('img');
            logo.src = `${extensionsPath}/deepseek-webui-plugin/static/images/deepseek-logo.png`;
            logo.className = 'deepseek-logo';
            tab.insertBefore(logo, tab.firstChild);
        }
        
        // Add event listeners
        const outputTextarea = gradioApp().querySelector('#deepseek_output textarea');
        if (outputTextarea) {
            outputTextarea.addEventListener('dblclick', function() {
                this.select();
            });
        }
    };
    
    // Check periodically until the UI is ready
    const timer = setInterval(function() {
        if (gradioApp().querySelector('#tab_deepseek')) {
            clearInterval(timer);
            onUiUpdate();
        }
    }, 500);
}

// Initialize when the page loads
document.addEventListener('DOMContentLoaded', initDeepseekPrompts);
