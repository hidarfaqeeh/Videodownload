"""
Video downloader module using yt-dlp
"""

import os
import asyncio
import yt_dlp
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

class VideoDownloader:
    def __init__(self):
        # Configure yt-dlp options
        self.ydl_opts = {
            'format': 'best[height<=720][ext=mp4]/best[ext=mp4]/best',
            'outtmpl': '%(title)s.%(ext)s',
            'noplaylist': True,
            'extractaudio': False,
            'audioformat': 'mp3',
            'embed_subs': False,
            'writesubtitles': False,
            'writeautomaticsub': False,
            'quiet': True,
            'no_warnings': True,
            'ignoreerrors': False,
            'socket_timeout': 30,
            'retries': 3,
        }
        
        # Options for playlist extraction
        self.playlist_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': True,  # Only get metadata, don't download
            'ignoreerrors': True,
            'socket_timeout': 30,
        }
    
    async def get_video_info(self, url: str) -> Optional[Dict[str, Any]]:
        """Get video information without downloading"""
        try:
            loop = asyncio.get_event_loop()
            
            def _get_info():
                with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
                    return ydl.extract_info(url, download=False)
            
            info = await loop.run_in_executor(None, _get_info)
            
            if info:
                logger.info(f"Got video info for: {info.get('title', 'Unknown')}")
                return {
                    'title': info.get('title', 'Unknown Title'),
                    'duration': info.get('duration'),
                    'filesize': info.get('filesize'),
                    'filesize_approx': info.get('filesize_approx'),
                    'width': info.get('width'),
                    'height': info.get('height'),
                    'ext': info.get('ext', 'mp4'),
                    'uploader': info.get('uploader'),
                    'upload_date': info.get('upload_date'),
                }
            
        except Exception as e:
            logger.error(f"Error getting video info for {url}: {str(e)}")
            
        return None

    async def get_available_formats(self, url: str) -> Optional[Dict[str, Any]]:
        """Get available video and audio formats"""
        try:
            loop = asyncio.get_event_loop()
            
            def _get_formats():
                with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
                    return ydl.extract_info(url, download=False)
            
            info = await loop.run_in_executor(None, _get_formats)
            
            if info:
                video_formats = []
                audio_formats = []
                
                formats = info.get('formats', [])
                
                # Process video formats
                for fmt in formats:
                    if fmt.get('vcodec') != 'none' and fmt.get('height'):
                        quality = f"{fmt.get('height', 'Unknown')}p"
                        ext = fmt.get('ext', 'mp4')
                        filesize = fmt.get('filesize') or fmt.get('filesize_approx', 0)
                        
                        video_formats.append({
                            'format_id': fmt.get('format_id'),
                            'quality': quality,
                            'ext': ext,
                            'filesize': filesize,
                            'fps': fmt.get('fps'),
                            'vcodec': fmt.get('vcodec'),
                            'acodec': fmt.get('acodec')
                        })
                
                # Sort by quality (height)
                video_formats.sort(key=lambda x: int(x.get('quality', '0p')[:-1]) if x.get('quality', '0p')[:-1].isdigit() else 0, reverse=True)
                
                return {
                    'title': info.get('title', 'Unknown Title'),
                    'duration': info.get('duration'),
                    'video_formats': video_formats[:6],  # Top 6 qualities
                    'audio_formats': audio_formats,
                    'uploader': info.get('uploader')
                }
                
        except Exception as e:
            logger.error(f"Error getting formats for {url}: {str(e)}")
            
        return None
    
    async def download_video_format(self, url: str, output_dir: str, format_id: str) -> Optional[str]:
        """Download video with specific format"""
        try:
            os.makedirs(output_dir, exist_ok=True)
            
            download_opts = self.ydl_opts.copy()
            download_opts['format'] = format_id
            # Use a simple template first, we'll rename after getting info
            download_opts['outtmpl'] = os.path.join(output_dir, 'temp_video.%(ext)s')
            
            loop = asyncio.get_event_loop()
            
            def _download():
                import time
                import shutil
                
                # Create simple filename first
                timestamp = int(time.time())
                temp_name = f"video_{timestamp}"
                download_opts['outtmpl'] = os.path.join(output_dir, f'{temp_name}.%(ext)s')
                
                with yt_dlp.YoutubeDL(download_opts) as ydl:
                    ydl.download([url])
                    
                    # Find the downloaded file with our timestamp
                    for file in os.listdir(output_dir):
                        if temp_name in file and file.endswith(('mp4', 'webm', 'mkv', 'avi')):
                            return os.path.join(output_dir, file)
                    
                    return None
            
            result = await loop.run_in_executor(None, _download)
            return result
            
        except Exception as e:
            logger.error(f"Error downloading video format {format_id} from {url}: {str(e)}")
            return None

    async def download_audio(self, url: str, output_dir: str, quality: str = "best") -> Optional[str]:
        """Download audio and convert to MP3"""
        try:
            os.makedirs(output_dir, exist_ok=True)
            
            download_opts = {
                'format': 'bestaudio[ext=m4a]/bestaudio[ext=webm]/bestaudio/best' if quality == "best" else 'worstaudio/worst',
                'outtmpl': os.path.join(output_dir, 'temp_audio.%(ext)s'),
                'quiet': True,
                'no_warnings': True,
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192' if quality == "best" else '128',
                }],
                'postprocessor_args': [
                    '-ar', '44100'
                ],
            }
            
            loop = asyncio.get_event_loop()
            
            def _download():
                import time
                
                # Create simple filename
                timestamp = int(time.time())
                temp_name = f"audio_{timestamp}"
                download_opts['outtmpl'] = os.path.join(output_dir, f'{temp_name}.%(ext)s')
                
                with yt_dlp.YoutubeDL(download_opts) as ydl:
                    ydl.download([url])
                    
                    # Find the downloaded MP3 file
                    for file in os.listdir(output_dir):
                        if temp_name in file and file.endswith('.mp3'):
                            return os.path.join(output_dir, file)
                    
                    return None
            
            result = await loop.run_in_executor(None, _download)
            return result
            
        except Exception as e:
            logger.error(f"Error downloading audio from {url}: {str(e)}")
            return None

    async def download_video(self, url: str, output_dir: str) -> Optional[str]:
        """Download video and return the file path"""
        try:
            # Create output directory if it doesn't exist
            os.makedirs(output_dir, exist_ok=True)
            
            # Update output template with directory
            download_opts = self.ydl_opts.copy()
            download_opts['outtmpl'] = os.path.join(output_dir, '%(title)s.%(ext)s')
            
            loop = asyncio.get_event_loop()
            
            def _download():
                with yt_dlp.YoutubeDL(download_opts) as ydl:
                    # Get info first to determine filename
                    info = ydl.extract_info(url, download=False)
                    if not info:
                        return None
                    
                    # Sanitize filename
                    title = info.get('title', 'video').replace('/', '_').replace('\\', '_')
                    title = ''.join(c for c in title if c.isalnum() or c in (' ', '-', '_', '.'))[:100]
                    ext = info.get('ext', 'mp4')
                    
                    # Set specific output path
                    filename = f"{title}.{ext}"
                    output_path = os.path.join(output_dir, filename)
                    download_opts['outtmpl'] = output_path.replace('.mp4', '.%(ext)s')
                    
                    # Download
                    ydl.download([url])
                    
                    # Find the downloaded file
                    for file in os.listdir(output_dir):
                        if file.startswith(title) and file.endswith(('mp4', 'webm', 'mkv', 'avi')):
                            return os.path.join(output_dir, file)
                    
                    return output_path if os.path.exists(output_path) else None
            
            result = await loop.run_in_executor(None, _download)
            
            if result and os.path.exists(result):
                logger.info(f"Successfully downloaded: {result}")
                return result
            else:
                logger.error(f"Download failed or file not found for {url}")
                return None
                
        except Exception as e:
            logger.error(f"Error downloading video from {url}: {str(e)}")
            return None
    
    def get_supported_sites(self) -> list:
        """Get list of supported sites"""
        try:
            with yt_dlp.YoutubeDL() as ydl:
                extractors = ydl.list_extractors()
                return [extractor.IE_NAME for extractor in extractors]
        except:
            return ['youtube', 'twitter', 'instagram', 'facebook', 'tiktok']

    async def get_playlist_info(self, url: str) -> Optional[Dict[str, Any]]:
        """Get playlist/channel information and videos list"""
        try:
            loop = asyncio.get_event_loop()
            
            def _get_playlist():
                with yt_dlp.YoutubeDL(self.playlist_opts) as ydl:
                    return ydl.extract_info(url, download=False)
            
            info = await loop.run_in_executor(None, _get_playlist)
            
            if info and 'entries' in info:
                playlist_title = info.get('title', 'قائمة تشغيل')
                entries = []
                
                # Process first 50 videos (to avoid overwhelming)
                for i, entry in enumerate(info['entries'][:50]):
                    if entry and entry.get('id'):
                        entries.append({
                            'id': entry.get('id'),
                            'title': entry.get('title', f'فيديو {i+1}'),
                            'duration': entry.get('duration'),
                            'url': entry.get('url') or f"https://www.youtube.com/watch?v={entry.get('id')}",
                            'thumbnail': entry.get('thumbnail'),
                            'index': i + 1
                        })
                
                logger.info(f"Got playlist info: {playlist_title} with {len(entries)} videos")
                return {
                    'type': 'playlist',
                    'title': playlist_title,
                    'entries': entries,
                    'total_count': len(entries),
                    'uploader': info.get('uploader', 'غير محدد'),
                    'description': info.get('description', '')
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting playlist info: {e}")
            return None

    async def is_playlist_url(self, url: str) -> bool:
        """Check if URL is a playlist or channel"""
        playlist_indicators = [
            'playlist?list=',
            'watch?v=.*&list=',
            '/channel/',
            '/c/',
            '/@',
            '/user/',
            'youtube.com/playlist',
            'youtube.com/channel'
        ]
        
        return any(indicator in url.lower() for indicator in playlist_indicators)
