"""
Transcript Extractor - Extracts transcripts from YouTube videos
"""

from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound
from youtube_transcript_api.formatters import TextFormatter
from pathlib import Path
import re

from config import Config
from logger import logger


class TranscriptExtractor:
    """Extracts transcripts from YouTube videos"""

    def __init__(self):
        self.formatter = TextFormatter()
        self.temp_path = Config.TEMP_PATH
        self.temp_path.mkdir(parents=True, exist_ok=True)

    def extract_video_id(self, url):
        """Extract video ID from various YouTube URL formats"""
        patterns = [
            r'(?:youtube\.com/watch\?v=|youtu\.be/|youtube\.com/embed/)([a-zA-Z0-9_-]{11})',
            r'^([a-zA-Z0-9_-]{11})$'  # Direct video ID
        ]

        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)

        return None

    def get_transcript(self, video_id_or_url, methods=None):
        """
        Get transcript using specified methods in order

        Args:
            video_id_or_url: YouTube video ID or URL
            methods: List of methods to try (default from config)

        Returns:
            dict with 'text', 'method', 'language' or None if failed
        """
        video_id = self.extract_video_id(video_id_or_url)
        if not video_id:
            logger.error(f"Could not extract video ID from: {video_id_or_url}")
            return None

        methods = methods or Config.TRANSCRIPT_METHODS

        for method in methods:
            logger.debug(f"Trying method: {method} for video {video_id}")

            if method == "youtube_auto":
                result = self._try_youtube_auto(video_id)
            elif method == "youtube_manual":
                result = self._try_youtube_manual(video_id)
            elif method == "whisper_api":
                result = self._try_whisper_api(video_id)
            elif method == "skip":
                logger.info(f"Skipping transcript extraction for {video_id}")
                return None
            else:
                logger.warning(f"Unknown method: {method}")
                continue

            if result:
                logger.info(f"Successfully extracted transcript using {method}")
                return result

        logger.warning(f"Failed to extract transcript for {video_id} using all methods")
        return None

    def _try_youtube_auto(self, video_id):
        """Try to get auto-generated YouTube transcript"""
        try:
            transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)

            # Try auto-generated transcripts first
            try:
                transcript = transcript_list.find_generated_transcript(['en'])
                transcript_data = transcript.fetch()
                text = self.formatter.format_transcript(transcript_data)

                return {
                    'text': text,
                    'method': 'youtube_auto',
                    'language': 'en',
                    'transcript_data': transcript_data
                }
            except NoTranscriptFound:
                pass

            # Try other auto-generated languages
            for transcript in transcript_list:
                if transcript.is_generated:
                    transcript_data = transcript.fetch()
                    text = self.formatter.format_transcript(transcript_data)

                    return {
                        'text': text,
                        'method': 'youtube_auto',
                        'language': transcript.language_code,
                        'transcript_data': transcript_data
                    }

        except TranscriptsDisabled:
            logger.debug(f"Transcripts disabled for video {video_id}")
        except Exception as e:
            logger.debug(f"YouTube auto transcript error: {e}")

        return None

    def _try_youtube_manual(self, video_id):
        """Try to get manually created YouTube transcript"""
        try:
            transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)

            # Try manually created transcripts
            for transcript in transcript_list:
                if not transcript.is_generated:
                    transcript_data = transcript.fetch()
                    text = self.formatter.format_transcript(transcript_data)

                    return {
                        'text': text,
                        'method': 'youtube_manual',
                        'language': transcript.language_code,
                        'transcript_data': transcript_data
                    }

        except Exception as e:
            logger.debug(f"YouTube manual transcript error: {e}")

        return None

    def _try_whisper_api(self, video_id):
        """Try to use OpenAI Whisper API (requires audio download)"""
        if not Config.OPENAI_API_KEY:
            logger.debug("OpenAI API key not configured, skipping Whisper")
            return None

        try:
            from openai import OpenAI
            import yt_dlp

            # Initialize OpenAI client (new API v1.0+)
            client = OpenAI(api_key=Config.OPENAI_API_KEY)

            # Download audio using yt-dlp
            audio_path = self.temp_path / f"{video_id}.mp3"

            ydl_opts = {
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
                'outtmpl': str(self.temp_path / video_id),
                'quiet': True,
            }

            logger.info(f"Downloading audio for Whisper transcription: {video_id}")
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([f"https://www.youtube.com/watch?v={video_id}"])

            # Transcribe with Whisper (new API v1.0+)
            logger.info("Transcribing with OpenAI Whisper...")
            with open(audio_path, 'rb') as audio_file:
                transcript = client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file
                )

            text = transcript.text

            # Clean up audio file
            if audio_path.exists():
                audio_path.unlink()

            return {
                'text': text,
                'method': 'whisper_api',
                'language': 'en'
            }

        except Exception as e:
            logger.error(f"Whisper API error: {e}")

        return None

    def extract_with_timestamps(self, video_id_or_url):
        """Extract transcript with timestamp information"""
        video_id = self.extract_video_id(video_id_or_url)
        if not video_id:
            return None

        try:
            transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)

            # Get any available transcript
            for transcript in transcript_list:
                transcript_data = transcript.fetch()

                # Format with timestamps
                formatted_transcript = []
                for entry in transcript_data:
                    start_time = self._format_timestamp(entry['start'])
                    text = entry['text']
                    formatted_transcript.append({
                        'timestamp': start_time,
                        'seconds': entry['start'],
                        'text': text
                    })

                return {
                    'entries': formatted_transcript,
                    'full_text': self.formatter.format_transcript(transcript_data),
                    'language': transcript.language_code
                }

        except Exception as e:
            logger.error(f"Error extracting transcript with timestamps: {e}")

        return None

    def _format_timestamp(self, seconds):
        """Convert seconds to MM:SS format"""
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{minutes}:{secs:02d}"

    def validate_transcript(self, transcript_result):
        """Validate transcript quality and length"""
        if not transcript_result:
            return False, "No transcript"

        text = transcript_result['text']

        # Check length
        if len(text) < 100:
            return False, "Transcript too short"

        if len(text) > Config.MAX_TRANSCRIPT_LENGTH:
            logger.warning(f"Transcript truncated from {len(text)} to {Config.MAX_TRANSCRIPT_LENGTH} chars")
            transcript_result['text'] = text[:Config.MAX_TRANSCRIPT_LENGTH]
            transcript_result['truncated'] = True

        # Check for gibberish
        words = text.split()
        if len(words) < 20:
            return False, "Too few words"

        return True, "Valid"

    def save_raw_transcript(self, video_id, transcript_result):
        """Save raw transcript for debugging"""
        if not Config.SAVE_RAW_TRANSCRIPTS:
            return

        output_path = self.temp_path / f"{video_id}_transcript.txt"
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(transcript_result['text'])

        logger.debug(f"Saved raw transcript to: {output_path}")


# Test function
if __name__ == "__main__":
    from logger import log_section

    log_section("Transcript Extractor Test")

    extractor = TranscriptExtractor()

    # Test with a known video (replace with actual video ID)
    test_video_id = "dQw4w9WgXcQ"  # Example video ID
    logger.info(f"Testing transcript extraction for video: {test_video_id}")

    result = extractor.get_transcript(test_video_id)

    if result:
        logger.info(f"Method: {result['method']}")
        logger.info(f"Language: {result['language']}")
        logger.info(f"Text length: {len(result['text'])} characters")
        logger.info(f"Preview: {result['text'][:200]}...")

        valid, message = extractor.validate_transcript(result)
        logger.info(f"Validation: {valid} - {message}")
    else:
        logger.warning("Failed to extract transcript")
