/**
 * MAIN.js - App initialization and setup
 */

document.addEventListener('DOMContentLoaded', () => {
    // Initialize dashboard when authenticated content is shown
    const observer = new MutationObserver(() => {
        const mainContent = document.getElementById('main-content');
        if (mainContent.style.display !== 'none' && !mainContent.innerHTML.includes('id="jobsContainer"')) {
            dashboard.init();
        }
    });

    observer.observe(document.getElementById('main-content'), { 
        attributes: true, 
        attributeFilter: ['style'] 
    });

    // Initialize dashboard if already authenticated
    if (document.getElementById('main-content').style.display !== 'none') {
        dashboard.init();
    }
});
