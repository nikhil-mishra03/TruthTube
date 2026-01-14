"""
YouTube service for extracting video metadata and transcripts.
"""
import re
from dataclasses import dataclass
from typing import Optional, List, Tuple
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import (
    TranscriptsDisabled,
    NoTranscriptFound,
    VideoUnavailable,
)
import httpx

from app.utils.logging import get_logger
from app.config import get_settings

logger = get_logger(__name__)


@dataclass
class VideoData:
    """Container for video metadata and transcript."""
    youtube_id: str
    title: str
    duration_seconds: int
    thumbnail_url: Optional[str]
    transcript: str
    word_count: int


class YouTubeService:
    """Service for fetching YouTube video data."""
    
    # Regex patterns for extracting video ID
    URL_PATTERNS = [
        re.compile(r'(?:youtube\.com/watch\?v=|youtu\.be/)([\w-]{11})'),
        re.compile(r'youtube\.com/embed/([\w-]{11})'),
        re.compile(r'youtube\.com/v/([\w-]{11})'),
    ]
    
    def __init__(self):
        self.settings = get_settings()
        self._api = YouTubeTranscriptApi()
    
    def extract_video_id(self, url: str) -> Optional[str]:
        """
        Extract video ID from a YouTube URL.
        
        Args:
            url: YouTube URL in any common format
            
        Returns:
            11-character video ID or None if not found
        """
        for pattern in self.URL_PATTERNS:
            match = pattern.search(url)
            if match:
                return match.group(1)
        return None
    
    async def validate_video_exists(self, url: str) -> tuple[bool, str, Optional[str]]:
        """
        Quick validation that a video exists (no transcript fetch).
        Uses YouTube oEmbed API - fast and doesn't require API key.
        
        Args:
            url: YouTube URL to validate
            
        Returns:
            Tuple of (is_valid, url, error_message or None)
        """
        video_id = self.extract_video_id(url)
        if not video_id:
            return False, url, "Invalid YouTube URL format"
        
        # Use oEmbed API for quick validation
        oembed_url = f"https://www.youtube.com/oembed?url=https://youtube.com/watch?v={video_id}&format=json"
        
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(oembed_url)
                if response.status_code == 200:
                    return True, url, None
                elif response.status_code == 404:
                    return False, url, "Video not found"
                else:
                    return False, url, f"YouTube returned status {response.status_code}"
        except httpx.TimeoutException:
            return False, url, "Timeout checking video"
        except Exception as e:
            return False, url, f"Error validating video: {str(e)}"
    
    async def validate_all_urls(self, urls: List[str]) -> tuple[bool, List[str]]:
        """
        Validate all URLs in parallel before processing.
        
        Args:
            urls: List of YouTube URLs to validate
            
        Returns:
            Tuple of (all_valid, list of error messages)
        """
        import asyncio
        
        logger.info(f"Validating {len(urls)} URLs...")
        tasks = [self.validate_video_exists(url) for url in urls]
        results = await asyncio.gather(*tasks)
        
        errors = []
        for is_valid, url, error_msg in results:
            if not is_valid:
                errors.append(f"{url}: {error_msg}")
        
        if errors:
            logger.warning(f"URL validation failed: {errors}")
            return False, errors
        
        logger.info("All URLs validated successfully")
        return True, []
    
    async def get_transcript_with_duration(self, video_id: str) -> Tuple[Optional[str], int]:
        """
        Fetch transcript for a YouTube video along with duration.
        
        Args:
            video_id: 11-character YouTube video ID
            
        Returns:
            Tuple of (transcript text, duration in seconds) or (None, 0) if unavailable
        """
        try:
            logger.info(f"Fetching transcript for video: {video_id}")
            
            # New API: instantiate and use fetch()
            transcript_result = self._api.fetch(video_id)
            
            # Combine all transcript segments and calculate duration
            segments = list(transcript_result)
            if not segments:
                return None, 0
            
            full_transcript = " ".join(segment.text for segment in segments)
            
            # Calculate duration from last segment
            last_segment = segments[-1]
            duration = int(last_segment.start + getattr(last_segment, 'duration', 0))
            
            logger.info(f"Transcript fetched: {len(full_transcript)} chars, {len(full_transcript.split())} words, {duration}s")
            return full_transcript, duration
            
        except TranscriptsDisabled:
            logger.warning(f"Transcripts disabled for video: {video_id}")
            return None, 0
        except NoTranscriptFound:
            logger.warning(f"No transcript found for video: {video_id}")
            return None, 0
        except VideoUnavailable:
            logger.warning(f"Video unavailable: {video_id}")
            return None, 0
        except Exception as e:
            logger.error(f"Error fetching transcript for {video_id}: {e}")
            return None, 0
    
    async def get_metadata(self, video_id: str) -> Optional[dict]:
        """
        Fetch video metadata using oEmbed API (no API key required).
        
        Args:
            video_id: 11-character YouTube video ID
            
        Returns:
            Dict with title, thumbnail_url, or None if error
        """
        try:
            url = f"https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v={video_id}&format=json"
            
            async with httpx.AsyncClient() as client:
                response = await client.get(url, timeout=10.0)
                response.raise_for_status()
                data = response.json()
                
                logger.info(f"Metadata fetched for {video_id}: {data.get('title', 'Unknown')[:50]}...")
                
                return {
                    "title": data.get("title", "Unknown"),
                    "thumbnail_url": data.get("thumbnail_url"),
                    "author_name": data.get("author_name"),
                }
                
        except Exception as e:
            logger.error(f"Error fetching metadata for {video_id}: {e}")
            raise e
    
    async def get_video_data(self, url: str) -> Optional[VideoData]:
        """
        Fetch complete video data (metadata + transcript).
        
        Args:
            url: YouTube URL
            
        Returns:
            VideoData object or None if critical data unavailable
        """
        video_id = self.extract_video_id(url)
        if not video_id:
            logger.error(f"Could not extract video ID from URL: {url}")
            return None
        
        # Fetch metadata
        metadata = await self.get_metadata(video_id)
        if not metadata:
            metadata = {"title": "Unknown", "thumbnail_url": None}
        
        # Fetch transcript and duration together
        transcript, duration = await self.get_transcript_with_duration(video_id)
        if not transcript:
            logger.error(f"No transcript available for video: {video_id}")
            return None
        
        return VideoData(
            youtube_id=video_id,
            title=metadata.get("title", "Unknown"),
            duration_seconds=duration,
            thumbnail_url=metadata.get("thumbnail_url"),
            transcript=transcript,
            word_count=len(transcript.split()),
        )
    
    async def get_multiple_video_data(self, urls: List[str]) -> List[VideoData]:
        """
        Fetch data for multiple videos.
        
        Args:
            urls: List of YouTube URLs
            
        Returns:
            List of VideoData objects (only successfully fetched videos)
        """
        import asyncio
        
        tasks = [self.get_video_data(url) for url in urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        video_data_list = []
        for i, result in enumerate(results):
            if isinstance(result, VideoData):
                video_data_list.append(result)
            elif isinstance(result, Exception):
                logger.error(f"Error processing URL {urls[i]}: {result}")
            else:
                logger.warning(f"No data retrieved for URL: {urls[i]}")
        
        logger.info(f"Successfully fetched {len(video_data_list)}/{len(urls)} videos")
        return video_data_list


# Singleton instance
youtube_service = YouTubeService()
