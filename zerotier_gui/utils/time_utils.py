from datetime import datetime, timezone

def format_timestamp(timestamp):
    """Convert Unix timestamp (in milliseconds) to human readable format."""
    try:
        # Convert milliseconds to seconds if needed
        if timestamp and len(str(timestamp)) > 10:
            timestamp = timestamp / 1000
        dt = datetime.fromtimestamp(timestamp)
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except (ValueError, TypeError):
        return "Unknown"

def get_current_timestamp():
    """Get current timestamp in seconds."""
    return datetime.now().timestamp()

def format_duration(seconds):
    """Format a duration in seconds to a human-readable string."""
    if not seconds:
        return "Unknown"
        
    try:
        seconds = int(seconds)
        days, remainder = divmod(seconds, 86400)
        hours, remainder = divmod(remainder, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        parts = []
        if days > 0:
            parts.append(f"{days}d")
        if hours > 0 or days > 0:
            parts.append(f"{hours}h")
        if minutes > 0 or hours > 0 or days > 0:
            parts.append(f"{minutes}m")
        parts.append(f"{seconds}s")
        
        return " ".join(parts)
    except (ValueError, TypeError):
        return "Unknown" 