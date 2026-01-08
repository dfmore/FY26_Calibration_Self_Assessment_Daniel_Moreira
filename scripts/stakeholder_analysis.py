#!/usr/bin/env python3
"""
Stakeholder & Time Analysis Script
Extracts engagement patterns, stakeholder relationships, and time analytics from calendar.
"""

import re
from datetime import datetime
from collections import defaultdict, Counter
from typing import Dict, List, Set, Tuple
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
        self.organizer_name = ""
        self.attendees = []
        self.categories = []
        self.status = ""
        self.busy_status = ""
        self.transp = ""
        self.created = ""
        self.uid = ""
        self.is_recurring = False
        self.recurrence_id = ""
        
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
    
    def get_month(self) -> str:
        """Extract month from event."""
        date = self.get_date()
        if date:
            return date[:7]  # YYYY-MM
        return ""
    
    def get_time_of_day(self) -> str:
        """Categorize event by time of day."""
        try:
            start_str = self.dtstart.split('TZID=')[-1] if 'TZID=' in self.dtstart else self.dtstart
            time_match = re.search(r'T(\d{2})\d{4}', start_str)
            if time_match:
                hour = int(time_match.group(1))
                if 0 <= hour < 6:
                    return "Night (00:00-06:00)"
                elif 6 <= hour < 9:
                    return "Early Morning (06:00-09:00)"
                elif 9 <= hour < 12:
                    return "Morning (09:00-12:00)"
                elif 12 <= hour < 14:
                    return "Lunch (12:00-14:00)"
                elif 14 <= hour < 17:
                    return "Afternoon (14:00-17:00)"
                elif 17 <= hour < 20:
                    return "Evening (17:00-20:00)"
                else:
                    return "Night (20:00-24:00)"
        except Exception:
            pass
        return "Unknown"
    
    def get_day_of_week(self) -> str:
        """Get day of week."""
        try:
            date = self.get_date()
            if date:
                dt = datetime.strptime(date, '%Y-%m-%d')
                return dt.strftime('%A')
        except Exception:
            pass
        return "Unknown"


def parse_ics_file(filepath: str) -> List[CalendarEvent]:
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
                'name': name_match.group(1) if name_match else email_match.group(1).split('@')[0],
                'status': partstat_match.group(1) if partstat_match else 'UNKNOWN'
            }
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


def is_work_relevant(event: CalendarEvent) -> bool:
    """Determine if event is work-relevant."""
    summary_lower = event.summary.lower()
    
    # Exclude non-meetings (no attendees) - personal tasks/reminders
    if len(event.attendees) == 0:
        return False
    
    # Exclude declined/tentative
    if event.status in ["DECLINED", "TENTATIVE"]:
        return False
    
    # Exclude OOO
    if event.busy_status == "OOF":
        return False
    
    # Exclude personal time
    if any(keyword in summary_lower for keyword in [
        "out of office", "ooo", "pto", "vacation", "holiday", 
        "personal", "dentist", "doctor"
    ]):
        return False
    
    # Exclude Focus Fridays
    if "focus friday" in summary_lower or "focus fridays" in summary_lower:
        return False
    
    # Exclude breaks (but keep customer dinners)
    if any(keyword in summary_lower for keyword in ["lunch", "breakfast", "gym", "workout"]):
        if not any(keyword in summary_lower for keyword in ["customer", "client", "meeting"]):
            return False
    
    # Exclude transparent/free time
    if event.transp == "TRANSPARENT" or event.busy_status == "FREE":
        return False
    
    return True


def extract_company_from_email(email: str) -> str:
    """Extract company/organization from email domain."""
    if not email or '@' not in email:
        return "Unknown"
    
    domain = email.split('@')[1].lower()
    
    # Map common domains to organizations
    if 'autodesk' in domain:
        return "Autodesk (Internal)"
    elif domain in ['gmail.com', 'outlook.com', 'hotmail.com', 'yahoo.com']:
        return "Personal Email"
    else:
        # Extract company name from domain
        company = domain.split('.')[0]
        return company.title()


