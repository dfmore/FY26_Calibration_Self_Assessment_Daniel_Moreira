/**
 * Navigation Module
 * Handles scroll progress, mobile toggle, smooth scroll, and active states
 */

import { ANIMATION, CLASSES, SELECTORS } from './config.js';
import { $, $$, on, createObserver, getScrollPercentage, scrollToElement, throttle } from './utils.js';

let navObserver = null;

/**
 * Update scroll progress indicator
 */
function updateScrollProgress() {
    const progressBar = $(SELECTORS.scrollProgress);
    if (progressBar) {
        progressBar.style.width = `${getScrollPercentage()}%`;
    }
}

/**
 * Initialize scroll progress tracking
 */
function initScrollProgress() {
    const throttledUpdate = throttle(updateScrollProgress, 16); // ~60fps
    on(window, 'scroll', throttledUpdate, { passive: true });
}

/**
 * Initialize smooth scrolling for anchor links
 */
function initSmoothScroll() {
    on(document, 'click', (e) => {
        const anchor = e.target.closest('a[href^="#"]');
        if (!anchor) return;
        
        e.preventDefault();
        const targetSelector = anchor.getAttribute('href');
        const target = $(targetSelector);
        
        if (target) {
            scrollToElement(target);
            
            // Close mobile menu if open
            const navLinks = $(SELECTORS.navLinks);
            const navToggle = $(SELECTORS.navToggle);
            if (navLinks && navToggle) {
                navLinks.classList.remove(CLASSES.open);
                navToggle.classList.remove(CLASSES.active);
                navToggle.setAttribute('aria-expanded', 'false');
            }
        }
    });
}

/**
 * Initialize mobile navigation toggle
 */
function initMobileNav() {
    const navToggle = $(SELECTORS.navToggle);
    const navLinks = $(SELECTORS.navLinks);
    
    if (!navToggle || !navLinks) return;
    
    on(navToggle, 'click', () => {
        const isOpen = navLinks.classList.toggle(CLASSES.open);
        navToggle.classList.toggle(CLASSES.active);
        navToggle.setAttribute('aria-expanded', String(isOpen));
    });
}

/**
 * Handle navigation section observer
 * @param {IntersectionObserverEntry[]} entries - Observer entries
 */
function handleNavIntersection(entries) {
    entries.forEach(entry => {
        if (!entry.isIntersecting) return;
        
        const sectionId = entry.target.id;
        if (!sectionId) return;
        
        // Update active nav link
        $$('.nav-link').forEach(link => {
            link.classList.remove(CLASSES.active);
            if (link.getAttribute('href') === `#${sectionId}`) {
                link.classList.add(CLASSES.active);
            }
        });
    });
}

/**
 * Initialize navigation active state tracking
 */
function initActiveStateTracking() {
    navObserver = createObserver(handleNavIntersection, {
        threshold: ANIMATION.navThreshold,
        rootMargin: '-80px 0px -50% 0px'
    });
    
    if (!navObserver) return;
    
    // Observe all sections with IDs
    $$('section[id]').forEach(section => {
        navObserver.observe(section);
    });
}

/**
 * Initialize all navigation functionality
 */
export function initNavigation() {
    initScrollProgress();
    initSmoothScroll();
    initMobileNav();
    initActiveStateTracking();
}

/**
 * Re-register sections with observer (call after dynamic content loads)
 */
export function registerSections() {
    if (!navObserver) return;
    
    $$('section[id]').forEach(section => {
        navObserver.observe(section);
    });
}

/**
 * Cleanup navigation observers
 */
export function destroyNavigation() {
    if (navObserver) {
        navObserver.disconnect();
        navObserver = null;
    }
}

