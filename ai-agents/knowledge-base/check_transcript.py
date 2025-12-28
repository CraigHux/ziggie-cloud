#!/usr/bin/env python3
"""Quick script to check if a video has transcripts"""

import sys
from youtube_transcript_api import YouTubeTranscriptApi

video_id = sys.argv[1] if len(sys.argv) > 1 else "KNURuuZW8VA"

try:
    transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
    print(f"Available transcripts for {video_id}:")
    print()

    for transcript in transcript_list:
        transcript_type = "auto-generated" if transcript.is_generated else "manual"
        print(f"  - {transcript.language} ({transcript.language_code}) - {transcript_type}")

    print()
    print("Attempting to fetch English transcript...")
    transcript = YouTubeTranscriptApi.get_transcript(video_id)
    print(f"Success! Transcript has {len(transcript)} segments")
    print(f"First segment: {transcript[0]['text'][:100]}...")

except Exception as e:
    print(f"Error: {e}")
    print()
    print("This video may not have transcripts/captions available.")
