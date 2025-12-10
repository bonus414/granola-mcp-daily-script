#!/usr/bin/env python3
"""
Daily backup script for Granola meeting transcripts.
Reads from Granola's cache and saves transcripts as markdown files.

CONFIGURATION: Set OUTPUT_DIR below to your desired backup location
"""

import json
import os
from pathlib import Path
from datetime import datetime
import zoneinfo
import sys

# ============================================================================
# CONFIGURATION - Customize these settings for your setup
# ============================================================================

# Where to save transcript backups (change this to your preferred location)
# You can also set via environment variable: GRANOLA_BACKUP_DIR
OUTPUT_DIR = os.getenv(
    "GRANOLA_BACKUP_DIR",
    os.path.expanduser("~/Documents/granola-transcripts")  # Default location
)

# Your timezone (auto-detects if not set, or set via GRANOLA_TIMEZONE env var)
# Common options: America/New_York, America/Chicago, America/Denver, America/Los_Angeles
TIMEZONE = os.getenv("GRANOLA_TIMEZONE", None)  # None = auto-detect

# Granola cache location (standard for all macOS users, usually doesn't need changing)
GRANOLA_CACHE_PATH = os.path.expanduser("~/Library/Application Support/Granola/cache-v3.json")

# ============================================================================
# No need to edit below this line
# ============================================================================

def detect_timezone():
    """Auto-detect system timezone."""
    if TIMEZONE:
        try:
            return zoneinfo.ZoneInfo(TIMEZONE)
        except Exception:
            print(f"Warning: Invalid timezone '{TIMEZONE}', using auto-detection")

    try:
        import time
        # Try to get system timezone
        if hasattr(time, 'tzname') and time.tzname:
            tz_mapping = {
                'EST': 'America/New_York', 'EDT': 'America/New_York',
                'CST': 'America/Chicago', 'CDT': 'America/Chicago',
                'MST': 'America/Denver', 'MDT': 'America/Denver',
                'PST': 'America/Los_Angeles', 'PDT': 'America/Los_Angeles'
            }
            current_tz = time.tzname[time.daylight]
            if current_tz in tz_mapping:
                return zoneinfo.ZoneInfo(tz_mapping[current_tz])

        # Fallback: detect from system offset
        local_offset = time.timezone if not time.daylight else time.altzone
        hours_offset = -local_offset // 3600

        offset_mapping = {
            -8: 'America/Los_Angeles', -7: 'America/Denver',
            -6: 'America/Chicago', -5: 'America/New_York',
            -4: 'America/New_York'
        }

        if hours_offset in offset_mapping:
            return zoneinfo.ZoneInfo(offset_mapping[hours_offset])
    except Exception as e:
        print(f"Warning: Error detecting timezone: {e}")

    # Ultimate fallback to UTC
    return zoneinfo.ZoneInfo('UTC')

def load_granola_cache():
    """Load and parse Granola cache file."""
    try:
        cache_path = Path(GRANOLA_CACHE_PATH)
        if not cache_path.exists():
            print(f"ERROR: Cache file not found at {GRANOLA_CACHE_PATH}")
            return None

        with open(cache_path, 'r', encoding='utf-8') as f:
            raw_data = json.load(f)

        # Handle Granola's nested cache structure
        if 'cache' in raw_data and isinstance(raw_data['cache'], str):
            actual_data = json.loads(raw_data['cache'])
            if 'state' in actual_data:
                return actual_data['state']
            return actual_data

        return raw_data

    except Exception as e:
        print(f"ERROR loading cache: {e}")
        return None

def parse_meetings(cache_data):
    """Extract meeting metadata from cache."""
    meetings = {}

    if "documents" not in cache_data:
        return meetings

    for meeting_id, meeting_data in cache_data["documents"].items():
        try:
            # Extract participants
            participants = []
            if "people" in meeting_data and isinstance(meeting_data["people"], list):
                participants = [person.get("name", "") for person in meeting_data["people"] if person.get("name")]

            # Parse creation date
            created_at = meeting_data.get("created_at")
            if created_at:
                if created_at.endswith('Z'):
                    created_at = created_at[:-1] + '+00:00'
                meeting_date = datetime.fromisoformat(created_at)
                if meeting_date.tzinfo is None:
                    meeting_date = meeting_date.replace(tzinfo=zoneinfo.ZoneInfo('UTC'))
            else:
                meeting_date = datetime.now(zoneinfo.ZoneInfo('UTC'))

            meetings[meeting_id] = {
                'id': meeting_id,
                'title': meeting_data.get("title", "Untitled Meeting"),
                'date': meeting_date,
                'participants': participants,
                'type': meeting_data.get("type", "meeting")
            }
        except Exception as e:
            print(f"Warning: Error parsing meeting {meeting_id}: {e}")

    return meetings

