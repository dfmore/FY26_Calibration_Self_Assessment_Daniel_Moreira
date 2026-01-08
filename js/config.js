/**
 * Configuration and Constants
 * Single source of truth for all magic numbers, data, and configuration
 */

// Animation timing constants
export const ANIMATION = {
    counterDuration: 2000,
    barDuration: 800,
    barDelay: 50,
    progressDelay: 200,
    revealThreshold: 0.1,
    navThreshold: 0.3
};

// Chart configuration
export const CHART_CONFIG = {
    width: 900,
    height: 280,
    margin: { top: 30, right: 50, bottom: 40, left: 50 }
};

export const CHART_FONT = "'Satoshi', sans-serif";

// Calendar data - extracted from original
export const calendarData = {
    byCategory: [
        { month: 'Jan', general: 52, customer: 14, training: 8, planning: 10, oneOnOne: 5, hours: 98.5 },
        { month: 'Feb', general: 41, customer: 10, training: 5, planning: 8, oneOnOne: 5, hours: 83.7 },
        { month: 'Mar', general: 32, customer: 8, training: 4, planning: 6, oneOnOne: 5, hours: 61.2 },
        { month: 'Apr', general: 33, customer: 7, training: 5, planning: 7, oneOnOne: 4, hours: 53.8 },
        { month: 'May', general: 36, customer: 8, training: 6, planning: 7, oneOnOne: 4, hours: 63.8 },
        { month: 'Jun', general: 25, customer: 6, training: 4, planning: 5, oneOnOne: 3, hours: 44.0 },
        { month: 'Jul', general: 40, customer: 10, training: 6, planning: 9, oneOnOne: 4, hours: 67.5 },
        { month: 'Aug', general: 22, customer: 5, training: 3, planning: 5, oneOnOne: 2, hours: 36.0 },
        { month: 'Sep', general: 34, customer: 8, training: 5, planning: 7, oneOnOne: 4, hours: 51.5 },
        { month: 'Oct', general: 46, customer: 11, training: 7, planning: 10, oneOnOne: 4, hours: 106.3 },
        { month: 'Nov', general: 31, customer: 7, training: 5, planning: 6, oneOnOne: 3, hours: 58.6 },
        { month: 'Dec', general: 23, customer: 6, training: 3, planning: 5, oneOnOne: 3, hours: 39.1 }
    ],
    byTag: [
        { month: 'Jan', informational: 12, onboarding: 8, eba: 4, ai: 2, nonEba: 3, sales: 2, support: 1, hours: 98.5 },
        { month: 'Feb', informational: 10, onboarding: 7, eba: 3, ai: 1, nonEba: 2, sales: 2, support: 1, hours: 83.7 },
        { month: 'Mar', informational: 8, onboarding: 6, eba: 3, ai: 1, nonEba: 2, sales: 1, support: 1, hours: 61.2 },
        { month: 'Apr', informational: 9, onboarding: 7, eba: 4, ai: 1, nonEba: 2, sales: 1, support: 1, hours: 53.8 },
        { month: 'May', informational: 10, onboarding: 8, eba: 4, ai: 2, nonEba: 2, sales: 2, support: 1, hours: 63.8 },
        { month: 'Jun', informational: 7, onboarding: 5, eba: 3, ai: 1, nonEba: 1, sales: 1, support: 1, hours: 44.0 },
        { month: 'Jul', informational: 11, onboarding: 7, eba: 4, ai: 2, nonEba: 2, sales: 2, support: 1, hours: 67.5 },
        { month: 'Aug', informational: 6, onboarding: 4, eba: 2, ai: 1, nonEba: 1, sales: 1, support: 1, hours: 36.0 },
        { month: 'Sep', informational: 9, onboarding: 6, eba: 3, ai: 2, nonEba: 2, sales: 1, support: 1, hours: 51.5 },
        { month: 'Oct', informational: 13, onboarding: 8, eba: 5, ai: 3, nonEba: 3, sales: 2, support: 2, hours: 106.3 },
        { month: 'Nov', informational: 10, onboarding: 6, eba: 3, ai: 2, nonEba: 2, sales: 1, support: 1, hours: 58.6 },
        { month: 'Dec', informational: 7, onboarding: 4, eba: 2, ai: 1, nonEba: 1, sales: 1, support: 1, hours: 39.1 }
    ]
};

