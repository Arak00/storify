/**
 * Storify - Main JavaScript File
 */

document.addEventListener('DOMContentLoaded', function() {
    console.log('Storify application initialized');
    
    // Initialize all tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    const tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Auto-dismiss alerts after 5 seconds
    setTimeout(function() {
        const alerts = document.querySelectorAll('.alert');
        alerts.forEach(function(alert) {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        });
    }, 5000);
    
    // Template selection in onboarding
    const templateCards = document.querySelectorAll('.template-card');
    templateCards.forEach(function(card) {
        card.addEventListener('click', function() {
            // Remove selected class from all cards
            templateCards.forEach(function(c) {
                c.classList.remove('selected');
            });
            
            // Add selected class to clicked card
            this.classList.add('selected');
            
            // Update hidden input with selected template
            const templateInput = document.getElementById('selected_template');
            if (templateInput) {
                templateInput.value = this.dataset.template;
            }
        });
    });
    
    // Handle subdomain input validation
    const subdomainInput = document.getElementById('subdomain');
    if (subdomainInput) {
        subdomainInput.addEventListener('input', function() {
            // Remove spaces, special characters and convert to lowercase
            this.value = this.value.toLowerCase().replace(/[^a-z0-9-]/g, '');
            
            // Update preview
            const subdomainPreview = document.getElementById('subdomain-preview');
            if (subdomainPreview) {
                subdomainPreview.textContent = this.value || 'your-name';
            }
        });
    }
    
    // Handle file uploads with preview
    const fileInputs = document.querySelectorAll('input[type="file"][data-preview]');
    fileInputs.forEach(function(input) {
        input.addEventListener('change', function() {
            const previewElement = document.getElementById(this.dataset.preview);
            if (previewElement && this.files && this.files[0]) {
                const reader = new FileReader();
                
                reader.onload = function(e) {
                    previewElement.src = e.target.result;
                };
                
                reader.readAsDataURL(this.files[0]);
            }
        });
    });
    
    // Copy to clipboard functionality
    const copyButtons = document.querySelectorAll('.copy-to-clipboard');
    copyButtons.forEach(function(button) {
        button.addEventListener('click', function() {
            const textToCopy = this.dataset.clipboard;
            
            navigator.clipboard.writeText(textToCopy).then(function() {
                // Change button text temporarily
                const originalText = button.textContent;
                button.textContent = 'Copied!';
                
                setTimeout(function() {
                    button.textContent = originalText;
                }, 2000);
            }).catch(function(err) {
                console.error('Could not copy text: ', err);
            });
        });
    });
    
    // Confirm dialog for dangerous actions
    const confirmButtons = document.querySelectorAll('[data-confirm]');
    confirmButtons.forEach(function(button) {
        button.addEventListener('click', function(e) {
            if (!confirm(this.dataset.confirm)) {
                e.preventDefault();
            }
        });
    });
});

/**
 * Show a loading spinner
 * @param {Element} element - The element to show the spinner in
 * @param {string} size - Size of the spinner (sm, md, lg)
 * @returns {void}
 */
function showSpinner(element, size = 'md') {
    const originalContent = element.innerHTML;
    element.setAttribute('data-original-content', originalContent);
    element.disabled = true;
    element.innerHTML = `<span class="spinner-border spinner-border-${size}" role="status" aria-hidden="true"></span> Loading...`;
}

/**
 * Hide the loading spinner
 * @param {Element} element - The element with the spinner
 * @returns {void}
 */
function hideSpinner(element) {
    const originalContent = element.getAttribute('data-original-content');
    element.innerHTML = originalContent;
    element.disabled = false;
}

/**
 * Make an AJAX request
 * @param {string} url - The URL to request
 * @param {Object} options - Request options
 * @returns {Promise} - The fetch promise
 */
function makeRequest(url, options = {}) {
    const defaultOptions = {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
            'X-Requested-With': 'XMLHttpRequest'
        },
        credentials: 'same-origin'
    };
    
    const mergedOptions = { ...defaultOptions, ...options };
    
    if (mergedOptions.body && typeof mergedOptions.body === 'object') {
        mergedOptions.body = JSON.stringify(mergedOptions.body);
    }
    
    return fetch(url, mergedOptions)
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error ${response.status}`);
            }
            return response.json();
        });
} 