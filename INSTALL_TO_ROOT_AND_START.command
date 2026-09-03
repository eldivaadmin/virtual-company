#!/bin/bash
set -e
SRC="$(cd "$(dirname "$0")" && pwd)"
TARGET="$HOME/Desktop/Virtual Company"

mkdir -p "$TARGET"
echo "=== Virtual Company 正式フォルダへ更新 ==="
echo "$TARGET"

# Preserve local secrets/config/db while updating program files.
for item in app web assets run.py requirements.txt setup_google.py setup_google_account.py \
            terminal_start.sh terminal_google_setup.sh terminal_set_keys.sh terminal_diagnose.sh \
            start_mac.command setup_mac.command .env.example README.md FIRST_SETUP.md GOOGLE_ACCOUNTS.md; do
  if [ -e "$SRC/$item" ]; then
    rsync -a --delete "$SRC/$item" "$TARGET/"
  fi
done

mkdir -p "$TARGET/data" "$TARGET/secrets"
if [ -f "$SRC/secrets/google_accounts.json" ] && [ ! -f "$TARGET/secrets/google_accounts.json" ]; then
  cp "$SRC/secrets/google_accounts.json" "$TARGET/secrets/google_accounts.json"
fi

cd "$TARGET"
chmod +x terminal_start.sh terminal_google_setup.sh terminal_set_keys.sh terminal_diagnose.sh 2>/dev/null || true

echo ""
echo "以後の起動コマンドは永久にこれです:"
echo 'cd ~/Desktop/"Virtual Company" && ./terminal_start.sh'
echo ""
./terminal_start.sh
