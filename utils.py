"""
Utility functions for the Telegram bot
"""

import os
import re
import shutil
import logging
from urllib.parse import urlparse
from typing import List

logger = logging.getLogger(__name__)

def is_valid_url(url: str) -> bool:
    """Check if the provided string is a valid URL"""
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False

def format_file_size(size_bytes: int) -> str:
    """Format file size in human readable format"""
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.1f} {size_names[i]}"

def sanitize_filename(filename: str) -> str:
    """Sanitize filename for safe file operations"""
    # Remove invalid characters
    filename = re.sub(r'[<>:"/\\|?*]', '', filename)
    # Replace spaces with underscores
    filename = re.sub(r'\s+', '_', filename)
    # Limit length
    if len(filename) > 100:
        name, ext = os.path.splitext(filename)
        filename = name[:100-len(ext)] + ext
    
    return filename

def cleanup_temp_files(temp_dir: str) -> None:
    """Clean up temporary files and directory"""
    try:
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
            logger.info(f"Cleaned up temporary directory: {temp_dir}")
    except Exception as e:
        logger.error(f"Error cleaning up temp directory {temp_dir}: {str(e)}")

def get_video_platforms() -> List[str]:
    """Get list of supported video platforms"""
    return [
        "YouTube",
        "Twitter/X", 
        "Instagram",
        "Facebook",
        "TikTok",
        "Snapchat"
    ]

def extract_urls_from_text(text: str) -> List[str]:
    """Extract URLs from text using regex"""
    url_pattern = re.compile(
        r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
    )
    return url_pattern.findall(text)

def is_supported_platform(url: str) -> bool:
    """Check if URL is from a supported platform"""
    supported_domains = [
        'youtube.com', 'youtu.be', 'm.youtube.com',
        'twitter.com', 'x.com', 'mobile.twitter.com',
        'instagram.com', 'www.instagram.com',
        'facebook.com', 'www.facebook.com', 'fb.watch', 'm.facebook.com',
        'tiktok.com', 'www.tiktok.com', 'm.tiktok.com', 'vm.tiktok.com',
        'snapchat.com', 'www.snapchat.com', 'story.snapchat.com', 'spotlight'
    ]
    
    url_lower = url.lower()
    return any(domain in url_lower for domain in supported_domains)

def format_duration(seconds: int) -> str:
    """Format duration in seconds to human readable format"""
    if seconds < 60:
        return f"{seconds}s"
    elif seconds < 3600:
        minutes = seconds // 60
        remaining_seconds = seconds % 60
        return f"{minutes}m {remaining_seconds}s"
    else:
        hours = seconds // 3600
        remaining_minutes = (seconds % 3600) // 60
        return f"{hours}h {remaining_minutes}m"

def validate_file_extension(filename: str) -> bool:
    """Validate if file has a supported video extension"""
    valid_extensions = ['.mp4', '.webm', '.mkv', '.avi', '.mov', '.flv', '.wmv']
    _, ext = os.path.splitext(filename.lower())
    return ext in valid_extensions
