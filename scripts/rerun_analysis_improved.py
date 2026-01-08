#!/usr/bin/env python3
"""
Re-run complete analysis with improved categorization rules.
Addresses: Focus Fridays, laptop setup, reminders, business meals.
"""

import re
from datetime import datetime
from collections import defaultdict
import json
import sys


class CalendarEvent:
    """Represents a single calendar event."""
    
    def __init__(self):
        self.summary = ""
        self.dtstart = ""
        self.dtend = ""
        self.description = ""
        self.location = ""
        self.organizer = ""
        self.organizer_name = ""
        self.attendees = []
        self.busy_status = ""
        self.transp = ""
        self.status = ""
        
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
    elif field_name == "LOCATION":
        event.location = value
    elif field_name == "ORGANIZER":
        email_match = re.search(r'mailto:([^\s]+)', value)
        name_match = re.search(r'CN="?([^";:]+)"?', field)
        if email_match:
            event.organizer = email_match.group(1)
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
    elif field_name == "X-MICROSOFT-CDO-BUSYSTATUS":
        event.busy_status = value
    elif field_name == "TRANSP":
        event.transp = value


def is_actual_meeting(event: CalendarEvent) -> bool:
    """Check if event is an actual meeting (has attendees)."""
    return len(event.attendees) > 0


def categorize_event_final(event: CalendarEvent) -> str:
    """Final improved categorization with all rules."""
    summary_lower = event.summary.lower()
    desc_lower = event.description.lower()
    
    # Priority 0: Non-meetings (no attendees) - personal tasks/reminders
    if not is_actual_meeting(event):
        return "non_meetings_excluded"
    
    # Priority 1: Declined or Tentative
    if event.status in ["DECLINED", "TENTATIVE"]:
        return f"declined_tentative_{event.status.lower()}"
    
    # Priority 2: Out of Office
    if event.busy_status == "OOF":
        return "out_of_office"
    
    if any(keyword in summary_lower for keyword in [
        "out of office", "ooo", "pto", "vacation", "holiday"
    ]):
        return "personal_time_off"
    
    # Priority 3: Focus Fridays - EXCLUDE (not work meetings)
    if "focus friday" in summary_lower or "focus fridays" in summary_lower:
        return "focus_fridays_excluded"
    
    # Priority 4: Work-related admin (laptop, IT, setup) - INCLUDE as work
    if any(keyword in summary_lower for keyword in [
        "laptop", "new laptop", "it support", "setup", "infoworks icm cloud"
    ]):
        return "work_admin_it"
    
    # Priority 5: Personal appointments - EXCLUDE
    if any(keyword in summary_lower for keyword in [
        "dentist", "doctor", "personal bookings"
    ]) and not any(keyword in summary_lower for keyword in ["customer", "client"]):
        return "personal_appointments_excluded"
    
    # Priority 6: Meals - distinguish business from personal
    if any(keyword in summary_lower for keyword in ["lunch", "breakfast"]):
        # Business meals/networking
        if any(keyword in summary_lower or keyword in desc_lower for keyword in [
            "customer", "client", "dinner", "reception", "networking", 
            "team", "cs dinner", "ebcs", "awi"
        ]):
            return "business_meals_networking"
        else:
            return "breaks_personal_excluded"
    
    # Gym/workout
    if any(keyword in summary_lower for keyword in ["gym", "workout", "exercise"]):
        return "breaks_personal_excluded"
    
    # Priority 7: Transparent/Free time - EXCLUDE
    if event.transp == "TRANSPARENT" or event.busy_status == "FREE":
        return "free_time_transparent_excluded"
    
    # === WORK CATEGORIES BELOW ===
    
    # Customer/External (high priority for work)
    if any(keyword in summary_lower or keyword in desc_lower for keyword in [
        "customer", "client", "external", "demo", "presentation", 
        "sales", "prospect", "dinner", "reception"
    ]):
        return "customer_external"
    
    # 1:1s and syncs
    if any(keyword in summary_lower for keyword in [
        "1:1", "one on one", "1-1", "sync", "catch up", "check in"
    ]):
        return "internal_meetings_1on1_sync"
    
    # Training/Learning
    if any(keyword in summary_lower for keyword in [
        "training", "workshop", "learning", "course", "webinar",
        "certification", "onboarding"
    ]):
        return "training_learning"
    
    # Project/Planning
    if any(keyword in summary_lower for keyword in [
        "planning", "roadmap", "strategy", "review", "retrospective",
        "sprint", "scrum", "project", "initiative", "backlog", "refinement"
    ]):
        return "planning_strategy"
    
    # Recruiting/Hiring
    if any(keyword in summary_lower for keyword in [
        "interview", "candidate", "hiring", "recruiting", "screening"
    ]):
        return "recruiting_hiring"
    
    # Focus/Blocked Time (but not Focus Fridays)
    if any(keyword in summary_lower for keyword in [
        "focus time", "blocked", "do not book", "dnb",
        "heads down", "deep work", "no meetings"
    ]) and "friday" not in summary_lower:
        return "focus_time_blocked"
    
    # Default: Check if busy
    if event.busy_status == "BUSY" or event.transp == "OPAQUE":
        return "general_work_meetings"
    
    return "uncategorized"


def is_work_relevant_final(category: str) -> bool:
    """Determine if a category is work-relevant."""
    excluded_categories = [
        'declined_tentative_declined',
        'declined_tentative_tentative',
        'out_of_office',
        'personal_time_off',
        'breaks_personal_excluded',
        'free_time_transparent_excluded',
        'focus_fridays_excluded',
        'personal_appointments_excluded',
        'non_meetings_excluded'
    ]
    return category not in excluded_categories


