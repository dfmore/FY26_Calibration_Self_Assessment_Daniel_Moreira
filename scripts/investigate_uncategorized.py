#!/usr/bin/env python3
"""
Investigate Uncategorized Events
Deep dive into events that weren't automatically categorized.
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
    
    def get_date(self) -> str:
        """Extract date from event."""
        try:
            start_str = self.dtstart.split('TZID=')[-1] if 'TZID=' in self.dtstart else self.dtstart
            date_match = re.search(r'(\d{8})', start_str)
            if date_match:
                date_str = date_match.group(1)
                dt = datetime.strptime(date_str, '%Y%m%d')
                return dt.strftime('%Y-%m-%d')
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
        event.summary = value
    elif field_name == "DTSTART":
        event.dtstart = field + ':' + value
    elif field_name == "DTEND":
        event.dtend = field + ':' + value
    elif field_name == "DESCRIPTION":
        event.description = value[:1000]
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


def categorize_event_improved(event: CalendarEvent) -> str:
    """Improved categorization with better rules."""
    summary_lower = event.summary.lower()
    desc_lower = event.description.lower()
    
    # Priority 1: Declined or Tentative
    if event.status in ["DECLINED", "TENTATIVE"]:
        return f"declined_tentative_{event.status.lower()}"
    
    # Priority 2: Out of Office / Personal
    if event.busy_status == "OOF":
        return "out_of_office"
    
    if any(keyword in summary_lower for keyword in [
        "out of office", "ooo", "pto", "vacation", "holiday"
    ]):
        return "personal_time_off"
    
    # Priority 3: Focus Fridays - EXCLUDE
    if "focus friday" in summary_lower or "focus fridays" in summary_lower:
        return "focus_fridays_excluded"
    
    # Priority 4: Work-related admin (laptop, IT, etc.)
    if any(keyword in summary_lower for keyword in [
        "laptop", "new laptop", "it support", "setup", "onboarding setup"
    ]):
        return "work_admin_it"
    
    # Priority 5: Personal appointments (dentist, doctor, etc.)
    if any(keyword in summary_lower for keyword in [
        "dentist", "doctor", "appointment", "personal"
    ]) and not any(keyword in summary_lower for keyword in ["customer", "client", "meeting"]):
        return "personal_appointments"
    
    # Priority 6: Breaks and meals (but exclude customer/business meals)
    if any(keyword in summary_lower for keyword in ["lunch", "breakfast", "gym", "workout"]):
        # Check if it's a business meal
        if any(keyword in summary_lower or keyword in desc_lower for keyword in [
            "customer", "client", "dinner", "reception", "networking", "team", "cs dinner"
        ]):
            return "business_meals_networking"
        else:
            return "breaks_personal_care"
    
    # Priority 7: Transparent/Free time
    if event.transp == "TRANSPARENT" or event.busy_status == "FREE":
        return "free_time_transparent"
    
    # Work categories below
    
    # 1:1s and syncs
    if any(keyword in summary_lower for keyword in [
        "1:1", "one on one", "1-1", "sync", "catch up", "check in"
    ]):
        return "internal_meetings_1on1_sync"
    
    # Customer/External
    if any(keyword in summary_lower or keyword in desc_lower for keyword in [
        "customer", "client", "external", "demo", "presentation", "sales", "prospect"
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
    
    # Default: Check if busy
    if event.busy_status == "BUSY" or event.transp == "OPAQUE":
        return "general_work_meetings"
    
    return "uncategorized"


def analyze_uncategorized(events: list):
    """Analyze uncategorized events in detail."""
    
    # Categorize all events with improved rules
    categorized = defaultdict(list)
    
    for event in events:
        category = categorize_event_improved(event)
        categorized[category].append(event)
    
    # Focus on uncategorized
    uncategorized = categorized['uncategorized']
    
    print("=" * 100)
    print("UNCATEGORIZED EVENTS ANALYSIS")
    print("=" * 100)
    print(f"\nTotal Uncategorized: {len(uncategorized)} events")
    print(f"Total Hours: {sum(e.get_duration_hours() for e in uncategorized):.1f}")
    
    # Analyze patterns
    print("\n" + "-" * 100)
    print("PATTERN ANALYSIS")
    print("-" * 100)
    
    # Blank titles
    blank_titles = [e for e in uncategorized if not e.summary.strip()]
    print(f"\nBlank Titles: {len(blank_titles)} events ({sum(e.get_duration_hours() for e in blank_titles):.1f} hours)")
    
    # By busy status
    by_status = defaultdict(int)
    for e in uncategorized:
        by_status[e.busy_status or 'None'] += 1
    
    print(f"\nBy Busy Status:")
    for status, count in sorted(by_status.items(), key=lambda x: x[1], reverse=True):
        print(f"  {status}: {count}")
    
    # By transparency
    by_transp = defaultdict(int)
    for e in uncategorized:
        by_transp[e.transp or 'None'] += 1
    
    print(f"\nBy Transparency:")
    for transp, count in sorted(by_transp.items(), key=lambda x: x[1], reverse=True):
        print(f"  {transp}: {count}")
    
    # Common words in titles
    all_words = []
    for e in uncategorized:
        if e.summary.strip():
            words = e.summary.lower().split()
            all_words.extend([w for w in words if len(w) > 3])
    
    word_freq = Counter(all_words)
    print(f"\nMost Common Words in Titles:")
    for word, count in word_freq.most_common(20):
        print(f"  {word}: {count}")
    
    # Sample events
    print("\n" + "-" * 100)
    print("SAMPLE UNCATEGORIZED EVENTS (First 50)")
    print("-" * 100)
    print(f"{'Date':<12} {'Duration':<8} {'Status':<10} {'Transp':<12} {'Title':<60}")
    print("-" * 100)
    
    for i, event in enumerate(uncategorized[:50], 1):
        date = event.get_date()
        duration = event.get_duration_hours()
        status = event.busy_status or 'N/A'
        transp = event.transp or 'N/A'
        title = event.summary[:59] if event.summary else "[BLANK]"
        
        print(f"{date:<12} {duration:<8.1f} {status:<10} {transp:<12} {title:<60}")
    
    # Check for reclassifications
    print("\n" + "=" * 100)
    print("RECLASSIFICATION SUMMARY")
    print("=" * 100)
    
    print(f"\nNew Categories Created:")
    new_categories = [
        'focus_fridays_excluded',
        'work_admin_it',
        'business_meals_networking',
        'personal_appointments'
    ]
    
    for cat in new_categories:
        if cat in categorized:
            events_in_cat = categorized[cat]
            hours = sum(e.get_duration_hours() for e in events_in_cat)
            print(f"\n{cat.upper().replace('_', ' ')}:")
            print(f"  Count: {len(events_in_cat)} events")
            print(f"  Hours: {hours:.1f}")
            print(f"  Samples:")
            for e in events_in_cat[:5]:
                print(f"    - {e.summary[:70]}")
    
    # Export detailed uncategorized list
    output = []
    for event in uncategorized:
        output.append({
            'summary': event.summary,
            'date': event.get_date(),
            'duration_hours': event.get_duration_hours(),
            'busy_status': event.busy_status,
            'transp': event.transp,
            'organizer': event.organizer_name or event.organizer,
            'attendee_count': len(event.attendees),
            'description_preview': event.description[:200]
        })
    
    with open('FY26/analysis_outputs/uncategorized_events_detailed.json', 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2)
    
    print(f"\n[OK] Detailed uncategorized events exported to: FY26/analysis_outputs/uncategorized_events_detailed.json")
    
    # Return updated categorization
    return categorized


def main():
    """Main execution."""
    calendar_file = "FY26/inputs/Daniel Moreira Calendar.ics"
    
    print(f"Parsing calendar file: {calendar_file}")
    events = parse_ics_file(calendar_file)
    print(f"[OK] Parsed {len(events)} events\n")
    
    categorized = analyze_uncategorized(events)
    
    # Summary of all categories
    print("\n" + "=" * 100)
    print("COMPLETE CATEGORIZATION SUMMARY")
    print("=" * 100)
    
    total_events = len(events)
    
    # Sort by count
    sorted_cats = sorted(categorized.items(), key=lambda x: len(x[1]), reverse=True)
    
    print(f"\n{'Category':<40} {'Count':<10} {'Hours':<10} {'% Events':<10}")
    print("-" * 100)
    
    for cat, cat_events in sorted_cats:
        count = len(cat_events)
        hours = sum(e.get_duration_hours() for e in cat_events)
        pct = (count / total_events * 100) if total_events > 0 else 0
        
        print(f"{cat[:39]:<40} {count:<10} {hours:<10.1f} {pct:<10.1f}%")


if __name__ == "__main__":
    main()

