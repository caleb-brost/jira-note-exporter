from datetime import datetime

def format_jira_time(timestamp: str) -> str:
    """
    Converts a Jira timestamp string to 'YYYY-MM-DD HH:MM' format.
    
    Example input: '2025-07-22T17:28:12.925-0600'
    """
    dt = datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S.%f%z")
    return dt.strftime("%Y-%m-%d %H:%M")

def jira_seconds_to_hours(seconds):
    """Convert Jira time in seconds to hours as a decimal rounded to 2 places."""
    if seconds is None:
        return 0.0
    hours = seconds / 3600
    return f"{(round(hours, 2))}h"
