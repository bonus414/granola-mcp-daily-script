# Granola Transcript Backup

A simple Python script to automatically backup your [Granola.ai](https://granola.ai) meeting transcripts before they expire from the 2-day cache.

## Why This Exists

Granola only keeps transcripts in its local cache for about 2 days. If you have many meetings, you might lose valuable transcripts before you can review them. This script automatically saves them as markdown files so you never lose a conversation.

## Features

- 🕐 **Daily Automation** - Set it up once, runs automatically every night at 11 PM
- 📝 **Markdown Export** - Saves transcripts as readable, searchable markdown files
- 🔒 **100% Local** - All data stays on your machine, no external API calls
- 🚫 **Smart Deduplication** - Never overwrites existing backups
- ⚙️ **Easy Configuration** - Simple environment variables or one-line edits
- 🌍 **Timezone Smart** - Auto-detects your timezone or customize it

## Quick Start

### Prerequisites

- macOS with [Granola.ai](https://granola.ai) installed
- Python 3.8+ (comes with macOS)
- Granola cache file at `~/Library/Application Support/Granola/cache-v3.json`

### Installation

**1. Download the script:**

```bash
curl -O https://raw.githubusercontent.com/bonus414/granola-transcript-backup/main/backup_transcripts.py
chmod +x backup_transcripts.py
```

Or just clone this repo:

```bash
git clone https://github.com/bonus414/granola-transcript-backup.git
cd granola-transcript-backup
```

**2. Customize the backup location (optional):**

Edit `backup_transcripts.py` line 23 to set where you want backups saved:

```python
OUTPUT_DIR = os.path.expanduser("~/Documents/granola-transcripts")  # Change this
```

Or use an environment variable:

```bash
export GRANOLA_BACKUP_DIR="$HOME/Dropbox/Granola"
```

**3. Test it:**

```bash
python3 backup_transcripts.py
```

You should see output like:

```
=== Granola Transcript Backup ===
Time: 2025-12-09 18:50:13
Output: /Users/you/Documents/granola-transcripts

Loading Granola cache...
Parsing meetings and transcripts...
Found 1132 meetings and 7 transcripts

  ✓ Saved: 2025-12-09_1430_Team_Standup.md
  ✓ Saved: 2025-12-09_1600_Product_Review.md

=== Backup Complete ===
Saved: 2 new transcripts
```

**4. Set up daily automation (optional):**

```bash
./install_daily_backup.sh
```

This creates a launchd job that runs the script every night at 11 PM.

## Configuration

### Output Directory

**Option 1: Edit the script (line 23)**

```python
OUTPUT_DIR = os.path.expanduser("~/Documents/my-backups")
```

**Option 2: Environment variable**

```bash
export GRANOLA_BACKUP_DIR="$HOME/path/to/backups"
python3 backup_transcripts.py
```

### Timezone

By default, the script auto-detects your timezone. To override:

**Option 1: Edit the script (line 28)**

```python
TIMEZONE = "America/Chicago"  # CST/CDT
```

**Option 2: Environment variable**

```bash
export GRANOLA_TIMEZONE="America/New_York"
```

Common US timezones:
- `America/New_York` (EST/EDT)
- `America/Chicago` (CST/CDT)
- `America/Denver` (MST/MDT)
- `America/Los_Angeles` (PST/PDT)

### Backup Schedule

The default installation runs at 11:00 PM. To change this, edit the plist file:

```bash
# After running install script, edit:
nano ~/Library/LaunchAgents/com.granola.backup.plist
```

Change the Hour and Minute values, then reload:

```bash
launchctl unload ~/Library/LaunchAgents/com.granola.backup.plist
launchctl load ~/Library/LaunchAgents/com.granola.backup.plist
```

## Output Format

Transcripts are saved as markdown files with this format:

```
YYYY-MM-DD_HHMM_Meeting_Title.md
```

Example file contents:

```markdown
# Team Standup

**Date:** 2025-12-09 14:30 PST
**Meeting ID:** abc123-def456
**Participants:** Alice, Bob, Charlie
**Speakers:** microphone, system

---

## Transcript

[Full conversation transcript here...]
```

## Manual Operations

### Run Backup Manually

```bash
python3 backup_transcripts.py
```

### Check if Daily Backup is Running

```bash
launchctl list | grep com.granola.backup
```

### View Backup Logs

```bash
cat backup.log
cat backup.error.log
```

### Uninstall Daily Backup

```bash
launchctl unload ~/Library/LaunchAgents/com.granola.backup.plist
rm ~/Library/LaunchAgents/com.granola.backup.plist
```

## Troubleshooting

### "Cache file not found"

Make sure Granola.ai is installed and has processed some meetings:

```bash
ls -la ~/Library/Application\ Support/Granola/cache-v3.json
```

### "Permission denied"

Make the script executable:

```bash
chmod +x backup_transcripts.py
```

### Daily backup not running

Check if the job is loaded:

```bash
launchctl list | grep com.granola.backup
```

If not, reload it:

```bash
launchctl load ~/Library/LaunchAgents/com.granola.backup.plist
```

Check error logs:

```bash
cat backup.error.log
```

### No new transcripts appearing

- Granola may not have new transcripts in cache (only keeps ~2 days)
- Check if Granola is running and recording meetings
- Run the script manually to see what it finds

## How It Works

1. Reads Granola's local cache file (`~/Library/Application Support/Granola/cache-v3.json`)
2. Parses meetings and transcript data
3. Converts transcripts to markdown format
4. Saves to your specified directory
5. Skips files that already exist

All processing is done locally. No data is sent anywhere.

## Credits

This script was created to work alongside the [Granola MCP Server](https://github.com/proofgeist/granola-ai-mcp-server) by [@proofgeist](https://github.com/proofgeist). The MCP server integrates Granola with Claude Desktop for real-time meeting queries. This backup script is a standalone utility that solves the transcript expiration problem.

## License

MIT License - Feel free to use, modify, and share!

## Contributing

Found a bug? Have a feature request? Open an issue or submit a PR!

## Support

If you find this useful, give it a ⭐️ on GitHub!
