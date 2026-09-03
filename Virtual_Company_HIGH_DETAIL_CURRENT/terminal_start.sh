#!/bin/bash
set -e
cd "$(dirname "$0")"

echo "=================================================="
echo " AI COMPANY OS - LOCAL START"
echo "=================================================="

echo "[1/6] Python確認"
if ! command -v python3 >/dev/null 2>&1; then
  echo "ERROR: python3 がありません。Macなら先に Homebrew または Python 3 を入れてください。"
  exit 1
fi
python3 --version

echo "[2/6] 仮想環境"
if [ ! -d .venv ]; then
  python3 -m venv .venv
fi
source .venv/bin/activate

echo "[3/6] ライブラリ確認/インストール"
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

echo "[4/6] .env確認"
if [ ! -f .env ]; then
  cp .env.example .env
  echo "初回用 .env を作成しました。APIキーなしでも画面は起動します。"
fi

echo "[5/6] ポート8765確認"
if lsof -iTCP:8765 -sTCP:LISTEN >/dev/null 2>&1; then
  echo "既に8765番ポートが使われています。既存AI COMPANY OSの可能性があります。"
  lsof -iTCP:8765 -sTCP:LISTEN || true
  echo "ブラウザを開きます。"
  open http://127.0.0.1:8765
  exit 0
fi

echo "[6/6] サーバー起動"
echo "このターミナルは閉じないでください。停止は Control+C"
(sleep 2; open http://127.0.0.1:8765) &
exec python run.py
