/* Food Bridge Custom JavaScript
   Enhances UI/UX with interactive features based on UI/UX Pro Max recommendations
   Using vanilla JavaScript replacements for Bootstrap components
*/

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips (vanilla replacement)
    bootstrapInstance.initTooltips();

    // Initialize popovers (vanilla replacement)
    bootstrapInstance.initPopovers();

    // Initialize toasts (vanilla replacement)
    bootstrapInstance.initToasts();

    // Initialize offcanvas menus (vanilla replacement)
    bootstrapInstance.initOffcanvas();

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
            // Replace Bootstrap Alert with vanilla dismiss
            alert.style.opacity = '0';
            setTimeout(() => {
                if (alert.parentNode) {
                    alert.parentNode.removeChild(alert);
                }
            }, 300); // Match CSS transition
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
        if (row.closest('.table-selectable')) {
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
                    // Vanilla collapse replacement
                    const bsCollapse = bootstrapInstance.get(collapseElement);
                    if (bsCollapse) {
                        bsCollapse.hide();
                    } else {
                        // Fallback: hide by removing show class and setting height
                        collapseElement.classList.remove('show');
                        collapseElement.style.height = '0';
                    }
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
        window.requestAnimationFrame(throttle(toggleBackToTopButton, 100));
    });
    // Initial check
    toggleBackToTopButton();

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
            const bsModal = bootstrapInstance.get(modalEl);
            if (bsModal) {
                bsModal.show();
            } else {
                // Fallback: show by adding classes
                modalEl.classList.add('show');
                modalEl.style.display = 'block';
                document.body.classList.add('modal-open');
                const backdrop = document.createElement('div');
                backdrop.className = 'modal-backdrop fade show';
                document.body.appendChild(backdrop);
            }
        }, 500);
    });

    // Modal trigger handling
    document.addEventListener('click', function(e) {
        const toggle = e.target.closest('[data-bs-toggle="modal"]');
        if (toggle) {
            const targetId = toggle.getAttribute('data-bs-target');
            if (targetId) {
                const modalEl = document.querySelector(targetId);
                if (modalEl) {
                    // Show modal
                    modalEl.classList.add('show');
                    modalEl.style.display = 'block';
                    document.body.classList.add('modal-open');
                    // Add backdrop
                    const backdrop = document.createElement('div');
                    backdrop.className = 'modal-backdrop fade show';
                    document.body.appendChild(backdrop);
                    // Click on backdrop to close
                    backdrop.addEventListener('click', function() {
                        modalEl.classList.remove('show');
                        modalEl.style.display = 'none';
                        document.body.classList.remove('modal-open');
                        backdrop.remove();
                    });
                    // Also handle escape key to close
                    const escapeHandler = function(e) {
                        if (e.key === 'Escape') {
                            modalEl.classList.remove('show');
                            modalEl.style.display = 'none';
                            document.body.classList.remove('modal-open');
                            backdrop.remove();
                            window.removeEventListener('keydown', escapeHandler);
                        }
                    };
                    window.addEventListener('keydown', escapeHandler);
                }
            }
        }
    });

    // Modal dismiss handling
    document.addEventListener('click', function(e) {
        const dismiss = e.target.closest('[data-bs-dismiss="modal"]');
        if (dismiss) {
            const modalEl = dismiss.closest('.modal');
            if (modalEl) {
                modalEl.classList.remove('show');
                modalEl.style.display = 'none';
                document.body.classList.remove('modal-open');
                const backdrop = document.querySelector('.modal-backdrop');
                if (backdrop) {
                    backdrop.remove();
                }
            }
        }
    });
});

// Vanilla JavaScript replacements for Bootstrap components
const bootstrapInstance = {
    // Store instances
    instances: new Map(),

    // Get or create instance
    get: function(element) {
        return this.instances.get(element) || null;
    },

    // Initialize tooltips
    initTooltips: function() {
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.forEach(tooltipTriggerEl => {
            if (!this.instances.has(tooltipTriggerEl)) {
                this.instances.set(tooltipTriggerEl, new Tooltip(tooltipTriggerEl));
            }
        });
    },

    // Initialize popovers
    initPopovers: function() {
        const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
        popoverTriggerList.forEach(popoverTriggerEl => {
            if (!this.instances.has(popoverTriggerEl)) {
                this.instances.set(popoverTriggerEl, new Popover(popoverTriggerEl));
            }
        });
    },

    // Initialize toasts
    initToasts: function() {
        const toastElList = [].slice.call(document.querySelectorAll('.toast'));
        toastElList.forEach(toastEl => {
            if (!this.instances.has(toastEl)) {
                this.instances.set(toastEl, new Toast(toastEl));
            }
        });
    },

    // Initialize offcanvas
    initOffcanvas: function() {
        const offcanvasElementList = [].slice.call(document.querySelectorAll('.offcanvas'));
        offcanvasElementList.forEach(el => {
            if (!this.instances.has(el)) {
                this.instances.set(el, new Offcanvas(el));
            }
        });
    }
};

