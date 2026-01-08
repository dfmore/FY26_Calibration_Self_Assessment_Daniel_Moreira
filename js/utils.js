/**
 * Utility Functions
 * Shared helper functions used across modules
 */

/**
 * Safely query a DOM element
 * @param {string} selector - CSS selector
 * @param {Element} [context=document] - Context element to search within
 * @returns {Element|null}
 */
export function $(selector, context = document) {
    return context.querySelector(selector);
}

/**
 * Safely query all matching DOM elements
 * @param {string} selector - CSS selector
 * @param {Element} [context=document] - Context element to search within
 * @returns {NodeListOf<Element>}
 */
export function $$(selector, context = document) {
    return context.querySelectorAll(selector);
}

/**
 * Add event listener with optional delegation
 * @param {Element|string} target - Element or selector
 * @param {string} event - Event type
 * @param {Function} handler - Event handler
 * @param {Object} [options] - Event listener options
 */
export function on(target, event, handler, options = {}) {
    const element = typeof target === 'string' ? $(target) : target;
    if (element) {
        element.addEventListener(event, handler, options);
    }
}

/**
 * Debounce function execution
 * @param {Function} func - Function to debounce
 * @param {number} wait - Delay in milliseconds
 * @returns {Function}
 */
export function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

/**
 * Throttle function execution
 * @param {Function} func - Function to throttle
 * @param {number} limit - Minimum time between calls in milliseconds
 * @returns {Function}
 */
export function throttle(func, limit) {
    let inThrottle;
    return function(...args) {
        if (!inThrottle) {
            func.apply(this, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}

/**
 * Easing function for animations (ease-out quart)
 * @param {number} t - Progress (0-1)
 * @returns {number}
 */
export function easeOutQuart(t) {
    return 1 - Math.pow(1 - t, 4);
}

/**
 * Animate a numeric value
 * @param {Object} options - Animation options
 * @param {number} options.from - Start value
 * @param {number} options.to - End value
 * @param {number} options.duration - Duration in milliseconds
 * @param {Function} options.onUpdate - Callback with current value
 * @param {Function} [options.onComplete] - Callback when complete
 * @param {Function} [options.easing] - Easing function
 */
export function animateValue({ from, to, duration, onUpdate, onComplete, easing = easeOutQuart }) {
    const start = performance.now();
    
    function update(now) {
        const elapsed = now - start;
        const progress = Math.min(elapsed / duration, 1);
        const easedProgress = easing(progress);
        const currentValue = from + (to - from) * easedProgress;
        
        onUpdate(currentValue);
        
        if (progress < 1) {
            requestAnimationFrame(update);
        } else if (onComplete) {
            onComplete();
        }
    }
    
    requestAnimationFrame(update);
}

/**
 * Create an IntersectionObserver with error handling
 * @param {Function} callback - Observer callback
 * @param {Object} [options] - Observer options
 * @returns {IntersectionObserver|null}
 */
export function createObserver(callback, options = {}) {
    try {
        return new IntersectionObserver(callback, options);
    } catch (error) {
        console.error('Failed to create IntersectionObserver:', error);
        return null;
    }
}

/**
 * Toggle a class on an element
 * @param {Element} element - Target element
 * @param {string} className - Class to toggle
 * @param {boolean} [force] - Force add/remove
 * @returns {boolean} - Whether class is now present
 */
export function toggleClass(element, className, force) {
    if (!element) return false;
    return element.classList.toggle(className, force);
}

/**
 * Check if element has a class
 * @param {Element} element - Target element
 * @param {string} className - Class to check
 * @returns {boolean}
 */
export function hasClass(element, className) {
    return element ? element.classList.contains(className) : false;
}

/**
 * Get scroll percentage of page
 * @returns {number} - Percentage (0-100)
 */
export function getScrollPercentage() {
    const scrollTop = window.scrollY;
    const docHeight = document.documentElement.scrollHeight - window.innerHeight;
    return docHeight > 0 ? (scrollTop / docHeight) * 100 : 0;
}

/**
 * Smooth scroll to an element
 * @param {Element|string} target - Target element or selector
 * @param {Object} [options] - Scroll options
 */
export function scrollToElement(target, options = { behavior: 'smooth', block: 'start' }) {
    const element = typeof target === 'string' ? $(target) : target;
    if (element) {
        element.scrollIntoView(options);
    }
}