def main():
    """Main execution."""
    calendar_file = "FY26/inputs/Daniel Moreira Calendar.ics"
    
    print("=" * 100)
    print("IMPROVED CALENDAR ANALYSIS - FINAL VERSION")
    print("=" * 100)
    print(f"\nParsing: {calendar_file}")
    
    events = parse_ics_file(calendar_file)
    print(f"[OK] Parsed {len(events)} events\n")
    
    # Categorize all events
    categorized = defaultdict(list)
    for event in events:
        category = categorize_event_final(event)
        categorized[category].append(event)
    
    # Calculate statistics
    total_events = len(events)
    work_categories = [cat for cat in categorized.keys() if is_work_relevant_final(cat)]
    excluded_categories = [cat for cat in categorized.keys() if not is_work_relevant_final(cat)]
    
    work_events = sum(len(categorized[cat]) for cat in work_categories)
    excluded_events = sum(len(categorized[cat]) for cat in excluded_categories)
    
    work_hours = sum(
        sum(e.get_duration_hours() for e in categorized[cat])
        for cat in work_categories
    )
    
    excluded_hours = sum(
        sum(e.get_duration_hours() for e in categorized[cat])
        for cat in excluded_categories
    )
    
    # Print summary
    print("=" * 100)
    print("CATEGORIZATION SUMMARY")
    print("=" * 100)
    
    print(f"\n{'Category':<50} {'Count':<10} {'Hours':<10} {'% Events':<10}")
    print("-" * 100)
    
    # Sort by count
    sorted_cats = sorted(categorized.items(), key=lambda x: len(x[1]), reverse=True)
    
    for cat, cat_events in sorted_cats:
        count = len(cat_events)
        hours = sum(e.get_duration_hours() for e in cat_events)
        pct = (count / total_events * 100) if total_events > 0 else 0
        
        work_marker = "[WORK]" if is_work_relevant_final(cat) else "[EXCL]"
        cat_display = f"{work_marker} {cat}"
        
        print(f"{cat_display[:49]:<50} {count:<10} {hours:<10.1f} {pct:<10.1f}%")
    
    # Work vs Excluded summary
    print("\n" + "=" * 100)
    print("WORK-RELEVANT vs EXCLUDED")
    print("=" * 100)
    
    print(f"\n[WORK] Work-Relevant Events:")
    print(f"  Count: {work_events} ({work_events/total_events*100:.1f}%)")
    print(f"  Hours: {work_hours:.1f}")
    
    print(f"\n[EXCL] Excluded Events:")
    print(f"  Count: {excluded_events} ({excluded_events/total_events*100:.1f}%)")
    print(f"  Hours: {excluded_hours:.1f}")
    
    # Key changes
    print("\n" + "=" * 100)
    print("KEY CATEGORIZATION CHANGES")
    print("=" * 100)
    
    print(f"\n1. Non-Meetings (0 attendees): {len(categorized['non_meetings_excluded'])} events ({sum(e.get_duration_hours() for e in categorized['non_meetings_excluded']):.1f}h) - EXCLUDED")
    print(f"2. Focus Fridays: {len(categorized.get('focus_fridays_excluded', []))} events ({sum(e.get_duration_hours() for e in categorized.get('focus_fridays_excluded', [])):.1f}h) - EXCLUDED")
    print(f"3. Work Admin/IT: {len(categorized.get('work_admin_it', []))} events ({sum(e.get_duration_hours() for e in categorized.get('work_admin_it', [])):.1f}h) - INCLUDED as work")
    print(f"4. Business Meals: {len(categorized.get('business_meals_networking', []))} events ({sum(e.get_duration_hours() for e in categorized.get('business_meals_networking', [])):.1f}h) - INCLUDED as work")
    print(f"5. Personal Appointments: {len(categorized.get('personal_appointments_excluded', []))} events - EXCLUDED")
    
    # Uncategorized remaining
    uncategorized_count = len(categorized['uncategorized'])
    uncategorized_hours = sum(e.get_duration_hours() for e in categorized['uncategorized'])
    
    print(f"\nRemaining Uncategorized: {uncategorized_count} events ({uncategorized_hours:.1f}h)")
    if uncategorized_count > 0:
        print("  Sample titles:")
        for e in categorized['uncategorized'][:10]:
            title = e.summary[:60] if e.summary else "[BLANK]"
            print(f"    - {title}")
    
    # Export updated analysis
    output = {
        'summary': {
            'total_events': total_events,
            'work_relevant_events': work_events,
            'work_relevant_hours': round(work_hours, 2),
            'excluded_events': excluded_events,
            'excluded_hours': round(excluded_hours, 2)
        },
        'by_category': {}
    }
    
    for cat, cat_events in categorized.items():
        output['by_category'][cat] = {
            'count': len(cat_events),
            'hours': round(sum(e.get_duration_hours() for e in cat_events), 2),
            'is_work_relevant': is_work_relevant_final(cat),
            'sample_events': [
                {
                    'summary': e.summary[:80],
                    'duration_hours': round(e.get_duration_hours(), 2)
                }
                for e in cat_events[:5]
            ]
        }
    
    output_file = 'FY26/analysis_outputs/improved_calendar_analysis.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2)
    
    print(f"\n[OK] Improved analysis exported to: {output_file}")
    
    print("\n" + "=" * 100)


if __name__ == "__main__":
    main()