// Tooltip class (vanilla)
class Tooltip {
    constructor(element) {
        this.element = element;
        this.tooltip = null;
        this.init();
    }

    init() {
        const title = this.element.getAttribute('title') || this.element.getAttribute('data-bs-title');
        if (!title) return;

        // Remove title to prevent browser tooltip
        this.element.removeAttribute('title');
        this.element.setAttribute('data-bs-original-title', title);

        // Create tooltip element
        this.tooltip = document.createElement('div');
        this.tooltip.className = 'tooltip fade show';
        this.tooltip.innerHTML = `<div class="tooltip-arrow"></div><div class="tooltip-inner">${title}</div>`;
        document.body.appendChild(this.tooltip);

        // Position and show
        this.updatePosition();
        this.tooltip.style.opacity = '1';

        // Hide on hide events
        this.element.addEventListener('mouseleave', () => this.hide());
        this.element.addEventListener('focusout', () => this.hide());
    }

    updatePosition() {
        const rect = this.element.getBoundingClientRect();
        const tooltipHeight = this.tooltip.offsetHeight;
        const tooltipWidth = this.tooltip.offsetWidth;

        // Default placement: top
        let top = rect.top - tooltipHeight - 10;
        let left = rect.left + (rect.width / 2) - (tooltipWidth / 2);

        // Adjust if out of viewport
        if (top < 0) {
            // Place at bottom
            top = rect.bottom + 10;
            this.tooltip.querySelector('.tooltip-arrow').style.top = '';
            this.tooltip.querySelector('.tooltip-arrow').style.bottom = '-5px';
        } else {
            this.tooltip.querySelector('.tooltip-arrow').style.top = '';
            this.tooltip.querySelector('.tooltip-arrow').style.bottom = '';
        }

        // Adjust left if needed
        if (left < 0) {
            left = 10;
        } else if (left + tooltipWidth > window.innerWidth) {
            left = window.innerWidth - tooltipWidth - 10;
        }

        this.tooltip.style.top = `${top + window.scrollY}px`;
        this.tooltip.style.left = `${left + window.scrollX}px`;
    }

    hide() {
        if (this.tooltip) {
            this.tooltip.style.opacity = '0';
            setTimeout(() => {
                if (this.tooltip.parentNode) {
                    this.tooltip.parentNode.removeChild(this.tooltip);
                }
            }, 150); // Match CSS transition
        }
    }

    // Static method to hide all tooltips
    static hideAll() {
        document.querySelectorAll('.tooltip').forEach(tip => {
            tip.style.opacity = '0';
            setTimeout(() => {
                if (tip.parentNode) {
                    tip.parentNode.removeChild(tip);
                }
            }, 150);
        });
    }
}

// Popover class (vanilla)
class Popover {
    constructor(element) {
        this.element = element;
        this.popover = null;
        this.init();
    }

    init() {
        const title = this.element.getAttribute('data-bs-title') || '';
        const content = this.element.getAttribute('data-bs-content') || '';
        if (!title && !content) return;

        // Create popover element
        this.popover = document.createElement('div');
        this.popover.className = 'popover fade show';
        this.popinner = document.createElement('div');
        this.popinner.className = 'popover-inner';
        if (title) {
            const titleEl = document.createElement('h3');
            titleEl.className = 'popover-header';
            titleEl.textContent = title;
            this.popinner.appendChild(titleEl);
        }
        const contentEl = document.createElement('div');
        contentEl.className = 'popover-body';
        contentEl.textContent = content;
        this.popinner.appendChild(contentEl);
        this.popover.appendChild(this.popinner);
        document.body.appendChild(this.popover);

        // Position and show
        this.updatePosition();
        this.popover.style.opacity = '1';

        // Hide on click outside or on hide events
        this.element.addEventListener('mouseleave', () => this.hide());
        document.addEventListener('click', (e) => {
            if (!this.popover.contains(e.target) && e.target !== this.element) {
                this.hide();
            }
        });
    }

