#!/bin/bash
set -e
SRC="$(cd "$(dirname "$0")" && pwd)"
TARGET="$HOME/Desktop/Virtual Company"
mkdir -p "$TARGET"
echo "高ディテールキャラ版を Virtual Company 直下へ上書きします..."
rsync -a --delete \
  --exclude '.env' \
  --exclude 'secrets/tokens' \
  --exclude 'ai_company_os_local_v1_1' \
  --exclude 'Virtual_Company_v1_2' \
  --exclude 'Virtual_Company_v2' \
  "$SRC/" "$TARGET/"
cd "$TARGET"
chmod +x terminal_start.sh 2>/dev/null || true
echo "上書き完了: $TARGET"
echo "起動します..."
./terminal_start.sh
