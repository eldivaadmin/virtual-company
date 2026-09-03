#!/bin/bash
set -e
ROOT="$HOME/Desktop/Virtual Company"
cd "$ROOT"
mkdir -p secrets

if [ ! -f secrets/credentials.json ]; then
  CANDIDATE=$(find "$HOME/Downloads" -maxdepth 1 -type f \( -name 'client_secret*.json' -o -name 'credentials*.json' \) | head -n 1)
  if [ -z "$CANDIDATE" ]; then
    echo ""
    echo "Google OAuthのDesktopアプリ用JSONが見つかりません。"
    echo "Google Cloud ConsoleでOAuth Client ID（Desktop app）を作成してJSONをDownloadsへ保存してください。"
    echo "必要API: Gmail API / Google Calendar API"
    echo ""
    exit 2
  fi
  cp "$CANDIDATE" secrets/credentials.json
  echo "OAuth JSONを自動検出: $CANDIDATE"
fi

source .venv/bin/activate
echo ""
echo "=== 1/3 Gmail: naoya.kizuka@gmail.com ==="
python setup_google_account.py "naoya.kizuka@gmail.com"
echo ""
echo "=== 2/3 Gmail: xnetwork.lab@gmail.com ==="
python setup_google_account.py "xnetwork.lab@gmail.com"
echo ""
echo "=== 3/3 Calendar: lamp.kizuka@gmail.com ==="
python setup_google_account.py "lamp.kizuka@gmail.com"

echo ""
echo "認証完了。サーバーを再起動します。"
PIDS=$(lsof -ti tcp:8765 2>/dev/null || true)
[ -n "$PIDS" ] && kill $PIDS 2>/dev/null || true
sleep 1
./terminal_start.sh
