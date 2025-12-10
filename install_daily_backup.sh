#!/bin/bash
# Install Granola backup script to run daily at 11 PM

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PLIST_FILE="com.granola.backup.plist"
PLIST_DEST="$HOME/Library/LaunchAgents/$PLIST_FILE"

echo "Installing Granola daily backup..."
echo ""

# Create LaunchAgents directory if it doesn't exist
mkdir -p "$HOME/Library/LaunchAgents"

# Create plist file
cat > "$PLIST_DEST" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.granola.backup</string>

    <key>ProgramArguments</key>
    <array>
        <string>/usr/bin/python3</string>
        <string>$SCRIPT_DIR/backup_transcripts.py</string>
    </array>

    <key>StartCalendarInterval</key>
    <dict>
        <key>Hour</key>
        <integer>23</integer>
        <key>Minute</key>
        <integer>0</integer>
    </dict>

    <key>StandardOutPath</key>
    <string>$SCRIPT_DIR/backup.log</string>

    <key>StandardErrorPath</key>
    <string>$SCRIPT_DIR/backup.error.log</string>

    <key>RunAtLoad</key>
    <false/>

    <key>KeepAlive</key>
    <false/>
</dict>
</plist>
EOF

echo "✓ Created $PLIST_FILE in ~/Library/LaunchAgents/"

# Load the plist
launchctl unload "$PLIST_DEST" 2>/dev/null  # Unload if already loaded
launchctl load "$PLIST_DEST"
echo "✓ Loaded launch agent"

echo ""
echo "Installation complete!"
echo ""
echo "The backup script will now run automatically every day at 11:00 PM."
echo ""
echo "Useful commands:"
echo "  • Test now:         launchctl start com.granola.backup"
echo "  • View output log:  tail -f \"$SCRIPT_DIR/backup.log\""
echo "  • View error log:   tail -f \"$SCRIPT_DIR/backup.error.log\""
echo "  • Uninstall:        launchctl unload ~/Library/LaunchAgents/$PLIST_FILE && rm ~/Library/LaunchAgents/$PLIST_FILE"
echo ""
