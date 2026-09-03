# 最初に1回だけ必要なこと（Mac）

1. `setup_mac.command` をダブルクリック。
2. OpenAI API Key / Anthropic API Key を入力（使わない方は空欄可）。
3. Gmail/Calendarも使う場合だけ、Google Cloudで **Desktop app OAuth** を1個作り、JSONを `secrets/credentials.json` として置く。
4. その後 `python setup_google.py` または `setup_mac.command` を再実行し、ブラウザでGoogle権限を許可。
5. 以後は `start_mac.command` だけで起動。

## 重要
APIキーとGoogleトークンはこのPCのフォルダ内だけに保存され、ブラウザJavaScriptには埋め込みません。
サーバーは `127.0.0.1:8765` のみで待受するため、外部公開しません。
