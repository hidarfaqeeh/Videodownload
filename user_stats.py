"""
User Statistics and Social Features Module
"""
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional

class UserStatsManager:
    def __init__(self, stats_file: str = "user_stats.json"):
        self.stats_file = stats_file
        self.stats = self.load_stats()
    
    def load_stats(self) -> Dict:
        """Load user statistics from file"""
        if os.path.exists(self.stats_file):
            try:
                with open(self.stats_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        return {}
    
    def save_stats(self):
        """Save user statistics to file"""
        try:
            with open(self.stats_file, 'w', encoding='utf-8') as f:
                json.dump(self.stats, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving stats: {e}")
    
    def get_user_stats(self, user_id: str) -> Dict:
        """Get user statistics"""
        if user_id not in self.stats:
            self.stats[user_id] = {
                'total_downloads': 0,
                'video_downloads': 0,
                'audio_downloads': 0,
                'platforms': {},
                'quality_preferences': {},
                'first_use': datetime.now().isoformat(),
                'last_use': datetime.now().isoformat(),
                'favorite_urls': [],
                'achievements': [],
                'points': 0,
                'level': 1,
                'download_history': [],
                'daily_downloads': 0,
                'daily_reset': datetime.now().date().isoformat()
            }
        return self.stats[user_id]
    
    def update_download_stats(self, user_id: str, platform: str, format_type: str, quality: str = "unknown"):
        """Update user download statistics"""
        user_stats = self.get_user_stats(user_id)
        
        # Reset daily downloads if new day
        today = datetime.now().date().isoformat()
        if user_stats['daily_reset'] != today:
            user_stats['daily_downloads'] = 0
            user_stats['daily_reset'] = today
        
        # Update counts
        user_stats['total_downloads'] += 1
        user_stats['daily_downloads'] += 1
        user_stats['last_use'] = datetime.now().isoformat()
        
        if format_type == 'video':
            user_stats['video_downloads'] += 1
        elif format_type == 'audio':
            user_stats['audio_downloads'] += 1
        
        # Update platform stats
        if platform not in user_stats['platforms']:
            user_stats['platforms'][platform] = 0
        user_stats['platforms'][platform] += 1
        
        # Update quality preferences
        if quality not in user_stats['quality_preferences']:
            user_stats['quality_preferences'][quality] = 0
        user_stats['quality_preferences'][quality] += 1
        
        # Add points and check level
        points_earned = self.calculate_points(format_type, quality)
        user_stats['points'] += points_earned
        user_stats['level'] = self.calculate_level(user_stats['points'])
        
        # Check for achievements
        self.check_achievements(user_stats)
        
        # Add to history (keep last 50)
        download_entry = {
            'platform': platform,
            'type': format_type,
            'quality': quality,
            'date': datetime.now().isoformat(),
            'points': points_earned
        }
        user_stats['download_history'].insert(0, download_entry)
        if len(user_stats['download_history']) > 50:
            user_stats['download_history'] = user_stats['download_history'][:50]
        
        self.save_stats()
        return points_earned
    
    def calculate_points(self, format_type: str, quality: str) -> int:
        """Calculate points for download"""
        base_points = 10
        
        # Bonus for high quality
        if '1080' in quality or '4K' in quality:
            base_points += 5
        elif '720' in quality:
            base_points += 3
        
        # Bonus for audio downloads
        if format_type == 'audio':
            base_points += 2
        
        return base_points
    
    def calculate_level(self, points: int) -> int:
        """Calculate user level based on points"""
        return min(50, max(1, points // 100 + 1))
    
    def check_achievements(self, user_stats: Dict):
        """Check and award achievements"""
        achievements = []
        
        # Download milestones
        total = user_stats['total_downloads']
        if total >= 1 and 'first_download' not in user_stats['achievements']:
            achievements.append('first_download')
        if total >= 10 and 'download_veteran' not in user_stats['achievements']:
            achievements.append('download_veteran')
        if total >= 50 and 'download_master' not in user_stats['achievements']:
            achievements.append('download_master')
        if total >= 100 and 'download_legend' not in user_stats['achievements']:
            achievements.append('download_legend')
        
        # Platform diversity
        platforms_used = len(user_stats['platforms'])
        if platforms_used >= 3 and 'platform_explorer' not in user_stats['achievements']:
            achievements.append('platform_explorer')
        if platforms_used >= 5 and 'platform_master' not in user_stats['achievements']:
            achievements.append('platform_master')
        
        # Quality enthusiast
        quality_prefs = user_stats['quality_preferences']
        high_quality_downloads = quality_prefs.get('1080p', 0) + quality_prefs.get('4K', 0)
        if high_quality_downloads >= 10 and 'quality_enthusiast' not in user_stats['achievements']:
            achievements.append('quality_enthusiast')
        
        # Audio lover
        if user_stats['audio_downloads'] >= 20 and 'audio_lover' not in user_stats['achievements']:
            achievements.append('audio_lover')
        
        # Daily user
        if user_stats['daily_downloads'] >= 5 and 'daily_user' not in user_stats['achievements']:
            achievements.append('daily_user')
        
        # Add new achievements
        for achievement in achievements:
            if achievement not in user_stats['achievements']:
                user_stats['achievements'].append(achievement)
                user_stats['points'] += 50  # Bonus points for achievements
    
    def get_user_rank(self, user_id: str) -> Dict:
        """Get user rank compared to others"""
        user_stats = self.get_user_stats(user_id)
        all_users = list(self.stats.values())
        
        # Sort by total downloads
        sorted_users = sorted(all_users, key=lambda x: x['total_downloads'], reverse=True)
        
        user_rank = 1
        for i, stats in enumerate(sorted_users):
            if stats.get('total_downloads', 0) == user_stats['total_downloads']:
                user_rank = i + 1
                break
        
        return {
            'rank': user_rank,
            'total_users': len(all_users),
            'percentile': round((len(all_users) - user_rank + 1) / len(all_users) * 100, 1)
        }
    
    def get_leaderboard(self, top_n: int = 10) -> List[Dict]:
        """Get top users leaderboard"""
        all_users = []
        for user_id, stats in self.stats.items():
            all_users.append({
                'user_id': user_id,
                'downloads': stats.get('total_downloads', 0),
                'level': stats.get('level', 1),
                'points': stats.get('points', 0)
            })
        
        return sorted(all_users, key=lambda x: x['downloads'], reverse=True)[:top_n]
    
    def get_achievement_info(self, achievement: str) -> Dict:
        """Get achievement information"""
        achievements_info = {
            'first_download': {'name': '🌟 البداية', 'desc': 'أول تحميل لك!'},
            'download_veteran': {'name': '⚡ المحارب', 'desc': '10 تحميلات'},
            'download_master': {'name': '🏆 الماهر', 'desc': '50 تحميل'},
            'download_legend': {'name': '👑 الأسطورة', 'desc': '100 تحميل'},
            'platform_explorer': {'name': '🌐 المستكشف', 'desc': '3 منصات مختلفة'},
            'platform_master': {'name': '🎯 سيد المنصات', 'desc': '5 منصات مختلفة'},
            'quality_enthusiast': {'name': '💎 عاشق الجودة', 'desc': '10 تحميلات عالية الجودة'},
            'audio_lover': {'name': '🎵 عاشق الموسيقى', 'desc': '20 ملف صوتي'},
            'daily_user': {'name': '📅 المستخدم اليومي', 'desc': '5 تحميلات في يوم واحد'}
        }
        return achievements_info.get(achievement, {'name': achievement, 'desc': 'إنجاز خاص'})