/*
   Food Bridge Modern JavaScript Utilities
   Enhanced version with modern ES6+ features, modular design, and improved performance
*/

// IIFE to avoid polluting global scope
(function() {
  // Utility Functions
  const utils = {
    // Debounce function for performance optimization
    debounce: (func, wait) => {
      let timeout;
      return function executedFunction(...args) {
        const later = () => {
          clearTimeout(timeout);
          func.apply(this, args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
      };
    },

    // Throttle function for rate limiting
    throttle: (func, limit) => {
      let inThrottle;
      return function executedFunction(...args) {
        if (!inThrottle) {
          func.apply(this, args);
          inThrottle = true;
          setTimeout(() => (inThrottle = false), limit);
        }
      };
    },

    // Check if element is in viewport
    isInViewport: (element) => {
      const rect = element.getBoundingClientRect();
      return (
        rect.top >= 0 &&
        rect.left >= 0 &&
        rect.bottom <= (window.innerHeight || document.documentElement.clientHeight) &&
        rect.right <= (window.innerWidth || document.documentElement.clientWidth)
      );
    },

    // Simple store for component instances
    _instances: new Map(),

    getInstance: (element, key) => {
      if (!element) return null;
      const elementKey = `${element.dataset.uid || element}-${key}`;
      return utils._instances.get(elementKey) || null;
    },

    setInstance: (element, key, instance) => {
      if (!element) return;
      const elementKey = `${element.dataset.uid || element}-${key}`;
      utils._instances.set(elementKey, instance);
    },

    // Format number with commas
    formatNumber: (num) => {
      return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
    },

    // Truncate text with ellipsis
    truncateText: (text, maxLength) => {
      if (!text || text.length <= maxLength) return text;
      return `${text.slice(0, Math.max(0, maxLength - 3))}...`;
    },

    // Convert date to relative time (e.g., "2 hours ago")
    timeAgo: (date) => {
      const seconds = Math.floor((Date.now() - new Date(date)) / 1000);
      let interval = Math.floor(seconds / 31536000);

      if (interval > 1) return `${interval} years ago`;
      interval = Math.floor(seconds / 2592000);
      if (interval > 1) return `${interval} months ago`;
      interval = Math.floor(seconds / 86400);
      if (interval > 1) return `${interval} days ago`;
      interval = Math.floor(seconds / 3600);
      if (interval > 1) return `${interval} hours ago`;
      interval = Math.floor(seconds / 60);
      if (interval > 1) return `${interval} minutes ago`;
      return `${Math.floor(seconds)} seconds ago`;
    }
  };

  // Component Classes
  class Tooltip {
    constructor(element, options = {}) {
      {
  typeof element === 'string' ? document.querySelector(element) : element
};
      this.options = {
        placement: 'top',
        trigger: 'hover focus',
        ...options
      };
      this.tooltip = null;
      this.visible = false;
      this.init();
    }

    init() {
      // Skip if already initialized
      if (this.element.dataset.tooltipInitialized) return;

      this.element.dataset.tooltipInitialized = 'true';
      this.title = this.element.getAttribute('title') || this.element.getAttribute('data-bs-title') || '';

      if (!this.title) return;

      // Remove title to prevent browser tooltip
      this.element.removeAttribute('title');

      // Create tooltip element
      this.tooltip = document.createElement('div');
      this.tooltip.className = 'tooltip fade';
      this.tooltip.innerHTML = `
        <div class="tooltip-arrow"></div>
        <div class="tooltip-inner">${this.title}</div>
      `;
      document.body.appendChild(this.tooltip);

      // Event listeners
      this._bindEvents();
    }

    _bindEvents() {
      const showEvents = this.options.trigger.includes('hover') ? ['mouseenter', 'focus'] : [];
      const hideEvents = this.options.trigger.includes('hover') ? ['mouseleave', 'blur'] : ['focusout'];

      showEvents.forEach(event => this.element.addEventListener(event, () => this.show()));
      hideEvents.forEach(event => this.element.addEventListener(event, () => this.hide()));
    }

    show() {
      if (this.visible || !this.title) return;

      this._position();
      this.tooltip.style.opacity = '1';
      this.tooltip.style.visibility = 'visible';
      this.visible = true;
    }

    hide() {
      if (!this.visible) return;
      this.tooltip.style.opacity = '0';
      this.tooltip.style.visibility = 'hidden';
      this.visible = false;
    }

    _position() {
      if (!this.tooltip) return;

      const rect = this.element.getBoundingClientRect();
      const tooltipWidth = this.tooltip.offsetWidth;
      const tooltipHeight = this.tooltip.offsetHeight;

      let top, left;

      switch (this.options.placement) {
        case 'top':
          top = rect.top - tooltipHeight - 8;
          left = rect.left + (rect.width / 2) - (tooltipWidth / 2);
          this._positionArrow('bottom');
          break;
        case 'bottom':
          top = rect.bottom + 8;
          left = rect.left + (rect.width / 2) - (tooltipWidth / 2);
          this._positionArrow('top');
          break;
        case 'left':
          top = rect.top + (rect.height / 2) - (tooltipHeight / 2);
          left = rect.left - tooltipWidth - 8;
          this._positionArrow('right');
          break;
        case 'right':
          top = rect.top + (rect.height / 2) - (tooltipHeight / 2);
          left = rect.right + 8;
          this._positionArrow('left');
          break;
        default:
          top = rect.top - tooltipHeight - 8;
          left = rect.left + (rect.width / 2) - (tooltipWidth / 2);
          this._positionArrow('bottom');
      }

      // Adjust for viewport boundaries
      const viewportPadding = 8;
      if (left < viewportPadding) left = viewportPadding;
      if (left + tooltipWidth > window.innerWidth - viewportPadding)
        left = window.innerWidth - tooltipWidth - viewportPadding;
      if (top < viewportPadding) top = viewportPadding;
      if (top + tooltipHeight > window.innerHeight - viewportPadding)
        top = window.innerHeight - tooltipHeight - viewportPadding;

      this.tooltip.style.top = `${window.pageYOffset + top}px`;
      this.tooltip.style.left = `${window.pageXOffset + left}px`;
    }

    _positionArrow(position) {
      if (!this.tooltip) return;
      const arrow = this.tooltip.querySelector('.tooltip-arrow');
      if (arrow) {
        arrow.style.top = '';
        arrow.style.bottom = '';
        arrow.style.left = '';
        arrow.style.right = '';

        if (position === 'top') {
          arrow.style.bottom = '0';
          arrow.style.borderWidth = '5px 5px 0';
          arrow.style.borderColor = 'transparent transparent transparent #000';
        } else if (position === 'bottom') {
          arrow.style.top = '0';
          arrow.style.borderWidth = '0 5px 5px';
          arrow.style.borderColor = 'transparent #000 transparent';
        } else if (position === 'left') {
          arrow.style.right = '0';
          arrow.style.borderWidth = '5px 0 5px 5px';
          arrow.style.borderColor = 'transparent transparent #000 transparent';
        } else if (position === 'right') {
          arrow.style.left = '0';
          arrow.style.borderWidth = '5px 5px 5px 0';
          arrow.style.borderColor = '#000 transparent transparent transparent';
        }
      }
    }

    dispose() {
      if (this.tooltip && this.tooltip.parentNode) {
        this.tooltip.parentNode.removeChild(this.tooltip);
      }
      this.element.removeEventListener('mouseenter', this.show);
      this.element.removeEventListener('mouseleave', this.hide);
      this.element.removeEventListener('focus', this.show);
      this.element.removeEventListener('blur', this.hide);
      this.element.removeAttribute('data-tooltip-initialized');
    }
  }

  class Dropdown {
    constructor(element, options = {}) {
      this.element = typeof element === 'string' ? document.querySelector(element) : element;
      this.options = {
        dropdownMenu: '.dropdown-menu',
        toggleClass: 'show',
        ...options
      };
      this.menu = null;
      this.visible = false;
      this.init();
    }

    init() {
      if (this.element.dataset.dropdownInitialized) return;
      this.element.dataset.dropdownInitialized = 'true';

      this.menu = this.element.querySelector(this.options.dropdownMenu);
      if (!this.menu) return;

      // Event listeners
      this.element.addEventListener('click', (e) => {
        e.preventDefault();
        e.stopPropagation();
        this.toggle();
      });

      // Close when clicking outside
      document.addEventListener('click', (e) => {
        if (this.visible && !this.element.contains(e.target) && !this.menu.contains(e.target)) {
          this.hide();
        }
      });

      // Close with Escape key
      document.addEventListener('keydown', (e) => {
        if (this.visible && e.key === 'Escape') {
          this.hide();
        }
      });
    }

    toggle() {
      if (this.visible) {
        this.hide();
      } else {
        this.show();
      }
    }

    show() {
      if (this.visible) return;
      this.element.classList.add(this.options.toggleClass);
      this.menu.classList.add(this.options.toggleClass);
      this.visible = true;
    }

    hide() {
      if (!this.visible) return;
      this.element.classList.remove(this.options.toggleClass);
      this.menu.classList.remove(this.options.toggleClass);
      this.visible = false;
    }

    dispose() {
      this.element.removeEventListener('click', this.toggle);
      document.removeEventListener('click', this._outsideClickHandler);
      document.removeEventListener('keydown', this._escapeKeyHandler);
      this.element.dataset.dropdownInitialized = 'false';
    }
  }

  class Modal {
    constructor(element, options = {}) {
      this.element = typeof element === 'string' ? document.querySelector(element) : element;
      this.options = {
        backdrop: true,
        keyboard: true,
        focus: true,
        show: true,
        ...options
      };
      this.dialog = null;
      this.backdrop = null;
      this.isShown = false;
      this.isBodyOverflowing = false;
      this.scrollbarWidth = 0;
      this.ignoreBackdropClick = false;
      this.isTransitioning = false;
      this.originalBodyPadding = 0;
      this.scrollbarWidth = 0;

      if (this.options.show) {
        this.show();
      }
    }

    init() {
      if (this.element.dataset.modalInitialized) return;
      this.element.dataset.modalInitialized = 'true';

      this.dialog = this.element.querySelector('.modal-dialog');

      // Click handler for backdrop
      this.element.addEventListener('click', (e) => {
        if (this.ignoreBackdropClick) {
          this.ignoreBackdropClick = false;
          return;
        }

        if (e.target === this.element) {
          this.hide();
        }
      });

      // Keyboard navigation
      document.addEventListener('keydown', (e) => {
        if (this.isShown && this.options.keyboard && e.key === 'Escape') {
          this.hide();
        }
      });
    }

    show() {
      if (this.isShown || this.isTransitioning) return;

      const showEvent = new Event('show.bs.modal');
      this.element.dispatchEvent(showEvent);
      if (showEvent.defaultPrevented) return;

      this.isShown = true;
      this._checkScrollbar();
      this._setScrollbar();

      document.body.classList.add('modal-open');

      this.element.style.display = 'block';
      this.element.removeAttribute('aria-hidden');
      this.element.setAttribute('aria-modal', 'true');
      this.element.setAttribute('role', 'dialog');

      this._setEscapeEvent();
      this._setResizeEvent();

      if (this.options.backdrop) {
        this._showBackdrop(() => this._showElement(this.dialog));
      } else {
        this._showElement(this.dialog);
      }
    }

    hide() {
      if (!this.isShown || this.isTransitioning) return;

      const hideEvent = new Event('hide.bs.modal');
      this.element.dispatchEvent(hideEvent);
      if (hideEvent.defaultPrevented) return;

      this.isShown = false;
      this._setEscapeEvent();
      this._setResizeEvent();

      document.removeEventListener('keydown', this._keydownCallback);
      this.element.classList.remove('show');
      this.element.setAttribute('aria-hidden', 'true');
      this.element.removeAttribute('aria-modal');
      this.element.removeAttribute('role');

      this._hideModal();
    }

    _showBackdrop(callback) {
      this.backdrop = document.createElement('div');
      this.backdrop.className = 'modal-backdrop fade';

      if (this.options.backdrop === 'static') {
        this.backdrop.className += ' static';
      }

      if (this.isShown) {
        document.body.appendChild(this.backdrop);
        this.backdrop.addEventListener('click', (e) => {
          if (this.options.backdrop === 'static') {
            this.element.focus();
          } else {
            this.hide();
          }
        });

        // Trigger reflow for animation
        this.backdrop.offsetWidth;
        this.backdrop.classList.add('show');

        if (callback) callback();
      } else if (callback) {
        callback();
      }
    }

    _hideModal() {
      this.element.style.display = 'none';
      this._hideBackdrop(() => {
        document.body.classList.remove('modal-open');
        this._resetAdjustments();
        this._resetScrollbar();
        this.element.dispatchEvent(new Event('hidden.bs.modal'));
      });
    }

    _removeBackdrop() {
      this.backdrop.parentNode.removeChild(this.backdrop);
      this.backdrop = null;
    }

    _showBackdrop(callback) {
      this._showBackdrop(callback);
    }

    _hideBackdrop(callback) {
      if (!this.backdrop) {
        if (callback) callback();
        return;
      }

      this.backdrop.classList.remove('show');

      const callbackRemove = () => {
        this._removeBackdrop();
        if (callback) callback();
      };

      if (this._isAnimated()) {
        this.backdrop.addEventListener('transitionend', callbackRemove);
      } else {
        callbackRemove();
      }
    }

    _isAnimated() {
      return this.element.classList.contains('fade');
    }

    _setEscapeEvent() {
      if (this.isShown && this.options.keyboard) {
        this._keydownCallback = (e) => {
          if (e.key === 'Escape') {
            this.hide();
          }
        };
        document.addEventListener('keydown', this._keydownCallback);
      } else if (!this.isShown) {
        document.removeEventListener('keydown', this._keydownCallback);
      }
    }

    _setResizeEvent() {
      if (this.isShown) {
        window.addEventListener('resize', this._updateDialog);
      } else {
        window.removeEventListener('resize', this._updateDialog);
      }
    }

    _hideModal() {
      this.element.style.display = 'none';
      this._hideBackdrop(() => {
        document.body.classList.remove('modal-open');
        this._resetAdjustments();
        this._resetScrollbar();
        this.element.dispatchEvent(new Event('hidden.bs.modal'));
      });
    }

    _removeBackdrop() {
      if (this.backdrop) {
        this.backdrop.parentNode.removeChild(this.backdrop);
        this.backdrop = null;
      }
    }

    _showElement(element) {
      const isAnimated = this._isAnimated();

      if (!this.element.parentNode ||
          this.element.parentNode.nodeType !== Node.ELEMENT_NODE) {
        document.body.appendChild(this.element);
      }

      this.element.style.display = 'block';
      this.element.removeAttribute('aria-hidden');
      this.element.setAttribute('aria-modal', 'true');
      this.element.setAttribute('role', 'dialog');

      if (isAnimated) {
        // Trigger reflow for animation
        this.element.offsetHeight;
      }

      this.element.classList.add('show');
      this.element.scrollTop = 0;

      if (this.options.focus) {
        this._enforceFocus();
      }

      this.element.dispatchEvent(new Event('shown.bs.modal'));
    }

    _enforceFocus() {
      document.addEventListener('focusin', (e) => {
        if (this.element !== e.target &&
            !this.element.contains(e.target)) {
          this.element.focus();
        }
      });
    }

    _setScrollbar() {
      const scrollBarWidth = window.innerWidth - document.documentElement.clientWidth;
      if (scrollBarWidth > 0) {
        document.body.style.paddingRight = `${scrollBarWidth}px`;
      }
    }

    _resetScrollbar() {
      document.body.style.paddingRight = '';
    }

    _measureScrollbar() {
      const scrollDiv = document.createElement('div');
      scrollDiv.className = 'modal-scrollbar-measure';
      document.body.appendChild(scrollDiv);
      this.scrollbarWidth = scrollDiv.offsetWidth - scrollDiv.clientWidth;
      document.body.removeChild(scrollDiv);
    }

    _adjustDialog() {
      const isOverflowing = this.element.scrollHeight > document.documentElement.clientHeight;
      this.style.paddingLeft = !this.bodyIsOverflowing && isOverflowing ? `${this.scrollbarWidth}px` : '';
      this.style.paddingRight = this.bodyIsOverflowing && !isOverflowing ? `${this.scrollbarWidth}px` : '';
    }

    _resetAdjustments() {
      this.element.style.paddingLeft = '';
      this.element.style.paddingRight = '';
    }
  }

  // Initialize components on DOMContentLoaded
  document.addEventListener('DOMContentLoaded', () => {
    // Initialize tooltips
    document.querySelectorAll('[data-bs-toggle="tooltip"]').forEach(el => {
      new Tooltip(el);
    });

    // Initialize dropdowns
    document.querySelectorAll('[data-bs-toggle="dropdown"]').forEach(el => {
      new Dropdown(el);
    });

    // Initialize modals
    document.querySelectorAll('[data-bs-toggle="modal"]').forEach(button => {
      button.addEventListener('click', (e) => {
        e.preventDefault();
        const target = document.querySelector(button.getAttribute('data-bs-target'));
        if (target) {
          new Modal(target);
        }
      });
    });

    // Enhance form validation
    const forms = document.querySelectorAll('.needs-validation');
    forms.forEach(form => {
      form.addEventListener('submit', (event) => {
        if (!form.checkValidity()) {
          event.preventDefault();
          event.stopPropagation();

          // Add shake animation to invalid fields
          const invalidFields = form.querySelectorAll(':invalid:not([type="submit"])');
          invalidFields.forEach(field => {
            field.classList.add('is-invalid');
            // Add shake animation
            const animation = [
              { transform: 'translateX(0)' },
              { transform: 'translateX(-5px)' },
              { transform: 'translateX(5px)' },
              { transform: 'translateX(-5px)' },
              { transform: 'translateX(5px)' },
              { transform: 'translateX(0)' }
            ];
            const timing = { duration: 300, iterations: 1 };
            field.animate(animation, timing);
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

    // Mobile menu toggle
    const mobileMenuButtons = document.querySelectorAll('[data-bs-toggle="offcanvas"]');
    mobileMenuButtons.forEach(button => {
      button.addEventListener('click', (e) => {
        e.preventDefault();
        const target = document.querySelector(button.getAttribute('data-bs-target'));
        if (target) {
          // Simple offcanvas implementation
          target.classList.toggle('show');
          document.body.style.overflow = target.classList.contains('show') ? 'hidden' : '';
        }
      });
    });

    // Back to top button
    const backToTopButton = document.createElement('button');
    backToTopButton.innerHTML = '<i class="bi bi-arrow-up"></i>';
    backToTopButton.className = 'btn-back-to-top btn btn-primary btn-sm rounded-circle position-fixed';
    backToTopButton.style.cssText = 'bottom: 2rem; right: 2rem; display: none; z-index: 1030;';
    backToTopButton.setAttribute('aria-label', 'Back to top');
    document.body.appendChild(backToTopButton);

    backToTopButton.addEventListener('click', () => {
      window.scrollTo({
        top: 0,
        behavior: 'smooth'
      });
    });

    const toggleBackToTopButton = () => {
      if (window.scrollY > 300) {
        backToTopButton.style.display = 'block';
      } else {
        backToTopButton.style.display = 'none';
      }
    };

    window.addEventListener('scroll', () => {
      requestAnimationFrame(() => {
        if (window.scrollY > 300) {
          backToTopButton.style.display = 'block';
        } else {
          backToTopButton.style.display = 'none';
        }
      });
    });

    // Initial check
    if (window.scrollY > 300) {
      backToTopButton.style.display = 'block';
    }

    // Smooth scroll for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
      anchor.addEventListener('click', function (e) {
        const href = this.getAttribute('href');
        if (href !== '#') {
          e.preventDefault();
          const target = document.querySelector(href);
          if (target) {
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
        }
      });
    });

    // Auto-dismiss alerts
    const alerts = document.querySelectorAll('.alert-auto-dismiss');
    alerts.forEach(alert => {
      setTimeout(() => {
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
            if (img.dataset.src) {
              img.src = img.dataset.src;
            }
            observer.unobserve(img);
          }
        });
      });

      lazyImages.forEach(img => {
        observer.observe(img);
      });
    }

    // Expose to window for global access
    window.FoodBridgeUtils = utils;
    window.FBTooltip = Tooltip;
    window.FBDropdown = Dropdown;
    window.FBModal = Modal;

    // Export functions for use in templates
    window.showToast = (message, type = 'info', delay = 5000) => {
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
      const toastInstance = new (class {
        constructor(element) {
          this.element = element;
          this.timeoutId = null;
          this.init();
        }

        init() {
          const autohide = this.element.getAttribute('data-bs-autohide') !== 'false';
          const delay = parseInt(this.element.getAttribute('data-bs-delay')) || 5000;

          if (autohide) {
            this.timeoutId = setTimeout(() => this.hide(), delay);
          }

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
      })(toastElement);

      toastInstance.show();

      // Auto remove after hidden
      toastElement.addEventListener('hidden.bs.toast', function () {
        container.remove();
      });
    };
  });
})();