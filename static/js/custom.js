/* Food Bridge Custom JavaScript
   Enhances UI/UX with interactive features based on UI/UX Pro Max recommendations
*/

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips (Bootstrap)
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
    const tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl)
    });

    // Initialize popovers (Bootstrap)
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'))
    const popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl)
    });

    // Initialize toasts
    const toastElList = [].slice.call(document.querySelectorAll('.toast'))
    const toastList = toastElList.map(function (toastEl) {
        return new bootstrap.Toast(toastEl)
    });

    // Initialize offcanvas menus
    const offcanvasElementList = [].slice.call(document.querySelectorAll('.offcanvas'))
    const offcanvasList = offcanvasElementList.map(function (el) {
        return new bootstrap.Offcanvas(el)
    });

    // Enhanced form validation with visual feedback
    const forms = document.querySelectorAll('.needs-validation');
    forms.forEach(form => {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();

                // Add shake animation to invalid fields
                const invalidFields = form.querySelectorAll(':invalid:not([type="submit"])');
                invalidFields.forEach(field => {
                    field.classList.add('is-invalid');
                    // Add shake animation
                    field.animate([
                        { transform: 'translateX(0)' },
                        { transform: 'translateX(-5px)' },
                        { transform: 'translateX(5px)' },
                        { transform: 'translateX(-5px)' },
                        { transform: 'translateX(5px)' },
                        { transform: 'translateX(0)' }
                    ], {
                        duration: 300,
                        iterations: 1
                    });
                });
            }
            form.classList.add('was-validated');
        });

        // Real-time validation feedback
        const inputs = form.querySelectorAll('input, select, textarea');
        inputs.forEach(input => {
            input.addEventListener('input', function() {
                if (this.checkValidity()) {
                    this.classList.remove('is-invalid');
                    this.classList.add('is-valid');
                } else {
                    this.classList.remove('is-valid');
                    this.classList.add('is-invalid');
                }
            });
        });
    });

    // Smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                e.preventDefault();
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });

                // Close mobile menu if open
                const navbarToggler = document.querySelector('.navbar-toggler');
                if (navbarToggler && !navbarToggler.classList.contains('collapsed')) {
                    navbarToggler.click();
                }
            }
        });
    });

    // Enhanced button feedback with ripple effect
    document.querySelectorAll('button, .btn, input[type="submit"], input[type="button"]').forEach(button => {
        // Skip buttons that are disabled or have specific classes
        if (button.disabled || button.closest('.no-ripple')) return;

        button.addEventListener('click', function(e) {
            const rect = this.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;

            // Create ripple element
            const ripple = document.createElement('div');
            ripple.style.position = 'absolute';
            ripple.style.left = `${x}px`;
            ripple.style.top = `${y}px`;
            ripple.style.width = '0';
            ripple.style.height = '0';
            ripple.style.borderRadius = '50%';
            ripple.style.backgroundColor = 'rgba(255, 255, 255, 0.3)';
            ripple.style.transform = 'translate(-50%, -50%)';
            ripple.style.pointerEvents = 'none';
            ripple.style.transition = 'width 0.6s ease, height 0.6s ease, opacity 0.6s ease';

            // Add ripple to button
            const position = getComputedStyle(this).position;
            if (position === 'static') {
                this.style.position = 'relative';
            }
            this.appendChild(ripple);

            // Animate ripple
            setTimeout(() => {
                ripple.style.width = `${Math.max(this.offsetWidth, this.offsetHeight) * 2}px`;
                ripple.style.height = `${Math.max(this.offsetWidth, this.offsetHeight) * 2}px`;
                ripple.style.opacity = '0';
            }, 10);

            // Remove ripple after animation
            setTimeout(() => {
                if (ripple.parentNode) {
                    ripple.parentNode.removeChild(ripple);
                }
            }, 600);
        });
    });

    // Auto-dismiss alerts after delay
    const alerts = document.querySelectorAll('.alert-auto-dismiss');
    alerts.forEach(alert => {
        setTimeout(() => {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000); // 5 seconds
    });

    // Enhanced table interactivity
    document.querySelectorAll('.table-hover tbody tr').forEach(row => {
        row.addEventListener('mouseenter', function() {
            this.style.backgroundColor = 'rgba(5, 150, 105, 0.05)';
        });

        row.addEventListener('mouseleave', function() {
            this.style.backgroundColor = '';
        });

        // Add click-to-select functionality for tables with checkboxes
        if (this.closest('.table-selectable')) {
            row.style.cursor = 'pointer';
            row.addEventListener('click', function(e) {
                // Skip if clicking on a button, link, or input
                if (e.target.tagName.match(/BUTTON|A|INPUT|TEXTAREA|SELECT/)) return;

                const checkbox = this.querySelector('input[type="checkbox"]');
                if (checkbox) {
                    checkbox.checked = !checkbox.checked;
                    // Trigger change event
                    checkbox.dispatchEvent(new Event('change'));
                }
            });
        }
    });

    // Lazy loading for images (if not native)
    if (!('loading' in HTMLImageElement.prototype)) {
        const lazyImages = document.querySelectorAll('img[loading="lazy"]');
        const observer = new IntersectionObserver((entries, observer) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    img.src = img.dataset.src;
                    observer.unobserve(img);
                }
            });
        });

        lazyImages.forEach(img => {
            observer.observe(img);
        });
    }

    // Handle offline/online status
    function updateOnlineStatus() {
        const statusIndicator = document.getElementById('connection-status');
        if (statusIndicator) {
            if (navigator.onLine) {
                statusIndicator.classList.remove('bg-danger');
                statusIndicator.classList.add('bg-success');
                statusIndicator.title = 'Online';
            } else {
                statusIndicator.classList.remove('bg-success');
                statusIndicator.classList.add('bg-danger');
                statusIndicator.title = 'Offline';
            }
        }
    }

    window.addEventListener('online', updateOnlineStatus);
    window.addEventListener('offline', updateOnlineStatus);
    updateOnlineStatus(); // Initial check

    // Form enhancement: show password toggle
    document.querySelectorAll('.password-toggle').forEach(wrapper => {
        const input = wrapper.querySelector('input[type="password"]');
        const toggle = wrapper.querySelector('.toggle-password');

        if (input && toggle) {
            toggle.addEventListener('click', function() {
                const type = input.getAttribute('type') === 'password' ? 'text' : 'password';
                input.setAttribute('type', type);
                this.classList.toggle('bi-eye');
                this.classList.toggle('bi-eye-slash');
                this.setAttribute('aria-label',
                    type === 'password' ? 'Show password' : 'Hide password'
                );
            });
        }
    });

    // Character counter for textareas
    document.querySelectorAll('.char-counter').forEach(container => {
        const textarea = container.querySelector('textarea');
        const counter = container.querySelector('.counter-value');
        const maxLength = textarea.getAttribute('maxlength');

        if (textarea && counter && maxLength) {
            const updateCounter = () => {
                const remaining = maxLength - textarea.value.length;
                counter.textContent = remaining;
                if (remaining < 10) {
                    counter.classList.add('text-danger');
                } else {
                    counter.classList.remove('text-danger');
                }
            };

            textarea.addEventListener('input', updateCounter);
            updateCounter(); // Initial call

            // Also update on paste
            textarea.addEventListener('paste', () => {
                setTimeout(updateCounter, 0);
            });
        }
    });

    // File input enhancement - show selected file name with preview
    document.querySelectorAll('.custom-file-input').forEach(input => {
        const label = input.nextElementSibling;
        const previewContainer = document.querySelector(`#${input.id}-preview`);

        if (label && label.classList.contains('custom-file-label')) {
            // Set initial label text
            label.textContent = label.dataset.browse || 'Choose file';

            input.addEventListener('change', function() {
                // Update filename
                const fileName = this.files.length > 0 ?
                    Array.from(this.files).map(file => file.name).join(', ') :
                    label.dataset.browse || 'Choose file';
                label.textContent = fileName;

                // Handle image preview
                if (previewContainer && this.files && this.files[0]) {
                    const file = this.files[0];
                    if (file.type.startsWith('image/')) {
                        const reader = new FileReader();
                        reader.onload = function(e) {
                            previewContainer.innerHTML = `<img src="${e.target.result}" class="img-fluid rounded" alt="Preview">`;
                        };
                        reader.readAsDataURL(file);
                    } else {
                        previewContainer.innerHTML = `<p class="text-muted">File selected: ${file.name}</p>`;
                    }
                }
            });
        }
    });

    // Accordion enhancement - close others when opening one
    document.querySelectorAll('.accordion').forEach(accordion => {
        accordion.addEventListener('show.bs.collapse', function(e) {
            // Close all other items in this accordion
            const items = this.querySelectorAll('.accordion-item');
            items.forEach(item => {
                const collapseElement = item.querySelector('.accordion-collapse');
                if (collapseElement !== e.target && collapseElement.classList.contains('show')) {
                    new bootstrap.Collapse(collapseElement, {
                        toggle: false
                    }).hide();
                }
            });
        });
    });

    // Back to top button functionality
    const backToTopButton = document.createElement('button');
    backToTopButton.innerHTML = '<i class="bi bi-arrow-up"></i>';
    backToTopButton.className = 'btn-back-to-top btn btn-primary btn-sm rounded-circle position-fixed';
    backToTopButton.style.bottom = '2rem';
    backToTopButton.style.right = '2rem';
    backToTopButton.style.display = 'none';
    backToTopButton.style.zIndex = '1000';
    backToTopButton.setAttribute('aria-label', 'Back to top');
    document.body.appendChild(backToTopButton);

    backToTopButton.addEventListener('click', () => {
        window.scrollTo({
            top: 0,
            behavior: 'smooth'
        });
    });

    // Show/hide back to top button based on scroll position
    function toggleBackToTopButton() {
        if (window.scrollY > 300) {
            backToTopButton.style.display = 'block';
        } else {
            backToTopButton.style.display = 'none';
        }
    }

    window.addEventListener('scroll', () => {
        // Throttle the scroll event
        window.requestAnimationFrame(toggleBackToTopButton);
    });
    // Initial check
    throttle(toggleBackToTopButton, 100)();

    // Add animation to elements as they enter viewport
    const animateElements = document.querySelectorAll('.animate-on-scroll');
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animate-in');
                // Uncomment if you want to animate only once
                // observer.unobserve(entry.target);
            }
        });
    }, observerOptions);

    animateElements.forEach(el => {
        observer.observe(el);
    });

    // Initialize any modals that should auto-open
    const autoOpenModals = document.querySelectorAll('.modal-auto-open');
    autoOpenModals.forEach(modalEl => {
        // Delay slightly to ensure DOM is ready
        setTimeout(() => {
            const modal = new bootstrap.Modal(modalEl);
            modal.show();
        }, 500);
    });
});