def categorize_meeting_type(event: CalendarEvent) -> str:
    """Categorize meeting type for analytics."""
    summary_lower = event.summary.lower()
    desc_lower = event.description.lower()
    
    # 1:1s and syncs
    if any(keyword in summary_lower for keyword in [
        "1:1", "one on one", "1-1", "sync", "catch up", "check in"
    ]):
        return "1:1 & Syncs"
    
    # Customer/External
    if any(keyword in summary_lower or keyword in desc_lower for keyword in [
        "customer", "client", "external", "demo", "presentation"
    ]):
        return "Customer/External"
    
    # Team meetings
    if any(keyword in summary_lower for keyword in [
        "team meeting", "standup", "stand-up", "all hands", "town hall"
    ]):
        return "Team Meetings"
    
    # Training
    if any(keyword in summary_lower for keyword in [
        "training", "workshop", "learning", "course", "webinar"
    ]):
        return "Training/Learning"
    
    # Planning
    if any(keyword in summary_lower for keyword in [
        "planning", "roadmap", "strategy", "review", "retrospective", "sprint"
    ]):
        return "Planning/Strategy"
    
    # Focus time
    if any(keyword in summary_lower for keyword in [
        "focus", "blocked", "do not book", "heads down"
    ]):
        return "Focus Time"
    
    return "General Meetings"


def analyze_stakeholders(events: List[CalendarEvent]) -> Dict:
    """Analyze stakeholder engagement patterns."""
    
    # Filter work-relevant events
    work_events = [e for e in events if is_work_relevant(e)]
    
    # Track stakeholder interactions
    stakeholder_meetings = defaultdict(lambda: {
        'count': 0,
        'hours': 0.0,
        'as_organizer': 0,
        'as_attendee': 0,
        'companies': set(),
        'meeting_types': defaultdict(int),
        'months_active': set()
    })
    
    # Track organizers
    organizer_stats = defaultdict(lambda: {
        'count': 0,
        'hours': 0.0,
        'company': '',
        'months_active': set()
    })
    
    for event in work_events:
        duration = event.get_duration_hours()
        month = event.get_month()
        meeting_type = categorize_meeting_type(event)
        
        # Track organizer
        if event.organizer and event.organizer != 'daniel.moreira@autodesk.com':
            org_key = event.organizer_name if event.organizer_name else event.organizer
            organizer_stats[org_key]['count'] += 1
            organizer_stats[org_key]['hours'] += duration
            organizer_stats[org_key]['company'] = extract_company_from_email(event.organizer)
            if month:
                organizer_stats[org_key]['months_active'].add(month)
        
        # Track all attendees
        for attendee in event.attendees:
            email = attendee['email']
            name = attendee['name']
            
            # Skip self
            if 'daniel.moreira' in email.lower():
                continue
            
            key = name if name else email
            company = extract_company_from_email(email)
            
            stakeholder_meetings[key]['count'] += 1
            stakeholder_meetings[key]['hours'] += duration
            stakeholder_meetings[key]['companies'].add(company)
            stakeholder_meetings[key]['meeting_types'][meeting_type] += 1
            
            if month:
                stakeholder_meetings[key]['months_active'].add(month)
            
            # Track if organized by me
            if event.organizer == 'daniel.moreira@autodesk.com':
                stakeholder_meetings[key]['as_organizer'] += 1
            else:
                stakeholder_meetings[key]['as_attendee'] += 1
    
    return {
        'stakeholders': stakeholder_meetings,
        'organizers': organizer_stats,
        'work_events': work_events
    }


