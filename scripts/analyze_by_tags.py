#!/usr/bin/env python3
"""
Tag-Based Calendar Analysis
Analyzes calendar events by their CATEGORIES tags to show major work responsibilities.
"""

import re
from datetime import datetime
from collections import defaultdict, Counter
import json


class CalendarEvent:
    """Represents a single calendar event."""
    
    def __init__(self):
        self.summary = ""
        self.dtstart = ""
        self.dtend = ""
        self.description = ""
        self.organizer_name = ""
        self.attendees = []
        self.categories = []
        self.status = ""
        self.busy_status = ""
        self.transp = ""
        
    def get_duration_hours(self) -> float:
        """Calculate event duration in hours."""
        try:
            start_str = self.dtstart.split('TZID=')[-1] if 'TZID=' in self.dtstart else self.dtstart
            end_str = self.dtend.split('TZID=')[-1] if 'TZID=' in self.dtend else self.dtend
            
            start_match = re.search(r'(\d{8}T\d{6})', start_str)
            end_match = re.search(r'(\d{8}T\d{6})', end_str)
            
            if start_match and end_match:
                start = datetime.strptime(start_match.group(1), '%Y%m%dT%H%M%S')
                end = datetime.strptime(end_match.group(1), '%Y%m%dT%H%M%S')
                return (end - start).total_seconds() / 3600
        except Exception:
            pass
        return 0.0
    
    def get_month(self) -> str:
        """Extract month from event."""
        try:
            start_str = self.dtstart.split('TZID=')[-1] if 'TZID=' in self.dtstart else self.dtstart
            date_match = re.search(r'(\d{8})', start_str)
            if date_match:
                date_str = date_match.group(1)
                dt = datetime.strptime(date_str, '%Y%m%d')
                return dt.strftime('%Y-%m')
        except Exception:
            pass
        return ""


def parse_ics_file(filepath: str) -> list:
    """Parse ICS file and extract events."""
    events = []
    current_event = None
    current_field = None
    continuation_value = ""
    
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.rstrip('\n\r')
            
            if line.startswith((' ', '\t')) and current_field:
                continuation_value += line.strip()
                continue
            
            if current_field and continuation_value:
                process_field(current_event, current_field, continuation_value)
                current_field = None
                continuation_value = ""
            
            if line == "BEGIN:VEVENT":
                current_event = CalendarEvent()
            elif line == "END:VEVENT" and current_event:
                events.append(current_event)
                current_event = None
            elif current_event and ':' in line:
                field, value = line.split(':', 1)
                
                if not line.endswith('='):
                    process_field(current_event, field, value)
                    current_field = None
                else:
                    current_field = field
                    continuation_value = value
    
    return events


def process_field(event: CalendarEvent, field: str, value: str):
    """Process a single field and update the event object."""
    field_name = field.split(';')[0]
    
    if field_name == "SUMMARY":
        event.summary = value.encode('ascii', 'ignore').decode('ascii')
    elif field_name == "DTSTART":
        event.dtstart = field + ':' + value
    elif field_name == "DTEND":
        event.dtend = field + ':' + value
    elif field_name == "DESCRIPTION":
        event.description = value[:500]
    elif field_name == "ORGANIZER":
        name_match = re.search(r'CN="?([^";:]+)"?', field)
        if name_match:
            event.organizer_name = name_match.group(1)
    elif field_name == "ATTENDEE":
        partstat_match = re.search(r'PARTSTAT=([^;:]+)', field)
        email_match = re.search(r'mailto:([^\s]+)', value)
        name_match = re.search(r'CN="?([^";:]+)"?', field)
        
        if 'daniel.moreira@autodesk.com' in value.lower():
            if partstat_match:
                event.status = partstat_match.group(1)
        
        if email_match:
            attendee_info = {
                'email': email_match.group(1),
                'name': name_match.group(1) if name_match else email_match.group(1).split('@')[0]
            }
            event.attendees.append(attendee_info)
    elif field_name == "CATEGORIES":
        event.categories = [cat.strip() for cat in value.split(',')]
    elif field_name == "X-MICROSOFT-CDO-BUSYSTATUS":
        event.busy_status = value
    elif field_name == "TRANSP":
        event.transp = value


def is_work_relevant(event: CalendarEvent) -> bool:
    """Determine if event is work-relevant meeting."""
    # Must have attendees (actual meeting)
    if len(event.attendees) == 0:
        return False
    
    # Exclude declined/tentative
    if event.status in ["DECLINED", "TENTATIVE"]:
        return False
    
    # Exclude OOO
    if event.busy_status == "OOF":
        return False
    
    # Exclude transparent/free time
    if event.transp == "TRANSPARENT" or event.busy_status == "FREE":
        return False
    
    return True


