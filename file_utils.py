import os
from typing import Optional, Tuple

def format_size(size_bytes: int) -> str:
    """Convert bytes to human readable format."""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.2f} PB"

def delete_file(file_path: str) -> Tuple[bool, Optional[str]]:
    """Safely delete a file and return success status and error message if any."""
    try:
        os.remove(file_path)
        return True, None
    except OSError as e:
        return False, str(e)

def get_file_type_icon(file_type: str) -> str:
    """Get an emoji icon for the file type."""
    ICONS = {
        '.txt': '📄',
        '.pdf': '📕',
        '.doc': '📗',
        '.docx': '📗',
        '.xls': '📊',
        '.xlsx': '📊',
        '.jpg': '🖼',
        '.jpeg': '🖼',
        '.png': '🖼',
        '.mp3': '🎵',
        '.mp4': '🎥',
        '.zip': '📦',
        '.exe': '⚙️',
    }
    return ICONS.get(file_type.lower(), '📄')