def analyze_time_patterns(events: List[CalendarEvent]) -> Dict:
    """Analyze time usage patterns."""
    
    work_events = [e for e in events if is_work_relevant(e)]
    
    stats = {
        'by_month': defaultdict(lambda: {'count': 0, 'hours': 0.0}),
        'by_day_of_week': defaultdict(lambda: {'count': 0, 'hours': 0.0}),
        'by_time_of_day': defaultdict(lambda: {'count': 0, 'hours': 0.0}),
        'by_meeting_type': defaultdict(lambda: {'count': 0, 'hours': 0.0}),
        'by_company': defaultdict(lambda: {'count': 0, 'hours': 0.0}),
        'by_location': defaultdict(lambda: {'count': 0, 'hours': 0.0}),
        'meeting_size_distribution': defaultdict(int),
        'recurring_vs_adhoc': {'recurring': 0, 'adhoc': 0, 'recurring_hours': 0.0, 'adhoc_hours': 0.0}
    }
    
    for event in work_events:
        duration = event.get_duration_hours()
        month = event.get_month()
        day = event.get_day_of_week()
        time_slot = event.get_time_of_day()
        meeting_type = categorize_meeting_type(event)
        
        # By month
        if month:
            stats['by_month'][month]['count'] += 1
            stats['by_month'][month]['hours'] += duration
        
        # By day of week
        stats['by_day_of_week'][day]['count'] += 1
        stats['by_day_of_week'][day]['hours'] += duration
        
        # By time of day
        stats['by_time_of_day'][time_slot]['count'] += 1
        stats['by_time_of_day'][time_slot]['hours'] += duration
        
        # By meeting type
        stats['by_meeting_type'][meeting_type]['count'] += 1
        stats['by_meeting_type'][meeting_type]['hours'] += duration
        
        # By company (from attendees)
        companies = set()
        for attendee in event.attendees:
            company = extract_company_from_email(attendee['email'])
            companies.add(company)
        
        for company in companies:
            stats['by_company'][company]['count'] += 1
            stats['by_company'][company]['hours'] += duration / len(companies)  # Split time
        
        # By location
        location = event.location if event.location else "No Location"
        if "teams.microsoft.com" in location.lower() or "zoom" in location.lower():
            location = "Virtual (Teams/Zoom)"
        elif location and location != "No Location":
            location = "Physical Location"
        
        stats['by_location'][location]['count'] += 1
        stats['by_location'][location]['hours'] += duration
        
        # Meeting size
        attendee_count = len(event.attendees)
        if attendee_count <= 2:
            size = "1:1 (2 people)"
        elif attendee_count <= 5:
            size = "Small (3-5 people)"
        elif attendee_count <= 10:
            size = "Medium (6-10 people)"
        elif attendee_count <= 20:
            size = "Large (11-20 people)"
        else:
            size = "Very Large (20+ people)"
        
        stats['meeting_size_distribution'][size] += 1
        
        # Recurring vs ad-hoc
        if event.is_recurring:
            stats['recurring_vs_adhoc']['recurring'] += 1
            stats['recurring_vs_adhoc']['recurring_hours'] += duration
        else:
            stats['recurring_vs_adhoc']['adhoc'] += 1
            stats['recurring_vs_adhoc']['adhoc_hours'] += duration
    
    return stats


