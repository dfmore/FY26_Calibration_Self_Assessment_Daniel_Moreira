#!/usr/bin/env python3
"""
Calendar Analysis Script
Parses ICS calendar file and categorizes events for work relevance analysis.
"""

import re
from datetime import datetime
from collections import defaultdict
from typing import Dict, List, Tuple
import json


class CalendarEvent:
    """Represents a single calendar event with relevant fields."""
    
    def __init__(self):
        self.summary = ""
        self.dtstart = ""
        self.dtend = ""
        self.description = ""
        self.location = ""
        self.organizer = ""
        self.attendees = []
        self.categories = []
        self.status = ""  # ACCEPTED, DECLINED, TENTATIVE
        self.busy_status = ""  # FREE, BUSY, TENTATIVE, OOF
        self.transp = ""  # TRANSPARENT, OPAQUE
        self.created = ""
        self.uid = ""
        self.is_recurring = False
        self.recurrence_id = ""
        
    def get_duration_hours(self) -> float:
        """Calculate event duration in hours."""
        try:
            # Parse datetime strings - handle timezone info
            start_str = self.dtstart.split('TZID=')[-1] if 'TZID=' in self.dtstart else self.dtstart
            end_str = self.dtend.split('TZID=')[-1] if 'TZID=' in self.dtend else self.dtend
            
            # Extract just the datetime part
            start_match = re.search(r'(\d{8}T\d{6})', start_str)
            end_match = re.search(r'(\d{8}T\d{6})', end_str)
            
            if start_match and end_match:
                start = datetime.strptime(start_match.group(1), '%Y%m%dT%H%M%S')
                end = datetime.strptime(end_match.group(1), '%Y%m%dT%H%M%S')
                return (end - start).total_seconds() / 3600
        except Exception:
            pass
        return 0.0


def parse_ics_file(filepath: str) -> List[CalendarEvent]:
    """Parse ICS file and extract events."""
    events = []
    current_event = None
    current_field = None
    continuation_value = ""
    
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.rstrip('\n\r')
            
            # Handle line continuation (starts with space or tab)
            if line.startswith((' ', '\t')) and current_field:
                continuation_value += line.strip()
                continue
            
            # Process previous field if we have continuation
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
                
                # Check if this might continue on next line
                if not line.endswith('='):
                    process_field(current_event, field, value)
                    current_field = None
                else:
                    current_field = field
                    continuation_value = value
    
    return events


def process_field(event: CalendarEvent, field: str, value: str):
    """Process a single field and update the event object."""
    # Handle fields with parameters (e.g., DTSTART;TZID=...)
    field_name = field.split(';')[0]
    
    if field_name == "SUMMARY":
        # Remove emojis and non-ASCII characters for console compatibility
        event.summary = value.encode('ascii', 'ignore').decode('ascii')
    elif field_name == "DTSTART":
        event.dtstart = field + ':' + value
    elif field_name == "DTEND":
        event.dtend = field + ':' + value
    elif field_name == "DESCRIPTION":
        event.description = value[:500]  # Truncate long descriptions
    elif field_name == "LOCATION":
        event.location = value
    elif field_name == "ORGANIZER":
        # Extract email from mailto:
        email_match = re.search(r'mailto:([^\s]+)', value)
        if email_match:
            event.organizer = email_match.group(1)
    elif field_name == "ATTENDEE":
        # Extract participation status and email
        partstat_match = re.search(r'PARTSTAT=([^;:]+)', field)
        email_match = re.search(r'mailto:([^\s]+)', value)
        
        if 'daniel.moreira@autodesk.com' in value.lower():
            if partstat_match:
                event.status = partstat_match.group(1)
        
        if email_match:
            attendee_info = {'email': email_match.group(1)}
            if partstat_match:
                attendee_info['status'] = partstat_match.group(1)
            event.attendees.append(attendee_info)
    elif field_name == "CATEGORIES":
        event.categories = [cat.strip() for cat in value.split(',')]
    elif field_name == "X-MICROSOFT-CDO-BUSYSTATUS":
        event.busy_status = value
    elif field_name == "TRANSP":
        event.transp = value
    elif field_name == "CREATED":
        event.created = value
    elif field_name == "UID":
        event.uid = value
    elif field_name == "RRULE":
        event.is_recurring = True
    elif field_name == "RECURRENCE-ID":
        event.recurrence_id = value


