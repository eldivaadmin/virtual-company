#!/bin/bash
set -e
SRC="$(cd "$(dirname "$0")" && pwd)"
TARGET="$HOME/Desktop/Virtual Company"
mkdir -p "$TARGET"
echo "Virtual Company v2 を上書きします: $TARGET"
rsync -a --delete --exclude '.env' --exclude 'secrets/tokens' "$SRC/" "$TARGET/"
cd "$TARGET"
chmod +x terminal_start.sh terminal_google_setup.sh 2>/dev/null || true
echo "上書き完了。起動します..."
./terminal_start.sh
