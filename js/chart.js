/**
 * Chart Module
 * D3.js calendar chart with view switching
 */

import { 
    CHART_CONFIG, 
    CHART_FONT, 
    calendarData, 
    viewConfigs, 
    SELECTORS 
} from './config.js';
import { $ } from './utils.js';

// Module state
let currentView = 'categories';
let chartSvg = null;
let chartGroup = null;
let xScale = null;
let yScale = null;
let isInitialized = false;

/**
 * Create the calendar chart SVG structure
 */
export function createCalendarChart() {
    const container = $(SELECTORS.calendarChart);
    if (!container || container.querySelector('svg') || isInitialized) return;
    
    // Check if D3 is available
    if (typeof d3 === 'undefined') {
        console.error('D3.js is not loaded');
        return;
    }
    
    isInitialized = true;
    
    const { width, height, margin } = CHART_CONFIG;
    const chartWidth = width - margin.left - margin.right;
    const chartHeight = height - margin.top - margin.bottom;
    
    chartSvg = d3.select(SELECTORS.calendarChart)
        .append('svg')
        .attr('viewBox', `0 0 ${width} ${height}`)
        .attr('preserveAspectRatio', 'xMidYMid meet')
        .style('width', '100%')
        .style('height', 'auto');
    
    chartGroup = chartSvg.append('g')
        .attr('transform', `translate(${margin.left},${margin.top})`);
    
    // Create scales
    xScale = d3.scaleBand()
        .domain(calendarData.byCategory.map(d => d.month))
        .range([0, chartWidth])
        .padding(0.3);
    
    yScale = d3.scaleLinear()
        .range([chartHeight, 0]);
    
    // Create axes groups
    chartGroup.append('g')
        .attr('class', 'x-axis')
        .attr('transform', `translate(0,${chartHeight})`);
    
    chartGroup.append('g')
        .attr('class', 'y-axis');
    
    // Initial render
    updateChart('categories', true);
    
    // Set up view toggle buttons
    initViewToggle();
}

/**
 * Initialize view toggle button listeners
 */
function initViewToggle() {
    const buttons = document.querySelectorAll('[data-view]');
    buttons.forEach(btn => {
        btn.addEventListener('click', () => {
            const view = btn.dataset.view;
            if (view && view !== currentView) {
                switchCalendarView(view);
            }
        });
    });
}

/**
 * Switch to a different chart view
 * @param {string} view - The view to switch to (categories, tags, count)
 */
export function switchCalendarView(view) {
    if (view === currentView) return;
    currentView = view;
    
    // Update button states
    document.querySelectorAll('[data-view]').forEach(btn => {
        btn.classList.remove('active');
        btn.setAttribute('aria-selected', 'false');
    });
    
    const activeBtn = document.querySelector(`[data-view="${view}"]`);
    if (activeBtn) {
        activeBtn.classList.add('active');
        activeBtn.setAttribute('aria-selected', 'true');
    }
    
    // Update chart
    updateChart(view, false);
}

/**
 * Update the chart with new data/view
 * @param {string} view - The view to render
 * @param {boolean} isInitial - Whether this is the initial render
 */
function updateChart(view, isInitial) {
    if (!chartGroup || !xScale || !yScale) return;
    
    const config = viewConfigs[view];
    const data = calendarData[config.dataSource];
    const duration = isInitial ? 800 : 600;
    
    // Update Y scale domain
    yScale.domain([0, config.yMax]);
    
    // Update axes
    const xAxis = d3.axisBottom(xScale).tickSize(0);
    const yAxis = d3.axisLeft(yScale).ticks(5).tickSize(0);
    
    chartGroup.select('.x-axis')
        .transition().duration(duration)
        .call(xAxis);
    
    chartGroup.select('.y-axis')
        .transition().duration(duration)
        .call(yAxis);
    
    // Style axes
    chartGroup.selectAll('.x-axis .domain, .y-axis .domain').remove();
    chartGroup.selectAll('.x-axis text')
        .attr('fill', '#a1a1a6')
        .attr('font-size', '11px')
        .attr('font-weight', '500')
        .attr('font-family', CHART_FONT);
    chartGroup.selectAll('.y-axis text')
        .attr('fill', '#8e8e93')
        .attr('font-size', '10px')
        .attr('font-weight', '500')
        .attr('font-family', CHART_FONT);
    
    // Prepare and render data based on view
    if (view === 'hours') {
        // Hours view - simple bars showing hours per month
        renderSimpleBars(data, config, duration, isInitial);
    } else {
        // Categories and tags views - stacked bars
        const stack = d3.stack()
            .keys(config.keys)
            .order(d3.stackOrderNone)
            .offset(d3.stackOffsetNone);
        const chartData = stack(data);
        renderStackedBars(chartData, config, duration, isInitial);
    }
    
    // Update stats, legend, and insights
    updateDynamicContent(config);
}

/**
 * Render stacked bar chart
 */
