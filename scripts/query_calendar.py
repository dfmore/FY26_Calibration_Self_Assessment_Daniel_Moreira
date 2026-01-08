#!/usr/bin/env python3
"""
Interactive Calendar Query Tool
Allows querying specific stakeholders, time periods, or meeting types.
"""

import json
import sys
from collections import defaultdict


def load_data():
    """Load analysis data."""
    with open('FY26/analysis_outputs/stakeholder_analysis.json', 'r', encoding='utf-8') as f:
        return json.load(f)


def query_stakeholder(data, name_search):
    """Query specific stakeholder by name."""
    results = []
    
    for name, info in data['stakeholders'].items():
        if name_search.lower() in name.lower():
            results.append((name, info))
    
    if not results:
        print(f"\nNo stakeholders found matching '{name_search}'")
        return
    
    print(f"\n{'='*80}")
    print(f"STAKEHOLDER SEARCH RESULTS: '{name_search}'")
    print(f"{'='*80}\n")
    
    for name, info in sorted(results, key=lambda x: x[1]['hours'], reverse=True):
        print(f"\nName: {name}")
        print(f"  Total Meetings: {info['count']}")
        print(f"  Total Hours: {info['hours']:.1f}")
        print(f"  Companies: {', '.join(info['companies'])}")
        print(f"  Months Active: {', '.join(sorted(info['months_active']))}")
        print(f"  As Organizer: {info['as_organizer']} | As Attendee: {info['as_attendee']}")
        
        if info['meeting_types']:
            print(f"  Meeting Types:")
            for mtype, count in sorted(info['meeting_types'].items(), key=lambda x: x[1], reverse=True):
                print(f"    - {mtype}: {count}")


def query_month(data, month):
    """Query specific month."""
    time_stats = data['time_stats']
    
    if month not in time_stats['by_month']:
        print(f"\nNo data found for month '{month}'")
        print(f"Available months: {', '.join(sorted(time_stats['by_month'].keys()))}")
        return
    
    month_data = time_stats['by_month'][month]
    
    print(f"\n{'='*80}")
    print(f"MONTH ANALYSIS: {month}")
    print(f"{'='*80}\n")
    print(f"Total Meetings: {month_data['count']}")
    print(f"Total Hours: {month_data['hours']:.1f}")
    print(f"Average Duration: {month_data['hours']/month_data['count']:.2f} hours")
    
    # Find stakeholders active in this month
    active_stakeholders = []
    for name, info in data['stakeholders'].items():
        if month in info['months_active']:
            active_stakeholders.append((name, info['hours'], info['count']))
    
    print(f"\nTop 10 Stakeholders in {month}:")
    for i, (name, hours, count) in enumerate(sorted(active_stakeholders, key=lambda x: x[1], reverse=True)[:10], 1):
        print(f"  {i}. {name}: {hours:.1f} hours ({count} meetings)")


def query_company(data, company_search):
    """Query specific company/organization."""
    results = defaultdict(lambda: {'people': [], 'total_hours': 0, 'total_meetings': 0})
    
    for name, info in data['stakeholders'].items():
        for company in info['companies']:
            if company_search.lower() in company.lower():
                results[company]['people'].append((name, info['hours'], info['count']))
                results[company]['total_hours'] += info['hours']
                results[company]['total_meetings'] += info['count']
    
    if not results:
        print(f"\nNo companies found matching '{company_search}'")
        return
    
    print(f"\n{'='*80}")
    print(f"COMPANY SEARCH RESULTS: '{company_search}'")
    print(f"{'='*80}\n")
    
    for company, info in sorted(results.items(), key=lambda x: x[1]['total_hours'], reverse=True):
        print(f"\nCompany: {company}")
        print(f"  Total Hours: {info['total_hours']:.1f}")
        print(f"  Total Meetings: {info['total_meetings']}")
        print(f"  People Engaged ({len(info['people'])}):")
        
        for name, hours, count in sorted(info['people'], key=lambda x: x[1], reverse=True)[:10]:
            print(f"    - {name}: {hours:.1f} hours ({count} meetings)")


