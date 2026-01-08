/**
 * Main Entry Point
 * Orchestrates loading and initialization of all modules
 */

import { initSections } from './section-loader.js';
import { initAnimations, registerElements } from './animations.js';
import { initNavigation, registerSections } from './navigation.js';
import { initCards } from './cards.js';
import { createCalendarChart } from './chart.js';
import { SELECTORS } from './config.js';
import { $, createObserver } from './utils.js';

/**
 * Initialize all application functionality
 */
function initApp() {
    // Initialize card behaviors (event delegation, works before sections load)
    initCards();
    
    // Initialize navigation (scroll, mobile toggle)
    initNavigation();
    
    // Initialize scroll-triggered animations
    initAnimations();
    
    // Re-register elements after sections are loaded
    registerElements();
    registerSections();
    
    // Set up chart observer (create chart when scrolled into view)
    initChartObserver();
}

/**
 * Create observer for chart initialization on scroll
 */
function initChartObserver() {
    const chartContainer = $(SELECTORS.calendarChart);
    if (!chartContainer) return;
    
    const observer = createObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                createCalendarChart();
                observer.disconnect();
            }
        });
    }, { threshold: 0.1 });
    
    if (observer) {
        observer.observe(chartContainer);
    }
}

/**
 * Bootstrap the application
 */
async function bootstrap() {
    try {
        // Load all HTML sections
        await initSections();
        
        // Initialize app after sections are loaded
        initApp();
        
        console.log('Application initialized successfully');
    } catch (error) {
        console.error('Failed to initialize application:', error);
    }
}

// Start the application when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', bootstrap);
} else {
    bootstrap();
}

