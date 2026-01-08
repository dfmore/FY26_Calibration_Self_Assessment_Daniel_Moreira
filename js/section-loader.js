/**
 * Section Loader Module
 * Dynamically loads HTML section fragments into the page
 */

/**
 * Load an HTML section from a file
 * @param {string} sectionName - Name of the section file (without .html)
 * @returns {Promise<string>} - The HTML content
 */
async function loadSection(sectionName) {
    try {
        const response = await fetch(`sections/${sectionName}.html`);
        if (!response.ok) {
            throw new Error(`Failed to load section: ${sectionName} (${response.status})`);
        }
        return await response.text();
    } catch (error) {
        console.error(`Error loading section ${sectionName}:`, error);
        return `<!-- Failed to load ${sectionName} -->`;
    }
}

/**
 * Load multiple sections in parallel
 * @param {string[]} sectionNames - Array of section file names
 * @returns {Promise<Map<string, string>>} - Map of section name to HTML content
 */
async function loadSections(sectionNames) {
    const results = new Map();
    const promises = sectionNames.map(async (name) => {
        const html = await loadSection(name);
        results.set(name, html);
    });
    
    await Promise.all(promises);
    return results;
}

/**
 * Inject loaded sections into the page
 * @param {HTMLElement} container - Container element to inject sections into
 * @param {string[]} sectionOrder - Ordered list of section names
 * @param {Map<string, string>} sections - Map of section name to HTML content
 */
function injectSections(container, sectionOrder, sections) {
    const fragment = document.createDocumentFragment();
    const tempDiv = document.createElement('div');
    
    for (const sectionName of sectionOrder) {
        const html = sections.get(sectionName);
        if (html) {
            tempDiv.innerHTML = html;
            while (tempDiv.firstChild) {
                fragment.appendChild(tempDiv.firstChild);
            }
        }
    }
    
    container.appendChild(fragment);
}

/**
 * Initialize and load all sections
 * @returns {Promise<void>}
 */
export async function initSections() {
    const sectionOrder = [
        'nav',
        'hero',
        'timeline',
        'calendar',
        'initiatives',
        'skills',
        'kpi',
        'kcs',
        'plaudits',
        'orbit',
        'closing',
        'footer'
    ];
    
    const container = document.getElementById('app');
    if (!container) {
        console.error('App container not found');
        return;
    }
    
    try {
        const sections = await loadSections(sectionOrder);
        injectSections(container, sectionOrder, sections);
        
        // Dispatch custom event when all sections are loaded
        document.dispatchEvent(new CustomEvent('sectionsLoaded'));
    } catch (error) {
        console.error('Failed to initialize sections:', error);
    }
}