def print_stakeholder_report(stakeholder_data: Dict, time_stats: Dict):
    """Print comprehensive stakeholder and time analysis report."""
    
    stakeholders = stakeholder_data['stakeholders']
    organizers = stakeholder_data['organizers']
    
    print("=" * 100)
    print("STAKEHOLDER ENGAGEMENT ANALYSIS")
    print("=" * 100)
    
    # Top stakeholders by meeting count
    print("\n" + "-" * 100)
    print("TOP 30 STAKEHOLDERS BY MEETING COUNT")
    print("-" * 100)
    print(f"{'Rank':<6} {'Name':<35} {'Meetings':<10} {'Hours':<10} {'Company':<25}")
    print("-" * 100)
    
    sorted_stakeholders = sorted(
        stakeholders.items(),
        key=lambda x: x[1]['count'],
        reverse=True
    )[:30]
    
    for i, (name, data) in enumerate(sorted_stakeholders, 1):
        companies = ', '.join(list(data['companies'])[:2])
        if len(data['companies']) > 2:
            companies += f" +{len(data['companies'])-2}"
        print(f"{i:<6} {name[:34]:<35} {data['count']:<10} {data['hours']:<10.1f} {companies[:24]:<25}")
    
    # Top stakeholders by time spent
    print("\n" + "-" * 100)
    print("TOP 30 STAKEHOLDERS BY TIME SPENT (HOURS)")
    print("-" * 100)
    print(f"{'Rank':<6} {'Name':<35} {'Hours':<10} {'Meetings':<10} {'Months Active':<15}")
    print("-" * 100)
    
    sorted_by_time = sorted(
        stakeholders.items(),
        key=lambda x: x[1]['hours'],
        reverse=True
    )[:30]
    
    for i, (name, data) in enumerate(sorted_by_time, 1):
        months_count = len(data['months_active'])
        print(f"{i:<6} {name[:34]:<35} {data['hours']:<10.1f} {data['count']:<10} {months_count:<15}")
    
    # External vs Internal breakdown
    print("\n" + "-" * 100)
    print("INTERNAL VS EXTERNAL STAKEHOLDERS")
    print("-" * 100)
    
    internal_count = sum(1 for s in stakeholders.values() if 'Autodesk (Internal)' in s['companies'])
    external_count = len(stakeholders) - internal_count
    
    internal_hours = sum(s['hours'] for s in stakeholders.values() if 'Autodesk (Internal)' in s['companies'])
    external_hours = sum(s['hours'] for s in stakeholders.values() if 'Autodesk (Internal)' not in s['companies'])
    
    print(f"Internal Stakeholders: {internal_count} ({internal_hours:.1f} hours)")
    print(f"External Stakeholders: {external_count} ({external_hours:.1f} hours)")
    
    # Top external organizations
    print("\n" + "-" * 100)
    print("TOP EXTERNAL ORGANIZATIONS")
    print("-" * 100)
    
    org_stats = defaultdict(lambda: {'count': 0, 'hours': 0.0, 'people': set()})
    for name, data in stakeholders.items():
        for company in data['companies']:
            if company != 'Autodesk (Internal)':
                org_stats[company]['count'] += data['count']
                org_stats[company]['hours'] += data['hours']
                org_stats[company]['people'].add(name)
    
    sorted_orgs = sorted(org_stats.items(), key=lambda x: x[1]['hours'], reverse=True)[:20]
    
    print(f"{'Rank':<6} {'Organization':<30} {'Meetings':<10} {'Hours':<10} {'People':<10}")
    print("-" * 100)
    for i, (org, data) in enumerate(sorted_orgs, 1):
        print(f"{i:<6} {org[:29]:<30} {data['count']:<10} {data['hours']:<10.1f} {len(data['people']):<10}")
    
    # Meeting organizers
    print("\n" + "-" * 100)
    print("TOP 20 MEETING ORGANIZERS (Who schedules meetings with you)")
    print("-" * 100)
    print(f"{'Rank':<6} {'Name':<35} {'Meetings':<10} {'Hours':<10} {'Company':<25}")
    print("-" * 100)
    
    sorted_organizers = sorted(
        organizers.items(),
        key=lambda x: x[1]['count'],
        reverse=True
    )[:20]
    
    for i, (name, data) in enumerate(sorted_organizers, 1):
        print(f"{i:<6} {name[:34]:<35} {data['count']:<10} {data['hours']:<10.1f} {data['company'][:24]:<25}")
    
    print("\n" + "=" * 100)
    print("TIME USAGE ANALYSIS")
    print("=" * 100)
    
    # By month
    print("\n" + "-" * 100)
    print("TIME DISTRIBUTION BY MONTH")
    print("-" * 100)
    print(f"{'Month':<15} {'Meetings':<12} {'Hours':<12} {'Avg/Meeting':<15}")
    print("-" * 100)
    
    for month in sorted(time_stats['by_month'].keys()):
        data = time_stats['by_month'][month]
        avg = data['hours'] / data['count'] if data['count'] > 0 else 0
        print(f"{month:<15} {data['count']:<12} {data['hours']:<12.1f} {avg:<15.2f}")
    
    # By day of week
    print("\n" + "-" * 100)
    print("TIME DISTRIBUTION BY DAY OF WEEK")
    print("-" * 100)
    print(f"{'Day':<15} {'Meetings':<12} {'Hours':<12} {'Avg/Day':<15}")
    print("-" * 100)
    
    day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    for day in day_order:
        if day in time_stats['by_day_of_week']:
            data = time_stats['by_day_of_week'][day]
            avg = data['hours'] / data['count'] if data['count'] > 0 else 0
            print(f"{day:<15} {data['count']:<12} {data['hours']:<12.1f} {avg:<15.2f}")
    
    # By time of day
    print("\n" + "-" * 100)
    print("TIME DISTRIBUTION BY TIME OF DAY")
    print("-" * 100)
    print(f"{'Time Slot':<30} {'Meetings':<12} {'Hours':<12} {'% of Total':<15}")
    print("-" * 100)
    
    total_hours = sum(d['hours'] for d in time_stats['by_time_of_day'].values())
    for time_slot in sorted(time_stats['by_time_of_day'].keys()):
        data = time_stats['by_time_of_day'][time_slot]
        pct = (data['hours'] / total_hours * 100) if total_hours > 0 else 0
        print(f"{time_slot:<30} {data['count']:<12} {data['hours']:<12.1f} {pct:<15.1f}%")
    
    # By meeting type
    print("\n" + "-" * 100)
    print("TIME DISTRIBUTION BY MEETING TYPE")
    print("-" * 100)
    print(f"{'Meeting Type':<30} {'Meetings':<12} {'Hours':<12} {'% of Total':<15}")
    print("-" * 100)
    
    sorted_types = sorted(
        time_stats['by_meeting_type'].items(),
        key=lambda x: x[1]['hours'],
        reverse=True
    )
    
    for meeting_type, data in sorted_types:
        pct = (data['hours'] / total_hours * 100) if total_hours > 0 else 0
        print(f"{meeting_type:<30} {data['count']:<12} {data['hours']:<12.1f} {pct:<15.1f}%")
    
    # Meeting size distribution
    print("\n" + "-" * 100)
    print("MEETING SIZE DISTRIBUTION")
    print("-" * 100)
    print(f"{'Size Category':<30} {'Count':<12}")
    print("-" * 100)
    
    size_order = [
        "1:1 (2 people)",
        "Small (3-5 people)",
        "Medium (6-10 people)",
        "Large (11-20 people)",
        "Very Large (20+ people)"
    ]
    
    for size in size_order:
        if size in time_stats['meeting_size_distribution']:
            count = time_stats['meeting_size_distribution'][size]
            print(f"{size:<30} {count:<12}")
    
    # Virtual vs Physical
    print("\n" + "-" * 100)
    print("MEETING LOCATION (Virtual vs Physical)")
    print("-" * 100)
    print(f"{'Location Type':<30} {'Meetings':<12} {'Hours':<12} {'% of Total':<15}")
    print("-" * 100)
    
    for location, data in sorted(time_stats['by_location'].items(), key=lambda x: x[1]['hours'], reverse=True):
        pct = (data['hours'] / total_hours * 100) if total_hours > 0 else 0
        print(f"{location:<30} {data['count']:<12} {data['hours']:<12.1f} {pct:<15.1f}%")
    
    # Recurring vs Ad-hoc
    print("\n" + "-" * 100)
    print("RECURRING VS AD-HOC MEETINGS")
    print("-" * 100)
    
    rec_data = time_stats['recurring_vs_adhoc']
    total_meetings = rec_data['recurring'] + rec_data['adhoc']
    
    print(f"Recurring Meetings: {rec_data['recurring']} ({rec_data['recurring']/total_meetings*100:.1f}%) - {rec_data['recurring_hours']:.1f} hours")
    print(f"Ad-hoc Meetings: {rec_data['adhoc']} ({rec_data['adhoc']/total_meetings*100:.1f}%) - {rec_data['adhoc_hours']:.1f} hours")
    
    print("\n" + "=" * 100)


