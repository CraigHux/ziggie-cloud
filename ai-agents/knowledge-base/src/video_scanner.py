"""
Video Scanner - Discovers new YouTube videos from creators
"""

import json
from datetime import datetime, timedelta
from pathlib import Path
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from config import Config
from logger import logger


class VideoScanner:
    """Scans YouTube channels for new videos"""

    def __init__(self):
        self.youtube = None
        if Config.YOUTUBE_API_KEY:
            self.youtube = build('youtube', 'v3', developerKey=Config.YOUTUBE_API_KEY)

        self.creator_db_path = Config.METADATA_PATH / "creator-database.json"
        self.creators = self.load_creators()

    def load_creators(self):
        """Load creator database"""
        if not self.creator_db_path.exists():
            logger.error(f"Creator database not found: {self.creator_db_path}")
            return {"creators": []}

        with open(self.creator_db_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def get_channel_id_from_handle(self, handle):
        """Convert @handle to channel ID"""
        try:
            # Remove @ if present
            handle = handle.replace("@", "")

            # Search for channel
            request = self.youtube.search().list(
                part="snippet",
                q=handle,
                type="channel",
                maxResults=1
            )
            response = request.execute()

            if response.get('items'):
                return response['items'][0]['snippet']['channelId']
            else:
                logger.warning(f"Channel not found for handle: {handle}")
                return None

        except HttpError as e:
            logger.error(f"YouTube API error for {handle}: {e}")
            return None

    def get_recent_videos(self, channel_id, max_results=None, days_back=None):
        """Get recent videos from a channel"""
        if not self.youtube:
            logger.error("YouTube API not initialized (missing API key)")
            return []

        max_results = max_results or Config.MAX_VIDEOS_PER_SCAN
        days_back = days_back or Config.SCAN_LOOKBACK_DAYS

        try:
            # Calculate published_after date
            published_after = (datetime.now() - timedelta(days=days_back)).isoformat() + "Z"

            # Search for recent uploads
            request = self.youtube.search().list(
                part="snippet",
                channelId=channel_id,
                order="date",
                type="video",
                publishedAfter=published_after,
                maxResults=max_results
            )
            response = request.execute()

            videos = []
            for item in response.get('items', []):
                video_data = {
                    'video_id': item['id']['videoId'],
                    'title': item['snippet']['title'],
                    'description': item['snippet']['description'],
                    'published_at': item['snippet']['publishedAt'],
                    'channel_id': channel_id,
                    'thumbnail': item['snippet']['thumbnails'].get('medium', {}).get('url'),
                    'url': f"https://www.youtube.com/watch?v={item['id']['videoId']}"
                }
                videos.append(video_data)

            logger.info(f"Found {len(videos)} recent videos for channel {channel_id}")
            return videos

        except HttpError as e:
            logger.error(f"YouTube API error for channel {channel_id}: {e}")
            return []

    def get_video_details(self, video_id):
        """Get detailed information about a video"""
        if not self.youtube:
            return None

        try:
            request = self.youtube.videos().list(
                part="snippet,contentDetails,statistics",
                id=video_id
            )
            response = request.execute()

            if not response.get('items'):
                return None

            item = response['items'][0]

            # Parse duration (PT format: PT15M33S)
            duration_str = item['contentDetails']['duration']
            duration_seconds = self.parse_duration(duration_str)

            return {
                'video_id': video_id,
                'title': item['snippet']['title'],
                'description': item['snippet']['description'],
                'published_at': item['snippet']['publishedAt'],
                'channel_id': item['snippet']['channelId'],
                'channel_title': item['snippet']['channelTitle'],
                'duration_seconds': duration_seconds,
                'view_count': int(item['statistics'].get('viewCount', 0)),
                'like_count': int(item['statistics'].get('likeCount', 0)),
                'comment_count': int(item['statistics'].get('commentCount', 0)),
                'url': f"https://www.youtube.com/watch?v={video_id}"
            }

        except HttpError as e:
            logger.error(f"YouTube API error for video {video_id}: {e}")
            return None

    def parse_duration(self, duration_str):
        """Parse PT duration format to seconds"""
        import re
        pattern = r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?'
        match = re.match(pattern, duration_str)

        if not match:
            return 0

        hours = int(match.group(1) or 0)
        minutes = int(match.group(2) or 0)
        seconds = int(match.group(3) or 0)

        return hours * 3600 + minutes * 60 + seconds

    def scan_creator(self, creator_id):
        """Scan a specific creator for new videos"""
        creator = next((c for c in self.creators['creators'] if c['id'] == creator_id), None)

        if not creator:
            logger.error(f"Creator not found: {creator_id}")
            return []

        logger.info(f"Scanning creator: {creator['name']} ({creator['handle']})")

        # Get channel ID
        channel_id = self.get_channel_id_from_handle(creator['handle'])
        if not channel_id:
            logger.error(f"Could not resolve channel ID for {creator['handle']}")
            return []

        # Get recent videos
        max_results = creator.get('scan_last_n_videos', Config.MAX_VIDEOS_PER_SCAN)
        videos = self.get_recent_videos(channel_id, max_results=max_results)

        # Filter by duration
        filtered_videos = []
        for video in videos:
            details = self.get_video_details(video['video_id'])
            if not details:
                continue

            duration = details['duration_seconds']

            # Check duration constraints
            if duration < Config.MIN_VIDEO_DURATION:
                logger.debug(f"Skipping {video['title']} (too short: {duration}s)")
                continue

            if duration > Config.MAX_VIDEO_DURATION:
                logger.debug(f"Skipping {video['title']} (too long: {duration}s)")
                continue

            # Add creator info
            details['creator_id'] = creator_id
            details['creator_name'] = creator['name']
            details['creator_priority'] = creator['priority']

            filtered_videos.append(details)

        logger.info(f"Filtered to {len(filtered_videos)} videos (duration constraints applied)")
        return filtered_videos

    def scan_all_creators(self, priority_filter=None):
        """Scan all creators (optionally filtered by priority)"""
        creators_to_scan = self.creators['creators']

        if priority_filter:
            creators_to_scan = [c for c in creators_to_scan if c['priority'] == priority_filter]

        logger.info(f"Scanning {len(creators_to_scan)} creators...")

        all_videos = []
        for creator in creators_to_scan:
            videos = self.scan_creator(creator['id'])
            all_videos.extend(videos)

        logger.info(f"Total videos discovered: {len(all_videos)}")
        return all_videos

    def scan_by_priority(self):
        """Scan creators based on priority levels"""
        results = {}

        for priority in ['critical', 'high', 'medium', 'low']:
            logger.info(f"Scanning {priority} priority creators...")
            videos = self.scan_all_creators(priority_filter=priority)
            results[priority] = videos

        return results


# Test function
if __name__ == "__main__":
    from logger import log_section

    log_section("Video Scanner Test")

    scanner = VideoScanner()

    # Test with InstaSD
    logger.info("Testing with InstaSD...")
    videos = scanner.scan_creator("instasd")

    if videos:
        logger.info(f"\nFound {len(videos)} videos from InstaSD:")
        for video in videos[:3]:  # Show first 3
            logger.info(f"  - {video['title']}")
            logger.info(f"    Duration: {video['duration_seconds']}s")
            logger.info(f"    URL: {video['url']}")
    else:
        logger.warning("No videos found or API key not configured")
