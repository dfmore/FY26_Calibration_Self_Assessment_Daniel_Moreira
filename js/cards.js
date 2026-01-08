/**
 * Cards Module
 * Handles expandable card behavior with event delegation
 */

import { CLASSES } from './config.js';
import { $, $$, on, hasClass, toggleClass } from './utils.js';

/**
 * Toggle card expansion state
 * @param {HTMLElement} card - The card element to toggle
 */
function toggleCard(card) {
    const isExpanded = toggleClass(card, CLASSES.expanded);
    
    // Update expand icon
    const icon = card.querySelector('.expand-icon');
    if (icon) {
        icon.textContent = isExpanded ? '−' : '+';
    }
    
    // Update ARIA state
    card.setAttribute('aria-expanded', String(isExpanded));
}

/**
 * Handle click on expandable cards
 * @param {Event} event - Click event
 */
function handleCardClick(event) {
    const card = event.target.closest('[data-expandable="true"]');
    if (!card) return;
    
    toggleCard(card);
}

/**
 * Handle keyboard navigation on expandable cards
 * @param {KeyboardEvent} event - Keyboard event
 */
function handleCardKeyboard(event) {
    if (event.key !== 'Enter' && event.key !== ' ') return;
    
    const card = event.target.closest('[data-expandable="true"]');
    if (!card) return;
    
    event.preventDefault();
    toggleCard(card);
}

// Cache for performance to avoid layout thrashing
const cardRects = new Map();

/**
 * Handle scale activation card hover
 * @param {MouseEvent} event - Mouse event
 */
function handleScaleCardHover(event) {
    // Guard against events that don't have target.closest
    if (!event.target || typeof event.target.closest !== 'function') return;
    
    const card = event.target.closest('[data-scale-card="true"]');
    if (!card) return;
    
    // Cache the rect once on entry
    cardRects.set(card, card.getBoundingClientRect());
    
    // Activate the card
    if (!hasClass(card, CLASSES.activated)) {
        card.classList.add(CLASSES.activated);
    }
}

/**
 * Handle mouse move on scale card for glow effect
 * @param {MouseEvent} event - Mouse event
 */
function handleScaleCardMouseMove(event) {
    // Guard against events that don't have target.closest
    if (!event.target || typeof event.target.closest !== 'function') return;
    
    const card = event.target.closest('[data-scale-card="true"]');
    if (!card) return;
    
    // Use cached rect or fallback
    const rect = cardRects.get(card) || card.getBoundingClientRect();
    const x = ((event.clientX - rect.left) / rect.width) * 100;
    const y = ((event.clientY - rect.top) / rect.height) * 100;
    
    card.style.setProperty('--mouse-x', `${x}%`);
    card.style.setProperty('--mouse-y', `${y}%`);
}

/**
 * Handle mouse leave on scale card to clear cache
 * @param {MouseEvent} event - Mouse event
 */
function handleScaleCardLeave(event) {
    if (!event.target || typeof event.target.closest !== 'function') return;
    const card = event.target.closest('[data-scale-card="true"]');
    if (card) {
        cardRects.delete(card);
    }
}

/**
 * Initialize card behaviors with event delegation
 */
export function initCards() {
    // Use event delegation on document for expandable cards
    on(document, 'click', handleCardClick);
    on(document, 'keydown', handleCardKeyboard);
    
    // Scale activation cards
    on(document, 'mouseenter', handleScaleCardHover, true);
    on(document, 'mouseleave', handleScaleCardLeave, true);
    on(document, 'mousemove', handleScaleCardMouseMove);
}

/**
 * Collapse all expanded cards
 */
export function collapseAllCards() {
    $$('[data-expandable="true"].expanded').forEach(card => {
        card.classList.remove(CLASSES.expanded);
        card.setAttribute('aria-expanded', 'false');
        
        const icon = card.querySelector('.expand-icon');
        if (icon) {
            icon.textContent = '+';
        }
    });
}