def parse_transcripts(cache_data):
    """Extract transcripts from cache."""
    transcripts = {}

    if "transcripts" not in cache_data:
        return transcripts

    for transcript_id, transcript_data in cache_data["transcripts"].items():
        try:
            content_parts = []
            speakers_set = set()

            if isinstance(transcript_data, list):
                # Granola format: list of speech segments
                for segment in transcript_data:
                    if isinstance(segment, dict) and "text" in segment:
                        text = segment["text"].strip()
                        if text:
                            content_parts.append(text)

                        # Extract speaker info
                        if "source" in segment:
                            speakers_set.add(segment["source"])

            if content_parts:
                transcripts[transcript_id] = {
                    'content': " ".join(content_parts),
                    'speakers': list(speakers_set)
                }

        except Exception as e:
            print(f"Warning: Error parsing transcript {transcript_id}: {e}")

    return transcripts

def create_filename(meeting_title, meeting_date, local_tz):
    """Create a safe filename from meeting title and date."""
    # Convert to local timezone for filename
    local_date = meeting_date.astimezone(local_tz)

    # Format: YYYY-MM-DD_HHMM_Title.md
    date_str = local_date.strftime('%Y-%m-%d_%H%M')

    # Clean title for filename
    safe_title = "".join(c for c in meeting_title if c.isalnum() or c in (' ', '-', '_')).strip()
    safe_title = safe_title.replace(' ', '_')
    safe_title = safe_title[:100]  # Limit length

    return f"{date_str}_{safe_title}.md"

def save_transcript_to_file(meeting, transcript, output_dir, local_tz):
    """Save a meeting transcript as a markdown file."""
    try:
        # Create output directory if it doesn't exist
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        # Create filename
        filename = create_filename(meeting['title'], meeting['date'], local_tz)
        filepath = output_path / filename

        # Skip if file already exists
        if filepath.exists():
            print(f"  Already exists: {filename}")
            return False

        # Format local time
        local_date = meeting['date'].astimezone(local_tz)
        date_str = local_date.strftime('%Y-%m-%d %H:%M %Z')

        # Build markdown content
        md_content = f"# {meeting['title']}\n\n"
        md_content += f"**Date:** {date_str}\n"
        md_content += f"**Meeting ID:** {meeting['id']}\n"

        if meeting['participants']:
            md_content += f"**Participants:** {', '.join(meeting['participants'])}\n"

        if transcript.get('speakers'):
            md_content += f"**Speakers:** {', '.join(transcript['speakers'])}\n"

        md_content += f"\n---\n\n## Transcript\n\n{transcript['content']}\n"

        # Write to file
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(md_content)

        print(f"  ✓ Saved: {filename}")
        return True

    except Exception as e:
        print(f"  ERROR saving {meeting['title']}: {e}")
        return False

def main():
    """Main backup function."""
    # Detect timezone
    local_tz = detect_timezone()

    print(f"\n=== Granola Transcript Backup ===")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Output: {OUTPUT_DIR}")
    print(f"Timezone: {local_tz}\n")

    # Load cache
    print("Loading Granola cache...")
    cache_data = load_granola_cache()
    if not cache_data:
        print("Failed to load cache. Exiting.")
        sys.exit(1)

    # Parse meetings and transcripts
    print("Parsing meetings and transcripts...")
    meetings = parse_meetings(cache_data)
    transcripts = parse_transcripts(cache_data)

    print(f"Found {len(meetings)} meetings and {len(transcripts)} transcripts\n")

    # Save transcripts
    saved_count = 0
    skipped_count = 0

    for meeting_id, meeting in meetings.items():
        if meeting_id in transcripts:
            result = save_transcript_to_file(meeting, transcripts[meeting_id], OUTPUT_DIR, local_tz)
            if result:
                saved_count += 1
            else:
                skipped_count += 1

    # Summary
    print(f"\n=== Backup Complete ===")
    print(f"Saved: {saved_count} new transcripts")
    print(f"Skipped: {skipped_count} existing files")
    print(f"Total: {len(transcripts)} transcripts in cache\n")

if __name__ == "__main__":
    main()
