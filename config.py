"""
Configuration settings for the Telegram Video Downloader Bot
"""

import os
from typing import List

# Bot Configuration
BOT_TOKEN = os.getenv("BOT_TOKEN", "7673414255:AAHwEGTXQG4ESNaNjM6H27ZJK5M8hnUMgfY")

# Pyrogram (for large uploads)
USE_PYROGRAM_UPLOAD = os.getenv("USE_PYROGRAM_UPLOAD", "false").lower() == "true"
PYROGRAM_API_ID = os.getenv("PYROGRAM_API_ID")
PYROGRAM_API_HASH = os.getenv("PYROGRAM_API_HASH")
PYROGRAM_WORKERS = int(os.getenv("PYROGRAM_WORKERS", "8"))

# File Size Limits (in bytes)
# If using Pyrogram uploads, allow up to ~1.9GB by default; otherwise default to 50MB
DEFAULT_MAX_MB = 1900 if USE_PYROGRAM_UPLOAD else 50
MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE_MB", str(DEFAULT_MAX_MB))) * 1024 * 1024

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
# yt-dlp concurrency tuning
YTDLP_CONCURRENT_FRAGMENTS = int(os.getenv("YTDLP_CONCURRENT_FRAGMENTS", "4"))
YTDLP_BUFFERSIZE = int(os.getenv("YTDLP_BUFFERSIZE", "1048576"))  # 1 MiB
YTDLP_HTTP_CHUNK_SIZE = os.getenv("YTDLP_HTTP_CHUNK_SIZE")  # e.g. "10M" or empty


# Cookies / Authentication Configuration
# Enable cookie-based authentication fallback across all platforms
COOKIES_ENABLED = os.getenv("COOKIES_ENABLED", "false").lower() == "true"

# Provide cookies via one of the following (priority: file path > base64 > raw header)
# 1) COOKIES_FILE_PATH: absolute path to a Netscape cookies.txt file
COOKIES_FILE_PATH = os.getenv("COOKIES_FILE_PATH")
# 2) COOKIES_B64: base64-encoded Netscape cookies.txt content; will be written to a temp file
COOKIES_B64 = os.getenv("COOKIES_B64")
# 3) COOKIES_RAW: raw Cookie header string, e.g. "name=value; name2=value2"
COOKIES_RAW = os.getenv("COOKIES_RAW")

# Apply cookies only if the first attempt fails (recommended). If false, always use cookies.
COOKIES_APPLY_ON_FAILURE_ONLY = os.getenv("COOKIES_APPLY_ON_FAILURE_ONLY", "true").lower() == "true"

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
