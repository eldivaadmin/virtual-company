#!/bin/bash
set -e
cd "$(dirname "$0")"
if [ ! -f secrets/credentials.json ]; then
  echo "ERROR: secrets/credentials.json がありません。Google CloudのDesktop OAuth JSONをここへ置いてください。"
  exit 1
fi
source .venv/bin/activate 2>/dev/null || true
for EMAIL in "naoya.kizuka@gmail.com" "xnetwork.lab@gmail.com" "lamp.kizuka@gmail.com"; do
  echo "=================================================="
  echo "$EMAIL を認証します"
  python setup_google_account.py "$EMAIL"
done
echo "3アカウント認証完了。サーバーを再起動してください。"
