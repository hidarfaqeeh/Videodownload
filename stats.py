"""
Bot Statistics Module
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any
import logging

logger = logging.getLogger(__name__)

class BotStats:
    def __init__(self, stats_file: str = "bot_stats.json"):
        self.stats_file = stats_file
        self.stats = self.load_stats()
    
    def load_stats(self) -> Dict:
        """Load statistics from file"""
        try:
            if os.path.exists(self.stats_file):
                with open(self.stats_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                return self.create_default_stats()
        except Exception as e:
            logger.error(f"Error loading stats: {e}")
            return self.create_default_stats()
    
    def create_default_stats(self) -> Dict:
        """Create default statistics structure"""
        return {
            "total_downloads": 0,
            "total_users": 0,
            "downloads_by_platform": {
                "youtube": 0,
                "tiktok": 0,
                "instagram": 0,
                "facebook": 0,
                "twitter": 0,
                "snapchat": 0
            },
            "downloads_by_type": {
                "video": 0,
                "audio": 0
            },
            "daily_stats": {},
            "users": {},
            "playlists_downloaded": 0,
            "total_files_size": 0,
            "peak_daily_downloads": 0,
            "created_date": datetime.now().isoformat()
        }
    
    def save_stats(self):
        """Save statistics to file"""
        try:
            with open(self.stats_file, 'w', encoding='utf-8') as f:
                json.dump(self.stats, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Error saving stats: {e}")
    
    def track_download(self, user_id: str, platform: str, file_type: str, file_size: int = 0):
        """Track a download"""
        today = datetime.now().strftime("%Y-%m-%d")
        
        # Update total stats
        self.stats["total_downloads"] += 1
        
        # Track platform
        platform_lower = platform.lower()
        if platform_lower in self.stats["downloads_by_platform"]:
            self.stats["downloads_by_platform"][platform_lower] += 1
        
        # Track file type
        if file_type in self.stats["downloads_by_type"]:
            self.stats["downloads_by_type"][file_type] += 1
        
        # Track daily stats
        if today not in self.stats["daily_stats"]:
            self.stats["daily_stats"][today] = 0
        self.stats["daily_stats"][today] += 1
        
        # Update peak daily downloads
        if self.stats["daily_stats"][today] > self.stats["peak_daily_downloads"]:
            self.stats["peak_daily_downloads"] = self.stats["daily_stats"][today]
        
        # Track user
        if user_id not in self.stats["users"]:
            self.stats["users"][user_id] = {
                "downloads": 0,
                "first_use": datetime.now().isoformat(),
                "last_use": datetime.now().isoformat()
            }
            self.stats["total_users"] += 1
        
        self.stats["users"][user_id]["downloads"] += 1
        self.stats["users"][user_id]["last_use"] = datetime.now().isoformat()
        
        # Track file size
        if file_size > 0:
            self.stats["total_files_size"] += file_size
        
        self.save_stats()
    
    def track_playlist_download(self, user_id: str, videos_count: int):
        """Track playlist download"""
        self.stats["playlists_downloaded"] += 1
        self.track_download(user_id, "youtube", "playlist")
        self.save_stats()
    
    def get_user_stats(self, user_id: str) -> Dict:
        """Get statistics for a specific user"""
        user_data = self.stats["users"].get(user_id, {})
        if not user_data:
            return {"downloads": 0, "rank": "جديد"}
        
        # Calculate user rank
        user_downloads = user_data.get("downloads", 0)
        all_downloads = [u.get("downloads", 0) for u in self.stats["users"].values()]
        all_downloads.sort(reverse=True)
        
        if user_downloads in all_downloads:
            rank = all_downloads.index(user_downloads) + 1
        else:
            rank = len(all_downloads) + 1
        
        return {
            "downloads": user_downloads,
            "rank": rank,
            "first_use": user_data.get("first_use"),
            "last_use": user_data.get("last_use")
        }
    
    def get_global_stats(self) -> Dict:
        """Get global statistics"""
        # Calculate recent activity (last 7 days)
        today = datetime.now()
        last_week_downloads = 0
        
        for i in range(7):
            date = (today - timedelta(days=i)).strftime("%Y-%m-%d")
            last_week_downloads += self.stats["daily_stats"].get(date, 0)
        
        # Get most popular platform
        platform_stats = self.stats["downloads_by_platform"]
        most_popular_platform = max(platform_stats.items(), key=lambda x: x[1])
        
        # Format total file size
        total_size_gb = self.stats["total_files_size"] / (1024**3)
        
        return {
            "total_downloads": self.stats["total_downloads"],
            "total_users": self.stats["total_users"],
            "last_week_downloads": last_week_downloads,
            "most_popular_platform": most_popular_platform,
            "total_size_gb": round(total_size_gb, 2),
            "peak_daily_downloads": self.stats["peak_daily_downloads"],
            "playlists_downloaded": self.stats["playlists_downloaded"],
            "platform_breakdown": platform_stats,
            "type_breakdown": self.stats["downloads_by_type"]
        }
    
    def get_top_users(self, limit: int = 10) -> List[Dict]:
        """Get top users by downloads"""
        users_list = []
        for user_id, data in self.stats["users"].items():
            users_list.append({
                "user_id": user_id,
                "downloads": data.get("downloads", 0),
                "first_use": data.get("first_use"),
                "last_use": data.get("last_use")
            })
        
        users_list.sort(key=lambda x: x["downloads"], reverse=True)
        return users_list[:limit]
    
    def cleanup_old_daily_stats(self, days_to_keep: int = 30):
        """Clean up old daily statistics"""
        cutoff_date = datetime.now() - timedelta(days=days_to_keep)
        cutoff_str = cutoff_date.strftime("%Y-%m-%d")
        
        keys_to_remove = []
        for date_str in self.stats["daily_stats"]:
            if date_str < cutoff_str:
                keys_to_remove.append(date_str)
        
        for key in keys_to_remove:
            del self.stats["daily_stats"][key]
        
        self.save_stats()