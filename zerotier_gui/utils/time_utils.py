from datetime import datetime

def format_timestamp(timestamp):
    """Convert Unix timestamp (in milliseconds) to human readable format."""
    try:
        # Convert milliseconds to seconds if needed
        if len(str(timestamp)) > 10:
            timestamp = timestamp / 1000
        dt = datetime.fromtimestamp(timestamp)
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except (ValueError, TypeError):
        return "Unknown" 