#!/bin/bash
# Install Granola backup script to run daily at 11 PM

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PLIST_FILE="com.granola.backup.plist"
PLIST_DEST="$HOME/Library/LaunchAgents/$PLIST_FILE"
WRAPPER_SCRIPT="$SCRIPT_DIR/run_backup.sh"

echo "Installing Granola daily backup..."
echo ""

# Create LaunchAgents directory if it doesn't exist
mkdir -p "$HOME/Library/LaunchAgents"

# Create wrapper script for launchd (needed for macOS permissions)
cat > "$WRAPPER_SCRIPT" <<'WRAPPER_EOF'
#!/bin/bash
# Wrapper script for Granola backup - allows launchd to run with proper permissions
# This script needs Full Disk Access permission via /bin/bash
WRAPPER_EOF

echo "cd \"$SCRIPT_DIR\"" >> "$WRAPPER_SCRIPT"
echo "/usr/bin/python3 backup_transcripts.py" >> "$WRAPPER_SCRIPT"

chmod +x "$WRAPPER_SCRIPT"
echo "✓ Created run_backup.sh wrapper script"

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
        <string>$WRAPPER_SCRIPT</string>
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
echo "⚠️  IMPORTANT: Grant Full Disk Access to /bin/bash"
echo ""
echo "Due to macOS privacy protections, you need to grant Full Disk Access:"
echo "  1. Open System Settings → Privacy & Security → Full Disk Access"
echo "  2. Click the '+' button"
echo "  3. Press Command+Shift+G and enter: /bin/bash"
echo "  4. Select 'bash' and click Open"
echo "  5. Enable the toggle next to 'bash'"
echo ""
echo "Without this, the backup will fail with 'Operation not permitted' errors."
echo ""
echo "The backup script will run automatically every day at 11:00 PM."
echo ""
echo "Useful commands:"
echo "  • Test now:         launchctl start com.granola.backup"
echo "  • View output log:  tail -f \"$SCRIPT_DIR/backup.log\""
echo "  • View error log:   tail -f \"$SCRIPT_DIR/backup.error.log\""
echo "  • Uninstall:        launchctl unload ~/Library/LaunchAgents/$PLIST_FILE && rm ~/Library/LaunchAgents/$PLIST_FILE"
echo ""
