import time
from datetime import datetime


def format_time(timestamp: float) -> str:
    return datetime.fromtimestamp(timestamp).strftime("%d.%m.%Y %H:%M")


def format_duration(seconds: int) -> str:
    if seconds < 0:
        return "истёк"
    
    days = seconds // 86400
    hours = (seconds % 86400) // 3600
    minutes = (seconds % 3600) // 60
    
    parts = []
    
    if days > 0:
        if days % 10 == 1 and days % 100 != 11:
            parts.append(f"{days} день")
        elif 2 <= days % 10 <= 4 and not (12 <= days % 100 <= 14):
            parts.append(f"{days} дня")
        else:
            parts.append(f"{days} дней")
    
    if hours > 0:
        if hours % 10 == 1 and hours % 100 != 11:
            parts.append(f"{hours} час")
        elif 2 <= hours % 10 <= 4 and not (12 <= hours % 100 <= 14):
            parts.append(f"{hours} часа")
        else:
            parts.append(f"{hours} часов")
    
    if minutes > 0:
        if minutes % 10 == 1 and minutes % 100 != 11:
            parts.append(f"{minutes} минута")
        elif 2 <= minutes % 10 <= 4 and not (12 <= minutes % 100 <= 14):
            parts.append(f"{minutes} минуты")
        else:
            parts.append(f"{minutes} минут")
    
    if not parts:
        return "менее минуты"
    
    return " ".join(parts)


def parse_duration(duration_str: str) -> int | None:
    if not duration_str:
        return None
    
    duration_str = duration_str.lower().strip()
    
    if duration_str.isdigit():
        return int(duration_str) * 60
    
    multipliers = {
        'm': 60, 'min': 60, 'м': 60, 'мин': 60,
        'h': 3600, 'hour': 3600, 'ч': 3600, 'час': 3600,
        'd': 86400, 'day': 86400, 'д': 86400, 'дн': 86400,
    }
    
    import re
    match = re.match(r'^(\d+)\s*([a-zа-я]+)$', duration_str)
    
    if match:
        value = int(match.group(1))
        suffix = match.group(2)
        
        if suffix in multipliers:
            return value * multipliers[suffix]
    
    return None


def get_remaining_time(unmute_time: float) -> str:
    remaining = int(unmute_time - time.time())
    if remaining <= 0:
        return "истёк"
    return format_duration(remaining)
