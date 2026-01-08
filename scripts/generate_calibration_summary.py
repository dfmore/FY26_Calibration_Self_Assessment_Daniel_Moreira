#!/usr/bin/env python3
"""
Generate Calibration Summary Document
Creates a markdown summary of calendar analysis for calibration purposes.
"""

import json
from datetime import datetime


def load_analysis_data():
    """Load both analysis JSON files."""
    with open('FY26/analysis_outputs/calendar_analysis.json', 'r', encoding='utf-8') as f:
        calendar_data = json.load(f)
    
    with open('FY26/analysis_outputs/stakeholder_analysis.json', 'r', encoding='utf-8') as f:
        stakeholder_data = json.load(f)
    
    return calendar_data, stakeholder_data


def generate_markdown_summary(calendar_data, stakeholder_data):
    """Generate a comprehensive markdown summary."""
    
    md = []
    md.append("# FY26 Calendar Analysis - Work Activity Summary")
    md.append(f"\n*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}*")
    md.append("\n---\n")
    
    # Executive Summary
    md.append("## Executive Summary\n")
    
    total_events = calendar_data['stats']['total_events']
    work_relevant_events = sum(
        cat['count'] for cat_name, cat in calendar_data['stats']['by_category'].items()
        if cat_name not in [
            'declined_tentative_declined', 'declined_tentative_tentative',
            'out_of_office', 'personal_time_off', 'breaks_personal_care',
            'free_time_transparent'
        ]
    )
    
    work_relevant_hours = sum(
        cat['total_hours'] for cat_name, cat in calendar_data['stats']['by_category'].items()
        if cat_name not in [
            'declined_tentative_declined', 'declined_tentative_tentative',
            'out_of_office', 'personal_time_off', 'breaks_personal_care',
            'free_time_transparent'
        ]
    )
    
    md.append(f"- **Total Calendar Events**: {total_events}")
    md.append(f"- **Work-Relevant Events**: {work_relevant_events} ({work_relevant_events/total_events*100:.1f}%)")
    md.append(f"- **Work Hours Tracked**: {work_relevant_hours:.1f} hours")
    md.append(f"- **Unique Stakeholders Engaged**: {len(stakeholder_data['stakeholders'])}")
    md.append(f"- **Internal Stakeholders**: {sum(1 for s in stakeholder_data['stakeholders'].values() if 'Autodesk (Internal)' in s.get('companies', []))}")
    md.append(f"- **External Stakeholders**: {sum(1 for s in stakeholder_data['stakeholders'].values() if 'Autodesk (Internal)' not in s.get('companies', []))}")
    
    # Key Metrics
    md.append("\n---\n")
    md.append("## Key Engagement Metrics\n")
    
    # Top stakeholders
    md.append("### Top 15 Stakeholders by Engagement Time\n")
    md.append("| Rank | Name | Hours | Meetings | Months Active | Primary Company |")
    md.append("|------|------|-------|----------|---------------|-----------------|")
    
    sorted_stakeholders = sorted(
        stakeholder_data['stakeholders'].items(),
        key=lambda x: x[1]['hours'],
        reverse=True
    )[:15]
    
    for i, (name, data) in enumerate(sorted_stakeholders, 1):
        companies = data.get('companies', ['Unknown'])
        primary_company = companies[0] if companies else 'Unknown'
        months = len(data.get('months_active', []))
        md.append(f"| {i} | {name} | {data['hours']:.1f} | {data['count']} | {months} | {primary_company} |")
    
    # Meeting type breakdown
    md.append("\n### Time Distribution by Activity Type\n")
    md.append("| Activity Type | Meetings | Hours | % of Total |")
    md.append("|---------------|----------|-------|------------|")
    
    time_stats = stakeholder_data['time_stats']
    total_hours = sum(d['hours'] for d in time_stats['by_meeting_type'].values())
    
    sorted_types = sorted(
        time_stats['by_meeting_type'].items(),
        key=lambda x: x[1]['hours'],
        reverse=True
    )
    
    for meeting_type, data in sorted_types:
        pct = (data['hours'] / total_hours * 100) if total_hours > 0 else 0
        md.append(f"| {meeting_type} | {data['count']} | {data['hours']:.1f} | {pct:.1f}% |")
    
    # Monthly trend
    md.append("\n### Monthly Activity Trend\n")
    md.append("| Month | Meetings | Hours | Avg Duration |")
    md.append("|-------|----------|-------|--------------|")
    
    for month in sorted(time_stats['by_month'].keys()):
        data = time_stats['by_month'][month]
        avg = data['hours'] / data['count'] if data['count'] > 0 else 0
        md.append(f"| {month} | {data['count']} | {data['hours']:.1f} | {avg:.2f}h |")
    
    # External organizations
    md.append("\n### Top External Organizations Engaged\n")
    
    org_stats = {}
    for name, data in stakeholder_data['stakeholders'].items():
        for company in data.get('companies', []):
            if company != 'Autodesk (Internal)' and company not in ['Unknown', '', 'Personal Email']:
                if company not in org_stats:
                    org_stats[company] = {'hours': 0, 'meetings': 0, 'people': set()}
                org_stats[company]['hours'] += data['hours']
                org_stats[company]['meetings'] += data['count']
                org_stats[company]['people'].add(name)
    
    sorted_orgs = sorted(org_stats.items(), key=lambda x: x[1]['hours'], reverse=True)[:10]
    
    if sorted_orgs:
        md.append("| Rank | Organization | Hours | Meetings | People |")
        md.append("|------|--------------|-------|----------|--------|")
        
        for i, (org, data) in enumerate(sorted_orgs, 1):
            md.append(f"| {i} | {org} | {data['hours']:.1f} | {data['meetings']} | {len(data['people'])} |")
    else:
        md.append("\n*No clear external organizations identified (may need email domain cleanup)*\n")
    
    # Work patterns
    md.append("\n---\n")
    md.append("## Work Patterns & Insights\n")
    
    # Day of week
    md.append("### Meeting Load by Day of Week\n")
    md.append("| Day | Meetings | Hours | Avg per Meeting |")
    md.append("|-----|----------|-------|-----------------|")
    
    day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    for day in day_order:
        if day in time_stats['by_day_of_week']:
            data = time_stats['by_day_of_week'][day]
            avg = data['hours'] / data['count'] if data['count'] > 0 else 0
            md.append(f"| {day} | {data['count']} | {data['hours']:.1f} | {avg:.2f}h |")
    
    # Time of day
    md.append("\n### Meeting Distribution by Time of Day\n")
    md.append("| Time Slot | Meetings | Hours | % of Total |")
    md.append("|-----------|----------|-------|------------|")
    
    total_hours_time = sum(d['hours'] for d in time_stats['by_time_of_day'].values())
    for time_slot in sorted(time_stats['by_time_of_day'].keys()):
        data = time_stats['by_time_of_day'][time_slot]
        pct = (data['hours'] / total_hours_time * 100) if total_hours_time > 0 else 0
        md.append(f"| {time_slot} | {data['count']} | {data['hours']:.1f} | {pct:.1f}% |")
    
    # Meeting size
    md.append("\n### Meeting Size Distribution\n")
    
    size_dist = time_stats['meeting_size_distribution']
    total_meetings = sum(size_dist.values())
    
    md.append("| Size Category | Count | % of Total |")
    md.append("|---------------|-------|------------|")
    
    size_order = [
        "1:1 (2 people)",
        "Small (3-5 people)",
        "Medium (6-10 people)",
        "Large (11-20 people)",
        "Very Large (20+ people)"
    ]
    
    for size in size_order:
        if size in size_dist:
            count = size_dist[size]
            pct = (count / total_meetings * 100) if total_meetings > 0 else 0
            md.append(f"| {size} | {count} | {pct:.1f}% |")
    
    # Key insights
    md.append("\n---\n")
    md.append("## Key Insights for Calibration\n")
    
    md.append("\n### Collaboration Breadth")
    total_stakeholders = len(stakeholder_data['stakeholders'])
    internal_count = sum(1 for s in stakeholder_data['stakeholders'].values() 
                        if 'Autodesk (Internal)' in s.get('companies', []))
    external_count = total_stakeholders - internal_count
    
    md.append(f"- Engaged with **{total_stakeholders} unique stakeholders** across the year")
    md.append(f"- **{internal_count} internal** and **{external_count} external** contacts")
    md.append(f"- Majority of time spent in **1:1 meetings** ({size_dist.get('1:1 (2 people)', 0)} meetings)")
    
    md.append("\n### Time Investment")
    general_meetings_hours = time_stats['by_meeting_type'].get('General Meetings', {}).get('hours', 0)
    customer_hours = time_stats['by_meeting_type'].get('Customer/External', {}).get('hours', 0)
    training_hours = time_stats['by_meeting_type'].get('Training/Learning', {}).get('hours', 0)
    
    md.append(f"- **{general_meetings_hours:.1f} hours** in general work meetings")
    md.append(f"- **{customer_hours:.1f} hours** in customer/external engagements")
    md.append(f"- **{training_hours:.1f} hours** invested in training and learning")
    
    md.append("\n### Work Patterns")
    busiest_day = max(time_stats['by_day_of_week'].items(), key=lambda x: x[1]['hours'])
    busiest_time = max(time_stats['by_time_of_day'].items(), key=lambda x: x[1]['hours'])
    
    md.append(f"- Busiest day: **{busiest_day[0]}** ({busiest_day[1]['hours']:.1f} hours)")
    md.append(f"- Most active time: **{busiest_time[0]}** ({busiest_time[1]['hours']:.1f} hours)")
    md.append(f"- **{time_stats['recurring_vs_adhoc']['adhoc']}** ad-hoc meetings vs **{time_stats['recurring_vs_adhoc']['recurring']}** recurring")
    
    # Top collaborators insight
    md.append("\n### Key Collaborators")
    top_5 = sorted_stakeholders[:5]
    md.append("\nMost frequent collaborators (by time spent):")
    for i, (name, data) in enumerate(top_5, 1):
        months = len(data.get('months_active', []))
        md.append(f"{i}. **{name}** - {data['hours']:.1f} hours across {data['count']} meetings ({months} months)")
    
    # Recommendations
    md.append("\n---\n")
    md.append("## Recommendations for Calibration Document\n")
    
    md.append("\n### Quantifiable Metrics to Highlight")
    md.append(f"- Maintained engagement with **{total_stakeholders}+ stakeholders** throughout FY26")
    md.append(f"- Invested **{customer_hours:.1f} hours** in direct customer/external engagements")
    md.append(f"- Participated in **{work_relevant_events}** work-relevant meetings/activities")
    md.append(f"- Sustained collaboration across **{len(time_stats['by_month'])} months** of the fiscal year")
    
    md.append("\n### Areas of Focus to Emphasize")
    
    # Identify top meeting types
    top_activity = sorted_types[0] if sorted_types else None
    if top_activity:
        md.append(f"- Primary focus on **{top_activity[0]}** ({top_activity[1]['hours']:.1f} hours, {top_activity[1]['hours']/total_hours*100:.1f}% of time)")
    
    md.append(f"- Strong **1:1 engagement** pattern ({size_dist.get('1:1 (2 people)', 0)} individual meetings)")
    md.append(f"- Balanced internal and external collaboration")
    
    md.append("\n### Data Quality Notes")
    md.append("- Some email domains may be truncated (Au, Aut, Auto, etc.) - likely Autodesk variations")
    md.append("- 'Unknown' company entries may need manual review for accurate external org attribution")
    md.append("- Consider manually categorizing key customer engagements from the detailed JSON files")
    
    md.append("\n---\n")
    md.append("\n*This analysis is based on calendar data and should be supplemented with qualitative descriptions of impact and outcomes.*")
    
    return '\n'.join(md)


def main():
    """Main execution."""
    print("Loading analysis data...")
    calendar_data, stakeholder_data = load_analysis_data()
    
    print("Generating calibration summary...")
    markdown = generate_markdown_summary(calendar_data, stakeholder_data)
    
    output_file = "FY26/analysis_outputs/calibration_summary.md"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(markdown)
    
    print(f"\n[OK] Calibration summary generated: {output_file}")
    print("\nSummary includes:")
    print("  - Executive metrics")
    print("  - Top stakeholder engagements")
    print("  - Time distribution analysis")
    print("  - Work pattern insights")
    print("  - Recommendations for calibration document")


if __name__ == "__main__":
    main()