def analyze_by_tags(events: list):
    """Analyze events grouped by their CATEGORIES tags."""
    
    # Filter to work-relevant meetings only
    work_events = [e for e in events if is_work_relevant(e)]
    
    # Group by tags
    by_tag = defaultdict(list)
    no_tag = []
    
    for event in work_events:
        if event.categories:
            for category in event.categories:
                by_tag[category].append(event)
        else:
            no_tag.append(event)
    
    # Calculate statistics
    tag_stats = {}
    for tag, tag_events in by_tag.items():
        total_hours = sum(e.get_duration_hours() for e in tag_events)
        months_active = set(e.get_month() for e in tag_events if e.get_month())
        
        tag_stats[tag] = {
            'count': len(tag_events),
            'hours': total_hours,
            'months_active': sorted(list(months_active)),
            'sample_events': [
                {
                    'summary': e.summary[:80],
                    'organizer': e.organizer_name,
                    'duration_hours': round(e.get_duration_hours(), 2)
                }
                for e in tag_events[:5]
            ]
        }
    
    return tag_stats, no_tag, work_events


def print_tag_analysis(tag_stats: dict, no_tag: list, work_events: list):
    """Print tag-based analysis report."""
    
    print("=" * 100)
    print("TAG-BASED CALENDAR ANALYSIS")
    print("=" * 100)
    
    total_work_events = len(work_events)
    total_work_hours = sum(e.get_duration_hours() for e in work_events)
    
    print(f"\nTotal Work-Relevant Meetings: {total_work_events}")
    print(f"Total Work Hours: {total_work_hours:.1f}")
    
    tagged_events = sum(stats['count'] for stats in tag_stats.values())
    tagged_hours = sum(stats['hours'] for stats in tag_stats.values())
    
    print(f"\nTagged Meetings: {tagged_events} ({tagged_events/total_work_events*100:.1f}%)")
    print(f"Untagged Meetings: {len(no_tag)} ({len(no_tag)/total_work_events*100:.1f}%)")
    
    print("\n" + "=" * 100)
    print("BREAKDOWN BY TAG")
    print("=" * 100)
    
    # Sort by hours
    sorted_tags = sorted(tag_stats.items(), key=lambda x: x[1]['hours'], reverse=True)
    
    print(f"\n{'Tag':<30} {'Meetings':<12} {'Hours':<12} {'% of Tagged':<15} {'Months Active':<15}")
    print("-" * 100)
    
    for tag, stats in sorted_tags:
        pct = (stats['hours'] / tagged_hours * 100) if tagged_hours > 0 else 0
        months = len(stats['months_active'])
        print(f"{tag[:29]:<30} {stats['count']:<12} {stats['hours']:<12.1f} {pct:<15.1f}% {months:<15}")
    
    # Detailed breakdown
    print("\n" + "=" * 100)
    print("DETAILED TAG ANALYSIS")
    print("=" * 100)
    
    for tag, stats in sorted_tags:
        print(f"\n{'-' * 100}")
        print(f"TAG: {tag}")
        print(f"{'-' * 100}")
        print(f"Meetings: {stats['count']}")
        print(f"Total Hours: {stats['hours']:.1f}")
        print(f"Months Active: {', '.join(stats['months_active'])}")
        
        print(f"\nSample Events:")
        for i, sample in enumerate(stats['sample_events'], 1):
            organizer = sample['organizer'] if sample['organizer'] else 'Unknown'
            print(f"  {i}. {sample['summary']}")
            print(f"     Organizer: {organizer} | Duration: {sample['duration_hours']}h")
    
    # Untagged summary
    if no_tag:
        print(f"\n{'-' * 100}")
        print(f"UNTAGGED MEETINGS: {len(no_tag)} events ({sum(e.get_duration_hours() for e in no_tag):.1f} hours)")
        print(f"{'-' * 100}")
        print("Sample untagged events:")
        for i, event in enumerate(no_tag[:10], 1):
            print(f"  {i}. {event.summary[:70]}")
    
    print("\n" + "=" * 100)


def export_tag_analysis(tag_stats: dict, no_tag: list, output_file: str):
    """Export tag analysis to JSON."""
    
    output = {
        'by_tag': tag_stats,
        'untagged_count': len(no_tag),
        'untagged_hours': sum(e.get_duration_hours() for e in no_tag),
        'untagged_samples': [
            {
                'summary': e.summary,
                'duration_hours': e.get_duration_hours(),
                'organizer': e.organizer_name
            }
            for e in no_tag[:20]
        ]
    }
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, default=str)
    
    print(f"\n[OK] Tag analysis exported to: {output_file}")


def main():
    """Main execution."""
    calendar_file = "FY26/inputs/Daniel Moreira Calendar.ics"
    output_json = "FY26/analysis_outputs/tag_analysis.json"
    
    print(f"Parsing calendar file: {calendar_file}")
    events = parse_ics_file(calendar_file)
    print(f"[OK] Parsed {len(events)} events\n")
    
    print("Analyzing by tags...")
    tag_stats, no_tag, work_events = analyze_by_tags(events)
    
    print_tag_analysis(tag_stats, no_tag, work_events)
    export_tag_analysis(tag_stats, no_tag, output_json)


if __name__ == "__main__":
    main()