    updatePosition() {
        const rect = this.element.getBoundingClientRect();
        const popoverHeight = this.popover.offsetHeight;
        const popoverWidth = this.popover.offsetWidth;

        // Default placement: right
        let top = rect.top + (rect.height / 2) - (popoverHeight / 2);
        let left = rect.right + 10;

        // Adjust if out of viewport
        if (left + popoverWidth > window.innerWidth) {
            // Place on left
            left = rect.left - popoverWidth - 10;
        }
        if (top < 0) {
            top = 0;
        }
        if (top + popoverHeight > window.innerHeight) {
            top = window.innerHeight - popoverHeight - 10;
        }

        this.popover.style.top = `${top + window.scrollY}px`;
        this.popover.style.left = `${left + window.scrollX}px`;
    }

    hide() {
        if (this.popover) {
            this.popover.style.opacity = '0';
            setTimeout(() => {
                if (this.popover.parentNode) {
                    this.popover.parentNode.removeChild(this.popover);
                }
            }, 150);
        }
    }
}

// Toast class (vanilla)
class Toast {
    constructor(element) {
        this.element = element;
        this.timeoutId = null;
        this.init();
    }

    init() {
        // If toast has data-bs-autohide="false", don't auto-dismiss
        const autohide = this.element.getAttribute('data-bs-autohide') !== 'false';
        const delay = parseInt(this.element.getAttribute('data-bs-delay')) || 5000;

        if (autohide) {
            this.timeoutId = setTimeout(() => {
                this.hide();
            }, delay);
        }

        // Add click handler to close button
        const closeButton = this.element.querySelector('.btn-close');
        if (closeButton) {
            closeButton.addEventListener('click', () => this.hide());
        }
    }

    hide() {
        if (this.timeoutId) {
            clearTimeout(this.timeoutId);
        }
        this.element.style.opacity = '0';
        this.element.style.transform = 'translateY(-10px)';
        setTimeout(() => {
            if (this.element.parentNode) {
                this.element.parentNode.removeChild(this.element);
            }
        }, 300); // Match CSS transition
    }

    show() {
        if (this.timeoutId) {
            clearTimeout(this.timeoutId);
        }
        this.element.style.opacity = '1';
        this.element.style.transform = 'translateY(0)';
        const delay = parseInt(this.element.getAttribute('data-bs-delay')) || 5000;
        const autohide = this.element.getAttribute('data-bs-autohide') !== 'false';
        if (autohide) {
            this.timeoutId = setTimeout(() => {
                this.hide();
            }, delay);
        }
    }
}

// Offcanvas class (vanilla)
class Offcanvas {
    constructor(element) {
        this.element = element;
        this.backdrop = null;
        this.init();
    }

    init() {
        // Add click handler to toggle buttons
        const triggers = document.querySelectorAll(`[data-bs-toggle="offcanvas"][data-bs-target="#${this.element.id}"]`);
        triggers.forEach(trigger => {
            trigger.addEventListener('click', () => this.toggle());
        });

        // Add click handler to close button inside offcanvas
        const closeBtn = this.element.querySelector('[data-bs-dismiss="offcanvas"]');
        if (closeBtn) {
            closeBtn.addEventListener('click', () => this.hide());
        }

        // Click on backdrop to close
        // (we'll handle this in show method)
    }

    toggle() {
        if (this.element.classList.contains('show')) {
            this.hide();
        } else {
            this.show();
        }
    }

    show() {
        this.element.classList.add('show');
        this.element.style.display = 'block';

        // Create backdrop
        this.backdrop = document.createElement('div');
        this.backdrop.className = 'offcanvas-backdrop fade show';
        document.body.appendChild(this.backdrop);

        // Prevent body scroll
        document.body.style.overflow = 'hidden';

        // Click on backdrop to hide
        this.backdrop.addEventListener('click', () => this.hide());
    }

    hide() {
        this.element.classList.remove('show');
        this.element.style.display = 'none';
        if (this.backdrop) {
            this.backdrop.classList.remove('show');
            setTimeout(() => {
                if (this.backdrop.parentNode) {
                    this.backdrop.parentNode.removeChild(this.backdrop);
                }
            }, 150);
            this.backdrop = null;
        }
        // Restore body scroll
        document.body.style.overflow = '';
    }
}

// Fallback for bootstrapInstance.get when using vanilla replacements
// We'll attach instances to elements directly for simplicity in other parts
// But we keep bootstrapInstance for compatibility with existing code that uses it

// Utility function for throttling
function throttle(func, wait) {
    let timeout;
    return function() {
        const context = this;
        const args = arguments;
        clearTimeout(timeout);
        timeout = setTimeout(() => func.apply(context, args), wait);
    };
}

// Utility function for debouncing
function debounce(func, wait) {
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
    const toast = new Toast(toastElement);
    toast.show();

    // Auto remove after hidden
    toastElement.addEventListener('hidden.bs.toast', function () {
        container.remove();
    });
}

// Export functions for use in templates
window.showToast = showToast;