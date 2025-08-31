"""
Video downloader module using yt-dlp
"""

import os
import asyncio
import yt_dlp
import logging
import base64
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

        # Load cookies configuration from environment via config
        from config import (
            COOKIES_ENABLED,
            COOKIES_FILE_PATH,
            COOKIES_B64,
            COOKIES_RAW,
            COOKIES_APPLY_ON_FAILURE_ONLY,
        )

        self.cookies_enabled = COOKIES_ENABLED
        self.cookies_apply_on_failure_only = COOKIES_APPLY_ON_FAILURE_ONLY
        self.cookies_mode = 'none'  # 'file' | 'raw' | 'none'
        self.cookies_file_path: Optional[str] = None
        self.cookies_raw: Optional[str] = None

        if self.cookies_enabled:
            try:
                if COOKIES_FILE_PATH and os.path.exists(COOKIES_FILE_PATH):
                    self.cookies_mode = 'file'
                    self.cookies_file_path = COOKIES_FILE_PATH
                    logger.info("Cookies enabled: using COOKIES_FILE_PATH")
                elif COOKIES_B64:
                    decoded = base64.b64decode(COOKIES_B64)
                    temp_path = os.path.join('/tmp', 'ytdlp_cookies_env.txt')
                    with open(temp_path, 'wb') as f:
                        f.write(decoded)
                    try:
                        os.chmod(temp_path, 0o600)
                    except Exception:
                        pass
                    self.cookies_mode = 'file'
                    self.cookies_file_path = temp_path
                    logger.info("Cookies enabled: using COOKIES_B64 written to temp file")
                elif COOKIES_RAW:
                    self.cookies_mode = 'raw'
                    self.cookies_raw = COOKIES_RAW
                    logger.info("Cookies enabled: using COOKIES_RAW header")
                else:
                    logger.info("Cookies enabled but no source provided (FILE/B64/RAW).")
            except Exception as e:
                logger.error(f"Failed to initialize cookies from env: {e}")

        # If cookies should always apply, merge into default opts now
        if self.cookies_enabled and not self.cookies_apply_on_failure_only:
            self.ydl_opts = self._merge_cookie_opts(self.ydl_opts)
            self.playlist_opts = self._merge_cookie_opts(self.playlist_opts)

    def _merge_cookie_opts(self, opts: Dict[str, Any]) -> Dict[str, Any]:
        """Merge cookie configuration into yt-dlp options if configured."""
        if not self.cookies_enabled:
            return opts
        merged = opts.copy()
        if self.cookies_mode == 'file' and self.cookies_file_path:
            merged['cookiefile'] = self.cookies_file_path
        elif self.cookies_mode == 'raw' and self.cookies_raw:
            headers = merged.get('http_headers', {}).copy()
            headers['Cookie'] = self.cookies_raw
            merged['http_headers'] = headers
        return merged

    def _build_opts(self, base_opts: Dict[str, Any], overrides: Optional[Dict[str, Any]] = None, use_cookies: bool = False) -> Dict[str, Any]:
        opts = base_opts.copy()
        if overrides:
            opts.update(overrides)
        if use_cookies:
            opts = self._merge_cookie_opts(opts)
        return opts
    
    async def get_video_info(self, url: str) -> Optional[Dict[str, Any]]:
        """Get video information without downloading"""
        try:
            loop = asyncio.get_event_loop()
            
            def _get_info(opts: Dict[str, Any]):
                with yt_dlp.YoutubeDL(opts) as ydl:
                    return ydl.extract_info(url, download=False)
            
            info = None
            try:
                info = await loop.run_in_executor(None, _get_info, self.ydl_opts)
            except Exception as e:
                if self.cookies_enabled and self.cookies_apply_on_failure_only:
                    cookie_opts = self._build_opts(self.ydl_opts, use_cookies=True)
                    logger.warning(f"Info fetch failed, retrying with cookies: {e}")
                    info = await loop.run_in_executor(None, _get_info, cookie_opts)
                else:
                    raise
            
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
            
            def _get_formats(opts: Dict[str, Any]):
                with yt_dlp.YoutubeDL(opts) as ydl:
                    return ydl.extract_info(url, download=False)
            
            info = None
            try:
                info = await loop.run_in_executor(None, _get_formats, self.ydl_opts)
            except Exception as e:
                if self.cookies_enabled and self.cookies_apply_on_failure_only:
                    cookie_opts = self._build_opts(self.ydl_opts, use_cookies=True)
                    logger.warning(f"Format fetch failed, retrying with cookies: {e}")
                    info = await loop.run_in_executor(None, _get_formats, cookie_opts)
                else:
                    raise
            
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
            
            overrides = {
                'format': format_id,
                'outtmpl': os.path.join(output_dir, 'temp_video.%(ext)s'),
            }
            download_opts = self._build_opts(self.ydl_opts, overrides=overrides, use_cookies=(self.cookies_enabled and not self.cookies_apply_on_failure_only))
            
            loop = asyncio.get_event_loop()
            
            def _download(opts: Dict[str, Any]):
                import time
                import shutil
                
                # Create simple filename first
                timestamp = int(time.time())
                temp_name = f"video_{timestamp}"
                opts = opts.copy()
                opts['outtmpl'] = os.path.join(output_dir, f'{temp_name}.%(ext)s')
                
                with yt_dlp.YoutubeDL(opts) as ydl:
                    ydl.download([url])
                    
                    # Find the downloaded file with our timestamp
                    for file in os.listdir(output_dir):
                        if temp_name in file and file.endswith(('mp4', 'webm', 'mkv', 'avi')):
                            return os.path.join(output_dir, file)
                    
                    return None
            
            result = None
            try:
                result = await loop.run_in_executor(None, _download, download_opts)
            except Exception as e:
                if self.cookies_enabled and self.cookies_apply_on_failure_only:
                    cookie_opts = self._build_opts(self.ydl_opts, overrides=overrides, use_cookies=True)
                    logger.warning(f"Format download failed, retrying with cookies: {e}")
                    result = await loop.run_in_executor(None, _download, cookie_opts)
                else:
                    raise
            return result
            
        except Exception as e:
            logger.error(f"Error downloading video format {format_id} from {url}: {str(e)}")
            return None

    async def download_audio(self, url: str, output_dir: str, quality: str = "best") -> Optional[str]:
        """Download audio and convert to MP3"""
        try:
            os.makedirs(output_dir, exist_ok=True)
            
            base_opts = {
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
            download_opts = self._build_opts(base_opts, use_cookies=(self.cookies_enabled and not self.cookies_apply_on_failure_only))
            
            loop = asyncio.get_event_loop()
            
            def _download(opts: Dict[str, Any]):
                import time
                
                # Create simple filename
                timestamp = int(time.time())
                temp_name = f"audio_{timestamp}"
                opts = opts.copy()
                opts['outtmpl'] = os.path.join(output_dir, f'{temp_name}.%(ext)s')
                
                with yt_dlp.YoutubeDL(opts) as ydl:
                    ydl.download([url])
                    
                    # Find the downloaded MP3 file
                    for file in os.listdir(output_dir):
                        if temp_name in file and file.endswith('.mp3'):
                            return os.path.join(output_dir, file)
                    
                    return None
            
            result = None
            try:
                result = await loop.run_in_executor(None, _download, download_opts)
            except Exception as e:
                if self.cookies_enabled and self.cookies_apply_on_failure_only:
                    cookie_opts = self._build_opts(base_opts, use_cookies=True)
                    logger.warning(f"Audio download failed, retrying with cookies: {e}")
                    result = await loop.run_in_executor(None, _download, cookie_opts)
                else:
                    raise
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
            overrides = {
                'outtmpl': os.path.join(output_dir, '%(title)s.%(ext)s')
            }
            base_opts = self._build_opts(self.ydl_opts, overrides=overrides, use_cookies=(self.cookies_enabled and not self.cookies_apply_on_failure_only))
            
            loop = asyncio.get_event_loop()
            
            def _download(opts: Dict[str, Any]):
                with yt_dlp.YoutubeDL(opts) as ydl:
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
                    opts = opts.copy()
                    opts['outtmpl'] = output_path.replace('.mp4', '.%(ext)s')
                    
                    # Download
                    ydl.download([url])
                    
                    # Find the downloaded file
                    for file in os.listdir(output_dir):
                        if file.startswith(title) and file.endswith(('mp4', 'webm', 'mkv', 'avi')):
                            return os.path.join(output_dir, file)
                    
                    return output_path if os.path.exists(output_path) else None
            
            result = None
            try:
                result = await loop.run_in_executor(None, _download, base_opts)
            except Exception as e:
                if self.cookies_enabled and self.cookies_apply_on_failure_only:
                    cookie_opts = self._build_opts(self.ydl_opts, overrides=overrides, use_cookies=True)
                    logger.warning(f"Video download failed, retrying with cookies: {e}")
                    result = await loop.run_in_executor(None, _download, cookie_opts)
                else:
                    raise
            
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
            
            def _get_playlist(opts: Dict[str, Any]):
                with yt_dlp.YoutubeDL(opts) as ydl:
                    return ydl.extract_info(url, download=False)
            
            info = None
            try:
                info = await loop.run_in_executor(None, _get_playlist, self.playlist_opts)
            except Exception as e:
                if self.cookies_enabled and self.cookies_apply_on_failure_only:
                    cookie_opts = self._build_opts(self.playlist_opts, use_cookies=True)
                    logger.warning(f"Playlist info fetch failed, retrying with cookies: {e}")
                    info = await loop.run_in_executor(None, _get_playlist, cookie_opts)
                else:
                    raise
            
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
