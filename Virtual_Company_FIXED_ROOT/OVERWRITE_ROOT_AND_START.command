#!/bin/bash
set -e
SRC="$(cd "$(dirname "$0")" && pwd)"
TARGET="$HOME/Desktop/Virtual Company"

echo "=== Virtual Company 高ディテール版を正式ルートへ上書き ==="
mkdir -p "$TARGET"

# Stop any server bound to 8765
PIDS=$(lsof -ti tcp:8765 2>/dev/null || true)
if [ -n "$PIDS" ]; then
  echo "旧サーバーを停止: $PIDS"
  kill $PIDS 2>/dev/null || true
  sleep 1
fi

# Preserve local credentials and runtime data
mkdir -p "$TARGET/secrets" "$TARGET/data"
TMP="$(mktemp -d)"
[ -f "$TARGET/.env" ] && cp "$TARGET/.env" "$TMP/.env" || true
[ -d "$TARGET/secrets" ] && cp -R "$TARGET/secrets" "$TMP/secrets" || true
[ -d "$TARGET/data" ] && cp -R "$TARGET/data" "$TMP/data" || true

# Replace program files in root only
rm -rf "$TARGET/app" "$TARGET/web" "$TARGET/assets"
cp -R "$SRC/app" "$TARGET/app"
cp -R "$SRC/web" "$TARGET/web"
cp -R "$SRC/assets" "$TARGET/assets"
cp "$SRC/run.py" "$TARGET/run.py"
cp "$SRC/requirements.txt" "$TARGET/requirements.txt"
for f in terminal_start.sh terminal_google_setup.sh terminal_set_keys.sh terminal_diagnose.sh setup_google.py setup_google_account.py; do
  [ -f "$SRC/$f" ] && cp "$SRC/$f" "$TARGET/$f"
done

# Restore runtime data/config
[ -f "$TMP/.env" ] && cp "$TMP/.env" "$TARGET/.env" || true
[ -d "$TMP/secrets" ] && cp -R "$TMP/secrets/." "$TARGET/secrets/" || true
[ -d "$TMP/data" ] && cp -R "$TMP/data/." "$TARGET/data/" || true
rm -rf "$TMP"

cd "$TARGET"
chmod +x terminal_start.sh terminal_google_setup.sh terminal_set_keys.sh terminal_diagnose.sh 2>/dev/null || true

echo ""
echo "正式ルート: $TARGET"
echo "高ディテールCEO確認:"
ls -lh "$TARGET/assets/characters/ceo/idle.png"
echo ""
echo "起動します..."
./terminal_start.sh
