#!/bin/bash
set -e
SRC="$(cd "$(dirname "$0")" && pwd)"
TARGET="$HOME/Desktop/Virtual Company"

echo "Virtual Companyへ完全FIXを上書きします..."
PIDS=$(lsof -ti tcp:8765 2>/dev/null || true)
[ -n "$PIDS" ] && kill $PIDS 2>/dev/null || true
sleep 1

mkdir -p "$TARGET/app" "$TARGET/web" "$TARGET/assets" "$TARGET/secrets" "$TARGET/data"

# Program/assets only. User tokens, .env and database remain.
rm -rf "$TARGET/app" "$TARGET/web" "$TARGET/assets/characters_hd2"
cp -R "$SRC/app" "$TARGET/app"
cp -R "$SRC/web" "$TARGET/web"
mkdir -p "$TARGET/assets"
cp -R "$SRC/assets/characters_hd2" "$TARGET/assets/characters_hd2"
[ -d "$SRC/assets/office" ] && { rm -rf "$TARGET/assets/office"; cp -R "$SRC/assets/office" "$TARGET/assets/office"; }

for f in run.py requirements.txt terminal_start.sh .env.example setup_google_account.py; do
  [ -f "$SRC/$f" ] && cp "$SRC/$f" "$TARGET/$f"
done

cd "$TARGET"
[ -f .env.example ] || printf 'OPENAI_API_KEY=\nANTHROPIC_API_KEY=\nUSER_DISPLAY_NAME=\n' > .env.example
[ -f .env ] || cp .env.example .env
chmod +x terminal_start.sh

echo "起動します..."
./terminal_start.sh