// Utility function for throttling
function funcWait(func, wait) {
    let timeout;
    return function() {
        const context = this;
        const args = arguments;
        clearTimeout(timeout);
        timeout = setTimeout(() => func.apply(context, args), wait);
    };
}

// Utility function to show toast notification
function showToast(message, type = 'info', delay = 5000) {
    // Remove any existing toasts
    const existingToasts = document.querySelectorAll('.toast-container');
    existingToasts.forEach(toast => toast.remove());

    // Create toast container
    const container = document.createElement('div');
    container.className = 'toast-container position-fixed bottom-0 end-0 p-3';
    container.style.zIndex = '1055';

    // Determine toast variant
    let bgVariant = 'info';
    if (type === 'success') bgVariant = 'success';
    else if (type === 'error') bgVariant = 'danger';
    else if (type === 'warning') bgVariant = 'warning';

    // Create toast
    const toastHTML = `
        <div class="toast text-bg-${bgVariant} align-items-center"
             role="alert" aria-live="assertive" aria-atomic="true">
            <div class="d-flex">
                <div class="toast-body">
                    ${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto"
                        data-bs-dismiss="toast" aria-label="Close"></button>
            </div>
        </div>
    `;

    container.innerHTML = toastHTML;
    document.body.appendChild(container);

    const toastElement = container.querySelector('.toast');
    const toast = new bootstrap.Toast(toastElement, { delay: delay });
    toast.show();

    // Auto remove after hidden
    toastElement.addEventListener('hidden.bs.toast', function () {
        container.remove();
    });
}

// Export functions for use in templates
window.showToast = showToast;