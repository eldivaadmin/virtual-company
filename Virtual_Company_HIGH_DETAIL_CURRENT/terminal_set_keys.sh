#!/bin/bash
set -e
cd "$(dirname "$0")"
[ -f .env ] || cp .env.example .env
printf "OpenAI API Key（未設定ならEnter）: "
read -r OPENAI_KEY
printf "Anthropic API Key（未設定ならEnter）: "
read -r ANTHROPIC_KEY
printf "あなたのメール判定用の名前（例: Naoya、未設定ならEnter）: "
read -r IMPORTANT_NAME
python3 - "$OPENAI_KEY" "$ANTHROPIC_KEY" "$IMPORTANT_NAME" <<'PY2'
from pathlib import Path
import sys
p=Path('.env')
lines=p.read_text(encoding='utf-8').splitlines()
vals={'OPENAI_API_KEY':sys.argv[1],'ANTHROPIC_API_KEY':sys.argv[2],'IMPORTANT_NAME':sys.argv[3]}
out=[]
seen=set()
for line in lines:
    if '=' in line and not line.lstrip().startswith('#'):
        k=line.split('=',1)[0]
        if k in vals:
            out.append(f'{k}={vals[k]}'); seen.add(k); continue
    out.append(line)
for k,v in vals.items():
    if k not in seen: out.append(f'{k}={v}')
p.write_text('\n'.join(out)+'\n',encoding='utf-8')
PY2
echo ".env を更新しました。APIキーはローカルファイルにのみ保存されます。"