def export_detailed_analysis(stakeholder_data: Dict, time_stats: Dict, output_file: str):
    """Export detailed analysis to JSON."""
    
    # Convert sets to lists for JSON serialization
    stakeholders_export = {}
    for name, data in stakeholder_data['stakeholders'].items():
        stakeholders_export[name] = {
            'count': data['count'],
            'hours': round(data['hours'], 2),
            'as_organizer': data['as_organizer'],
            'as_attendee': data['as_attendee'],
            'companies': list(data['companies']),
            'meeting_types': dict(data['meeting_types']),
            'months_active': sorted(list(data['months_active']))
        }
    
    organizers_export = {}
    for name, data in stakeholder_data['organizers'].items():
        organizers_export[name] = {
            'count': data['count'],
            'hours': round(data['hours'], 2),
            'company': data['company'],
            'months_active': sorted(list(data['months_active']))
        }
    
    output = {
        'stakeholders': stakeholders_export,
        'organizers': organizers_export,
        'time_stats': {
            'by_month': dict(time_stats['by_month']),
            'by_day_of_week': dict(time_stats['by_day_of_week']),
            'by_time_of_day': dict(time_stats['by_time_of_day']),
            'by_meeting_type': dict(time_stats['by_meeting_type']),
            'by_company': dict(time_stats['by_company']),
            'by_location': dict(time_stats['by_location']),
            'meeting_size_distribution': dict(time_stats['meeting_size_distribution']),
            'recurring_vs_adhoc': time_stats['recurring_vs_adhoc']
        }
    }
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, default=str)
    
    print(f"\n[OK] Detailed stakeholder analysis exported to: {output_file}")


def main():
    """Main execution function."""
    calendar_file = "FY26/inputs/Daniel Moreira Calendar.ics"
    output_json = "FY26/analysis_outputs/stakeholder_analysis.json"
    
    print(f"Parsing calendar file: {calendar_file}")
    events = parse_ics_file(calendar_file)
    print(f"[OK] Parsed {len(events)} events")
    
    print("\nAnalyzing stakeholder engagement patterns...")
    stakeholder_data = analyze_stakeholders(events)
    
    print("Analyzing time usage patterns...")
    time_stats = analyze_time_patterns(events)
    
    print("\nGenerating reports...\n")
    print_stakeholder_report(stakeholder_data, time_stats)
    
    export_detailed_analysis(stakeholder_data, time_stats, output_json)


if __name__ == "__main__":
    main()

