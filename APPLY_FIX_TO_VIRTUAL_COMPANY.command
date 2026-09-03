#!/bin/bash
set -e
SRC="$(cd "$(dirname "$0")" && pwd)"
TARGET="$HOME/Desktop/Virtual Company"
PIDS=$(lsof -ti tcp:8765 2>/dev/null || true)
[ -n "$PIDS" ] && kill $PIDS 2>/dev/null || true
sleep 1

mkdir -p "$TARGET/app" "$TARGET/web" "$TARGET/assets" "$TARGET/secrets" "$TARGET/data"
cp -R "$SRC/app/." "$TARGET/app/"
cp -R "$SRC/web/." "$TARGET/web/"
cp -R "$SRC/assets/." "$TARGET/assets/"
cp "$SRC/CONNECT_GOOGLE_ACCOUNTS.command" "$TARGET/CONNECT_GOOGLE_ACCOUNTS.command"
for f in run.py requirements.txt terminal_start.sh setup_google_account.py; do
  [ -f "$SRC/$f" ] && cp "$SRC/$f" "$TARGET/$f"
done
cd "$TARGET"
chmod +x terminal_start.sh CONNECT_GOOGLE_ACCOUNTS.command
./terminal_start.sh
