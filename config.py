"""
Configuration settings for the Telegram Video Downloader Bot
"""

import os
from typing import List

# Bot Configuration
BOT_TOKEN = os.getenv("BOT_TOKEN", "7673414255:AAHwEGTXQG4ESNaNjM6H27ZJK5M8hnUMgfY")

# File Size Limits (in bytes)
MAX_FILE_SIZE = 500 * 1024 * 1024  # 50MB - Telegram's limit for bots

# Supported Platforms
SUPPORTED_PLATFORMS: List[str] = [
    "YouTube",
    "Twitter/X",
    "Instagram", 
    "Facebook",
    "TikTok",
    "Snapchat"
]

# Download Configuration
DOWNLOAD_TIMEOUT = 300  # 5 minutes
MAX_RETRIES = 3

# Logging Configuration
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# Video Quality Settings
PREFERRED_FORMATS = [
    'best[height<=720][ext=mp4]',
    'best[ext=mp4]',
    'best[height<=720]',
    'best'
]

# Temporary Directory Settings
TEMP_DIR_PREFIX = "telegram_video_bot_"
CLEANUP_INTERVAL = 3600  # 1 hour in seconds

# Rate Limiting (if needed in future)
MAX_DOWNLOADS_PER_USER_PER_HOUR = 10
MAX_DOWNLOADS_PER_CHAT_PER_HOUR = 20

# Error Messages
ERROR_MESSAGES = {
    "invalid_url": "❌ Please send a valid video URL.",
    "unsupported_platform": "❌ This platform is not supported.",
    "download_failed": "❌ Download failed. Please try again later.",
    "file_too_large": "❌ Video is too large. Maximum size is 50MB.",
    "video_not_found": "❌ Video not found or is private.",
    "network_error": "❌ Network error. Please try again.",
    "unknown_error": "❌ An unexpected error occurred."
}

# Success Messages
SUCCESS_MESSAGES = {
    "download_started": "🔄 Starting download...",
    "processing": "📋 Processing your request...",
    "uploading": "📤 Uploading video...",
    "completed": "✅ Download completed!"
}