def categorize_event(event: CalendarEvent) -> str:
    """Categorize event based on various criteria."""
    summary_lower = event.summary.lower()
    desc_lower = event.description.lower()
    
    # Priority 1: Declined or Tentative
    if event.status in ["DECLINED", "TENTATIVE"]:
        return f"declined_tentative_{event.status.lower()}"
    
    # Priority 2: Out of Office / Personal
    if event.busy_status == "OOF":
        return "out_of_office"
    
    if any(keyword in summary_lower for keyword in [
        "out of office", "ooo", "pto", "vacation", "holiday", 
        "personal", "dentist", "doctor", "appointment"
    ]):
        return "personal_time_off"
    
    # Priority 3: Breaks and Personal Care
    if any(keyword in summary_lower for keyword in [
        "lunch", "breakfast", "dinner", "coffee break", "break",
        "gym", "workout", "exercise"
    ]):
        return "breaks_personal_care"
    
    # Priority 4: Transparent/Free time
    if event.transp == "TRANSPARENT" or event.busy_status == "FREE":
        return "free_time_transparent"
    
    # Priority 5: Work Categories
    
    # Internal meetings
    if any(keyword in summary_lower for keyword in [
        "1:1", "one on one", "1-1", "sync", "standup", "stand-up",
        "team meeting", "all hands", "town hall", "skip level"
    ]):
        return "internal_meetings_1on1_sync"
    
    # Customer/External
    if any(keyword in summary_lower or keyword in desc_lower for keyword in [
        "customer", "client", "external", "demo", "presentation",
        "sales", "prospect"
    ]):
        return "customer_external"
    
    # Training/Learning
    if any(keyword in summary_lower for keyword in [
        "training", "workshop", "learning", "course", "webinar",
        "certification", "onboarding"
    ]):
        return "training_learning"
    
    # Project/Planning
    if any(keyword in summary_lower for keyword in [
        "planning", "roadmap", "strategy", "review", "retrospective",
        "sprint", "scrum", "project", "initiative"
    ]):
        return "planning_strategy"
    
    # Recruiting/Hiring
    if any(keyword in summary_lower for keyword in [
        "interview", "candidate", "hiring", "recruiting", "screening"
    ]):
        return "recruiting_hiring"
    
    # Focus/Blocked Time
    if any(keyword in summary_lower for keyword in [
        "focus", "focus time", "blocked", "do not book", "dnb",
        "heads down", "deep work", "no meetings"
    ]):
        return "focus_time_blocked"
    
    # Default: General Work
    if event.busy_status == "BUSY" or event.transp == "OPAQUE":
        return "general_work_meetings"
    
    return "uncategorized"


def analyze_calendar(events: List[CalendarEvent]) -> Dict:
    """Analyze events and generate statistics."""
    categories = defaultdict(list)
    stats = {
        'total_events': len(events),
        'by_category': {},
        'by_status': defaultdict(int),
        'by_busy_status': defaultdict(int),
        'total_hours_by_category': defaultdict(float),
    }
    
    for event in events:
        category = categorize_event(event)
        categories[category].append(event)
        
        duration = event.get_duration_hours()
        stats['total_hours_by_category'][category] += duration
        
        if event.status:
            stats['by_status'][event.status] += 1
        if event.busy_status:
            stats['by_busy_status'][event.busy_status] += 1
    
    # Calculate category stats
    for category, cat_events in categories.items():
        stats['by_category'][category] = {
            'count': len(cat_events),
            'total_hours': round(stats['total_hours_by_category'][category], 2),
            'sample_events': [
                {
                    'summary': e.summary[:80],
                    'start': e.dtstart.split(':')[-1][:15] if e.dtstart else '',
                    'duration_hours': round(e.get_duration_hours(), 2),
                    'status': e.status,
                    'busy_status': e.busy_status
                }
                for e in cat_events[:5]  # First 5 samples
            ]
        }
    
    return dict(categories), stats


