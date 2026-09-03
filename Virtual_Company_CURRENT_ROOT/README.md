# AI COMPANY OS Local v1
完全ローカル起動の実働MVP。Web公開しません。サーバーは `127.0.0.1:8765` のみです。

## 起動
Mac: `start_mac.command` をダブルクリック。必要なら一度だけ `chmod +x start_mac.command`。
Windows: `start_windows.bat` をダブルクリック。

## GPT / Claude
`.env.example` を `.env` にコピーし、OpenAI / Anthropic APIキーを記入します。キーはブラウザ側には送られません。

## Gmail / Calendar
Google Cloudで Gmail API と Google Calendar API を有効化し、OAuthクライアントを「デスクトップアプリ」で作成。JSONを `secrets/credentials.json` として置き、`python setup_google.py` を実行。初回だけGoogle認証します。以後トークンは `secrets/token.json` にローカル保存されます。

## 実働
- Gmail 5分巡回（変更可）
- 名前判定による重要メール通知 (`IMPORTANT_NAME`)
- Calendar 24時間先確認
- AI社員へ実タスク指示
- 社員ごとにGPT/Claudeを既定割当
- SQLiteに履歴保存
- 重要イベント時に社員が社長エリアへ移動

## キャラクター
`assets/characters/` が正式スプライト置換先。現状は実働優先でCSSキャラ。生成した世界観画像 `assets/concept_v2.png` を背景に組み込んでいます。
