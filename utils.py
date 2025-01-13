from datetime import datetime, timedelta
import re

def parse_relative_date(text):
    """Extract relative date (e.g., '3w ago', '1mo ago', '52m ago') and convert it to an absolute date."""
    now = datetime.now()
    match = re.search(r"(\d+)\s*(d|w|mo|y|m) ago", text)  # Adjusted regex to handle 'mo' and 'm' for minutes
    if match:
        quantity = int(match.group(1))
        unit = match.group(2)
        if unit == "d":  # Days
            return (now - timedelta(days=quantity)).strftime("%d/%m/%Y")
        elif unit == "w":  # Weeks
            return (now - timedelta(weeks=quantity)).strftime("%d/%m/%Y")
        elif unit == "mo":  # Months
            return (now - timedelta(days=30 * quantity)).strftime("%d/%m/%Y")
        elif unit == "y":  # Years
            return (now - timedelta(days=365 * quantity)).strftime("%d/%m/%Y")
        elif unit == "m" and quantity < 60:  # Minutes
            return now.strftime("%d/%m/%Y")
    return "N/A"