def list_top_stakeholders(data, n=20):
    """List top N stakeholders."""
    print(f"\n{'='*80}")
    print(f"TOP {n} STAKEHOLDERS BY TIME")
    print(f"{'='*80}\n")
    
    sorted_stakeholders = sorted(
        data['stakeholders'].items(),
        key=lambda x: x[1]['hours'],
        reverse=True
    )[:n]
    
    print(f"{'Rank':<6} {'Name':<35} {'Hours':<10} {'Meetings':<10} {'Company':<20}")
    print("-" * 85)
    
    for i, (name, info) in enumerate(sorted_stakeholders, 1):
        company = info['companies'][0] if info['companies'] else 'Unknown'
        print(f"{i:<6} {name[:34]:<35} {info['hours']:<10.1f} {info['count']:<10} {company[:19]:<20}")


def show_summary(data):
    """Show overall summary."""
    time_stats = data['time_stats']
    
    print(f"\n{'='*80}")
    print("CALENDAR ANALYSIS SUMMARY")
    print(f"{'='*80}\n")
    
    total_stakeholders = len(data['stakeholders'])
    internal = sum(1 for s in data['stakeholders'].values() if 'Autodesk (Internal)' in s.get('companies', []))
    external = total_stakeholders - internal
    
    print(f"Total Stakeholders: {total_stakeholders}")
    print(f"  Internal: {internal}")
    print(f"  External: {external}")
    
    total_hours = sum(m['hours'] for m in time_stats['by_month'].values())
    total_meetings = sum(m['count'] for m in time_stats['by_month'].values())
    
    print(f"\nTotal Work Hours: {total_hours:.1f}")
    print(f"Total Meetings: {total_meetings}")
    print(f"Average Meeting Duration: {total_hours/total_meetings:.2f} hours")
    
    print(f"\nTime by Meeting Type:")
    for mtype, mdata in sorted(time_stats['by_meeting_type'].items(), key=lambda x: x[1]['hours'], reverse=True):
        pct = (mdata['hours'] / total_hours * 100) if total_hours > 0 else 0
        print(f"  {mtype}: {mdata['hours']:.1f} hours ({pct:.1f}%)")
    
    print(f"\nMonthly Breakdown:")
    for month in sorted(time_stats['by_month'].keys()):
        mdata = time_stats['by_month'][month]
        print(f"  {month}: {mdata['count']} meetings, {mdata['hours']:.1f} hours")


def print_help():
    """Print help message."""
    print("""
Calendar Query Tool - Usage:

  python query_calendar.py summary                    - Show overall summary
  python query_calendar.py top [N]                    - List top N stakeholders (default 20)
  python query_calendar.py stakeholder <name>         - Search for stakeholder by name
  python query_calendar.py month <YYYY-MM>            - Analyze specific month
  python query_calendar.py company <name>             - Search for company/organization
  
Examples:
  python query_calendar.py stakeholder "Mike"
  python query_calendar.py month 2025-10
  python query_calendar.py company "Arcadis"
  python query_calendar.py top 30
""")


def main():
    """Main execution."""
    if len(sys.argv) < 2:
        print_help()
        return
    
    command = sys.argv[1].lower()
    
    data = load_data()
    
    if command == 'summary':
        show_summary(data)
    
    elif command == 'top':
        n = int(sys.argv[2]) if len(sys.argv) > 2 else 20
        list_top_stakeholders(data, n)
    
    elif command == 'stakeholder':
        if len(sys.argv) < 3:
            print("Error: Please provide stakeholder name to search")
            print("Usage: python query_calendar.py stakeholder <name>")
            return
        name_search = ' '.join(sys.argv[2:])
        query_stakeholder(data, name_search)
    
    elif command == 'month':
        if len(sys.argv) < 3:
            print("Error: Please provide month in YYYY-MM format")
            print("Usage: python query_calendar.py month <YYYY-MM>")
            return
        month = sys.argv[2]
        query_month(data, month)
    
    elif command == 'company':
        if len(sys.argv) < 3:
            print("Error: Please provide company name to search")
            print("Usage: python query_calendar.py company <name>")
            return
        company_search = ' '.join(sys.argv[2:])
        query_company(data, company_search)
    
    else:
        print(f"Unknown command: {command}")
        print_help()


if __name__ == "__main__":
    main()

