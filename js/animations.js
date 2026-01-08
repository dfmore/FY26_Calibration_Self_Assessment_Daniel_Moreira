/**
 * Animations Module
 * Handles IntersectionObserver, counter animations, and progress bars
 */

import { ANIMATION, CLASSES } from './config.js';
import { $$, createObserver, animateValue, easeOutQuart } from './utils.js';

let mainObserver = null;

/**
 * Animate a counter element from 0 to its target value
 * @param {HTMLElement} element - Element with data-target attribute
 */
export function animateCounter(element) {
    const target = parseInt(element.dataset.target, 10);
    if (isNaN(target)) return;
    
    animateValue({
        from: 0,
        to: target,
        duration: ANIMATION.counterDuration,
        easing: easeOutQuart,
        onUpdate: (value) => {
            element.textContent = Math.floor(value);
        }
    });
}

/**
 * Animate a progress bar fill
 * @param {HTMLElement} track - Progress track element
 */
export function animateProgressBar(track) {
    const fill = track.querySelector('.progress-fill');
    if (!fill || !fill.dataset.width) return;
    
    setTimeout(() => {
        fill.style.width = `${fill.dataset.width}%`;
    }, ANIMATION.progressDelay);
}

/**
 * Handle intersection observer callback
 * @param {IntersectionObserverEntry[]} entries - Observer entries
 */
function handleIntersection(entries) {
    entries.forEach(entry => {
        if (!entry.isIntersecting) return;
        
        const el = entry.target;
        
        // Reveal animations
        if (el.classList.contains(CLASSES.reveal) || 
            el.classList.contains(CLASSES.timelineItem) || 
            el.classList.contains(CLASSES.animateIn)) {
            el.classList.add(CLASSES.visible);
        }
        
        // Counter animations (only if not already animated)
        if (el.dataset.target && el.textContent.trim() === '0') {
            animateCounter(el);
        }
        
        // Progress bar animations
        if (el.classList.contains(CLASSES.progressTrack)) {
            animateProgressBar(el);
        }
    });
}

/**
 * Initialize the main intersection observer for scroll-triggered effects
 */
export function initAnimations() {
    // Create main observer
    mainObserver = createObserver(handleIntersection, { 
        threshold: ANIMATION.revealThreshold 
    });
    
    if (!mainObserver) {
        console.warn('IntersectionObserver not supported');
        // Fallback: show all elements immediately
        $$('.reveal, .timeline-item, .animate-in').forEach(el => {
            el.classList.add(CLASSES.visible);
        });
        return;
    }
    
    // Observe all relevant elements
    const elementsToObserve = $$(
        '.reveal, .timeline-item, .animate-in, [data-target], .progress-track'
    );
    
    elementsToObserve.forEach(el => mainObserver.observe(el));
}

/**
 * Re-register elements with observer (call after dynamic content loads)
 */
export function registerElements() {
    if (!mainObserver) return;
    
    const elementsToObserve = $$(
        '.reveal, .timeline-item, .animate-in, [data-target], .progress-track'
    );
    
    elementsToObserve.forEach(el => mainObserver.observe(el));
}

/**
 * Cleanup observer
 */
export function destroyAnimations() {
    if (mainObserver) {
        mainObserver.disconnect();
        mainObserver = null;
    }
}

