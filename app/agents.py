AGENTS=[
 {'id':'ceo','name':'CEO（あなた）','role':'承認・意思決定・全体統括','room':'ceo','provider':'openai','sprite':'ceo','seat':[16,18],'capacity':100,'mission':'全社員から重要結果を受け取り意思決定する'},
 {'id':'secretary','name':'秘書AI','role':'Gmail・Calendar・重要通知・未返信監視','room':'secretary','provider':'openai','sprite':'secretary','seat':[39,18],'capacity':100,'mission':'メール・予定・請求・重要連絡を監視しCEOへ報告'},
 {'id':'planning','name':'経営企画AI','role':'KPI・競合・新規事業分析','room':'planning','provider':'claude','sprite':'planning','seat':[65,18],'capacity':100,'mission':'経営判断に必要な分析をCEOへ報告'},
 {'id':'sales','name':'営業AI','role':'提案・追客・商談・会議準備','room':'sales','provider':'openai','sprite':'sales','seat':[87,20],'capacity':100,'mission':'Calendarから営業予定を確認し、提案・定例資料・不足情報を報告'},
 {'id':'accounting','name':'経理AI','role':'請求書・支払期限・入出金','room':'accounting','provider':'openai','sprite':'accounting','seat':[15,61],'capacity':100,'mission':'請求・支払・期限を監視し遅延リスクをCEOへ報告'},
 {'id':'hr','name':'人事AI','role':'採用・面談・人員管理','room':'meeting','provider':'openai','sprite':'hr','seat':[40,61],'capacity':100,'mission':'採用・人員・面談を管理'},
 {'id':'webprod','name':'Web制作AI','role':'Claude Code・GPT・Google AI・ローカル案件監視','room':'development','provider':'claude','sprite':'engineer','seat':[66,61],'capacity':100,'mission':'制作案件の稼働・完了・期限・ログをCEOへ報告'},
 {'id':'webmarketing','name':'WebマーケAI','role':'GA・広告・CV監視','room':'marketing','provider':'openai','sprite':'marketing','seat':[87,61],'capacity':100,'mission':'通常PVではなくCVと意味のあるコンバージョンだけをCEOへ報告'},
 {'id':'playboy','name':'遊び人AI','role':'X・note監視・話題発掘','room':'lounge','provider':'openai','sprite':'sales','seat':[76,82],'capacity':100,'mission':'Xとnoteを監視しトレンド・反応・バズ候補をCEOへ報告'},
]
BY_ID={a['id']:a for a in AGENTS}