function renderStackedBars(series, config, duration, isInitial) {
    const chartHeight = yScale.range()[0];
    const tooltip = d3.select(SELECTORS.chartTooltip);
    
    // Bind series data
    const groups = chartGroup.selectAll('.series')
        .data(series, d => d.key);
    
    // Exit
    groups.exit()
        .transition().duration(duration)
        .style('opacity', 0)
        .remove();
    
    // Enter + Update
    const groupsEnter = groups.enter()
        .append('g')
        .attr('class', 'series');
    
    const groupsMerge = groupsEnter.merge(groups)
        .attr('fill', d => config.colors[d.key]);
    
    // Bind rect data
    const rects = groupsMerge.selectAll('rect')
        .data(d => d, d => d.data.month);
    
    // Exit
    rects.exit()
        .transition().duration(duration)
        .attr('y', chartHeight)
        .attr('height', 0)
        .remove();
    
    // Enter
    const rectsEnter = rects.enter()
        .append('rect')
        .attr('x', d => xScale(d.data.month))
        .attr('y', chartHeight)
        .attr('width', xScale.bandwidth())
        .attr('height', 0)
        .attr('rx', 2);
    
    // Update
    rectsEnter.merge(rects)
        .on('mouseover', function(event, d) {
            const key = d3.select(this.parentNode).datum().key;
            const value = d.data[key];
            const month = d.data.month;
            tooltip.html(`
                <strong>${month}</strong><br/>
                ${config.labels[key]}: <strong>${value}</strong> meetings<br/>
                <span style="opacity: 0.7;">Total: ${Object.keys(config.colors).reduce((sum, k) => sum + (d.data[k] || 0), 0)} meetings</span>
            `)
            .style('opacity', 1)
            .style('left', (event.pageX + 15) + 'px')
            .style('top', (event.pageY - 15) + 'px');
        })
        .on('mouseout', function() {
            tooltip.style('opacity', 0);
        })
        .transition().duration(duration)
        .delay((d, i) => isInitial ? i * 30 : 0)
        .attr('x', d => xScale(d.data.month))
        .attr('y', d => yScale(d[1]))
        .attr('width', xScale.bandwidth())
        .attr('height', d => yScale(d[0]) - yScale(d[1]));
}

/**
 * Render simple bar chart
 */
function renderSimpleBars(data, config, duration, isInitial) {
    const chartHeight = yScale.range()[0];
    const tooltip = d3.select(SELECTORS.chartTooltip);
    const key = config.keys[0];
    
    // Bind data
    const bars = chartGroup.selectAll('.simple-bar')
        .data(data, d => d.month);
    
    // Exit
    bars.exit()
        .transition().duration(duration)
        .attr('y', chartHeight)
        .attr('height', 0)
        .remove();
    
    // Enter
    const barsEnter = bars.enter()
        .append('rect')
        .attr('class', 'simple-bar')
        .attr('x', d => xScale(d.month))
        .attr('y', chartHeight)
        .attr('width', xScale.bandwidth())
        .attr('height', 0)
        .attr('rx', 4)
        .attr('fill', config.colors[key]);
    
    // Update
    barsEnter.merge(bars)
        .on('mouseover', function(event, d) {
            const value = d[key];
            tooltip.html(`
                <strong>${d.month}</strong><br/>
                ${config.labels[key]}: <strong>${value}${key === 'hours' ? 'h' : ''}</strong>
            `)
            .style('opacity', 1)
            .style('left', (event.pageX + 15) + 'px')
            .style('top', (event.pageY - 15) + 'px');
            
            d3.select(this)
                .attr('fill', '#00d4ff')
                .attr('filter', 'drop-shadow(0 0 10px rgba(0, 212, 255, 0.6))');
        })
        .on('mouseout', function() {
            tooltip.style('opacity', 0);
            d3.select(this)
                .attr('fill', config.colors[key])
                .attr('filter', 'none');
        })
        .transition().duration(duration)
        .delay((d, i) => isInitial ? i * 40 : 0)
        .attr('x', d => xScale(d.month))
        .attr('y', d => yScale(d[key]))
        .attr('width', xScale.bandwidth())
        .attr('height', d => chartHeight - yScale(d[key]));
    
    // Remove any stacked series
    chartGroup.selectAll('.series').remove();
}

/**
 * Update dynamic content (stats, legend, insights)
 */
function updateDynamicContent(config) {
    // Update stats
    const stat1 = $('#stat1');
    const stat1Label = $('#stat1-label');
    const stat2 = $('#stat2');
    const stat2Label = $('#stat2-label');
    const stat3 = $('#stat3');
    const stat3Label = $('#stat3-label');
    
    if (stat1) stat1.textContent = config.stats.stat1;
    if (stat1Label) stat1Label.textContent = config.stats.stat1Label;
    if (stat2) stat2.textContent = config.stats.stat2;
    if (stat2Label) stat2Label.textContent = config.stats.stat2Label;
    if (stat3) stat3.textContent = config.stats.stat3;
    if (stat3Label) stat3Label.textContent = config.stats.stat3Label;
    
    // Update legend
    const legendTitle = $(SELECTORS.legendTitle);
    const legendContent = $(SELECTORS.legendContent);
    
    if (legendTitle) legendTitle.textContent = config.legendTitle;
    if (legendContent) {
        legendContent.innerHTML = Object.keys(config.colors).map(key => `
            <div class="flex items-center gap-2">
                <div class="w-3 h-3 rounded-full" style="background: ${config.colors[key]};"></div>
                <span class="text-[var(--text-secondary)]">${config.labels[key]}</span>
            </div>
        `).join('');
    }
    
    // Update insights
    const insightsContent = $(SELECTORS.insightsContent);
    if (insightsContent) {
        insightsContent.innerHTML = config.insights.map(insight => 
            `<p>${insight}</p>`
        ).join('');
    }
}

/**
 * Get current view
 * @returns {string}
 */
export function getCurrentView() {
    return currentView;
}