// Chart view configurations
export const viewConfigs = {
    categories: {
        keys: ['general', 'customer', 'training', 'planning', 'oneOnOne'],
        colors: { 
            general: '#6b7280', 
            customer: '#00a693', 
            training: '#3b82f6', 
            planning: '#f59e0b', 
            oneOnOne: '#a855f7' 
        },
        labels: { 
            general: 'General', 
            customer: 'Customer', 
            training: 'Training', 
            planning: 'Planning', 
            oneOnOne: '1:1s' 
        },
        dataSource: 'byCategory',
        yMax: 100,
        stats: { 
            stat1: '305', 
            stat1Label: 'Work Meetings', 
            stat2: '303h', 
            stat2Label: 'Meeting Hours', 
            stat3: '89', 
            stat3Label: 'Peak (Jan)' 
        },
        legendTitle: 'Meeting Categories',
        insights: [
            '<span class="text-[var(--text-primary)] font-medium">General meetings dominate (59%)</span> — Core collaboration and team coordination',
            '<span class="text-[var(--text-primary)] font-medium">Customer focus (16%)</span> — Direct engagement with external stakeholders',
            '<span class="text-[var(--text-primary)] font-medium">Continuous learning (9%)</span> — Invested in AI/ML and platform capabilities'
        ]
    },
    tags: {
        keys: ['informational', 'onboarding', 'eba', 'ai', 'nonEba', 'sales', 'support'],
        colors: { 
            informational: '#6b7280', 
            onboarding: '#00a693', 
            eba: '#3b82f6', 
            ai: '#a855f7', 
            nonEba: '#f59e0b', 
            sales: '#ec4899', 
            support: '#10b981' 
        },
        labels: { 
            informational: 'Informational', 
            onboarding: 'Onboarding', 
            eba: 'EBA AS/IS', 
            ai: 'AI', 
            nonEba: 'Non-EBA IS', 
            sales: 'Sales', 
            support: 'Support' 
        },
        dataSource: 'byTag',
        yMax: 50,
        stats: { 
            stat1: '209', 
            stat1Label: 'Tagged Meetings', 
            stat2: '68%', 
            stat2Label: 'Tag Coverage', 
            stat3: '76', 
            stat3Label: 'Informational' 
        },
        legendTitle: 'Work Areas (by Tag)',
        insights: [
            '<span class="text-[var(--text-primary)] font-medium">Informational (76 meetings)</span> — Cross-team collaboration, all-hands, syncs',
            '<span class="text-[var(--text-primary)] font-medium">Onboarding (51 meetings)</span> — Customer enablement and training delivery',
            '<span class="text-[var(--text-primary)] font-medium">EBA AS/IS (27 meetings)</span> — Enterprise Business Agreement technical support'
        ]
    },
    count: {
        keys: ['total'],
        colors: { total: '#3b82f6' },
        labels: { total: 'Meetings' },
        dataSource: 'byCategory',
        yMax: 100,
        stats: { 
            stat1: '305', 
            stat1Label: 'Total Meetings', 
            stat2: '25', 
            stat2Label: 'Monthly Avg', 
            stat3: '1.0h', 
            stat3Label: 'Avg Duration' 
        },
        legendTitle: 'Meeting Count Distribution',
        insights: [
            '<span class="text-[var(--text-primary)] font-medium">January peak (89 meetings)</span> — Highest activity month with system launches',
            '<span class="text-[var(--text-primary)] font-medium">Balanced distribution</span> — Consistent 20-40 meetings per month',
            '<span class="text-[var(--text-primary)] font-medium">Efficient meetings</span> — Average 1 hour duration, focused discussions'
        ]
    }
};

// Selectors for DOM queries
export const SELECTORS = {
    scrollProgress: '#scrollProgress',
    calendarChart: '#calendarChart',
    chartTooltip: '#chartTooltip',
    navToggle: '#navToggle',
    navLinks: '#navLinks',
    dynamicStats: '#dynamicStats',
    legendTitle: '#legendTitle',
    legendContent: '#legendContent',
    insightsContent: '#insightsContent'
};

// CSS classes for JavaScript hooks
export const CLASSES = {
    reveal: 'reveal',
    visible: 'visible',
    expanded: 'expanded',
    active: 'active',
    open: 'open',
    animateIn: 'animate-in',
    timelineItem: 'timeline-item',
    initiativeCard: 'initiative-card',
    orbitCard: 'orbit-card',
    progressTrack: 'progress-track',
    scaleActivationCard: 'scale-activation-card',
    activated: 'activated'
};

