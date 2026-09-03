#!/bin/bash
set -e
cd "$(dirname "$0")"
echo "=== AI COMPANY OS 初期設定 ==="
if [ ! -d .venv ]; then python3 -m venv .venv; fi
source .venv/bin/activate
pip install -r requirements.txt
read -s -p "OpenAI API Key（未使用ならEnter）: " OPENAI_KEY; echo
read -s -p "Anthropic API Key（未使用ならEnter）: " ANTHROPIC_KEY; echo
read -p "重要メール判定に使う自分の名前（例: Naoya / 木塚、空欄可）: " IMPORTANT_NAME
cat > .env <<EOF
OPENAI_API_KEY=$OPENAI_KEY
ANTHROPIC_API_KEY=$ANTHROPIC_KEY
OPENAI_MODEL=gpt-5
ANTHROPIC_MODEL=claude-sonnet-5
GMAIL_POLL_MINUTES=5
CALENDAR_POLL_MINUTES=5
IMPORTANT_NAME=$IMPORTANT_NAME
EOF
echo
echo "AIキー設定を保存しました: .env"
if [ -f secrets/credentials.json ]; then
  echo "Google OAuthを開始します。"
  python setup_google.py || true
else
  echo "Google連携は未設定です。Google CloudからDesktop OAuth JSONを取得後、secrets/credentials.json に置いてください。"
fi
echo "初期設定完了。次回から start_mac.command をダブルクリックしてください。"
read -p "Enterで終了"