def print_analysis(categories: Dict, stats: Dict):
    """Print analysis results in a readable format."""
    print("=" * 80)
    print("CALENDAR ANALYSIS REPORT")
    print("=" * 80)
    print(f"\nTotal Events: {stats['total_events']}")
    print(f"\nStatus Breakdown:")
    for status, count in sorted(stats['by_status'].items()):
        print(f"  {status}: {count}")
    
    print(f"\nBusy Status Breakdown:")
    for status, count in sorted(stats['by_busy_status'].items()):
        print(f"  {status}: {count}")
    
    print("\n" + "=" * 80)
    print("EVENTS BY CATEGORY")
    print("=" * 80)
    
    # Sort categories by relevance
    category_order = [
        "declined_tentative_declined",
        "declined_tentative_tentative",
        "out_of_office",
        "personal_time_off",
        "breaks_personal_care",
        "free_time_transparent",
        "focus_time_blocked",
        "customer_external",
        "planning_strategy",
        "internal_meetings_1on1_sync",
        "recruiting_hiring",
        "training_learning",
        "general_work_meetings",
        "uncategorized"
    ]
    
    for category in category_order:
        if category not in stats['by_category']:
            continue
            
        cat_stats = stats['by_category'][category]
        print(f"\n{'-' * 80}")
        print(f"[*] {category.upper().replace('_', ' ')}")
        print(f"{'-' * 80}")
        print(f"Count: {cat_stats['count']} events | Total Hours: {cat_stats['total_hours']}")
        print(f"\nSample Events:")
        
        for i, sample in enumerate(cat_stats['sample_events'], 1):
            print(f"  {i}. {sample['summary']}")
            print(f"     Start: {sample['start']} | Duration: {sample['duration_hours']}h | "
                  f"Status: {sample['status'] or 'N/A'} | Busy: {sample['busy_status'] or 'N/A'}")
    
    print("\n" + "=" * 80)
    print("WORK RELEVANCE SUMMARY")
    print("=" * 80)
    
    # Calculate work-relevant vs non-relevant hours
    non_relevant = [
        "declined_tentative_declined",
        "declined_tentative_tentative",
        "out_of_office",
        "personal_time_off",
        "breaks_personal_care",
        "free_time_transparent"
    ]
    
    non_relevant_hours = sum(
        stats['by_category'].get(cat, {}).get('total_hours', 0)
        for cat in non_relevant
    )
    
    non_relevant_count = sum(
        stats['by_category'].get(cat, {}).get('count', 0)
        for cat in non_relevant
    )
    
    total_hours = sum(stats['total_hours_by_category'].values())
    work_relevant_hours = total_hours - non_relevant_hours
    work_relevant_count = stats['total_events'] - non_relevant_count
    
    print(f"\n[X] NON-WORK-RELEVANT:")
    print(f"   Events: {non_relevant_count} ({non_relevant_count/stats['total_events']*100:.1f}%)")
    print(f"   Hours: {non_relevant_hours:.1f} ({non_relevant_hours/total_hours*100:.1f}%)")
    
    print(f"\n[OK] WORK-RELEVANT:")
    print(f"   Events: {work_relevant_count} ({work_relevant_count/stats['total_events']*100:.1f}%)")
    print(f"   Hours: {work_relevant_hours:.1f} ({work_relevant_hours/total_hours*100:.1f}%)")
    
    print("\n" + "=" * 80)


def export_to_json(categories: Dict, stats: Dict, output_file: str):
    """Export analysis to JSON file."""
    output = {
        'stats': stats,
        'categories': {}
    }
    
    for category, events in categories.items():
        output['categories'][category] = [
            {
                'summary': e.summary,
                'start': e.dtstart,
                'end': e.dtend,
                'duration_hours': e.get_duration_hours(),
                'location': e.location,
                'organizer': e.organizer,
                'attendee_count': len(e.attendees),
                'status': e.status,
                'busy_status': e.busy_status,
                'categories': e.categories
            }
            for e in events
        ]
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, default=str)
    
    print(f"\n[OK] Detailed analysis exported to: {output_file}")


def main():
    """Main execution function."""
    calendar_file = "FY26/inputs/Daniel Moreira Calendar.ics"
    output_json = "FY26/analysis_outputs/calendar_analysis.json"
    
    print(f"Parsing calendar file: {calendar_file}")
    events = parse_ics_file(calendar_file)
    print(f"[OK] Parsed {len(events)} events")
    
    print("\nAnalyzing events...")
    categories, stats = analyze_calendar(events)
    
    print_analysis(categories, stats)
    export_to_json(categories, stats, output_json)


if __name__ == "__main__":
    main()

