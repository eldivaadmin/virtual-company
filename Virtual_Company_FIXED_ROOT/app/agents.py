AGENTS=[
 {'id':'ceo','name':'CEO（あなた）','role':'承認・意思決定・全体統括','room':'ceo','provider':'openai','sprite':'ceo','seat':[16,18]},
 {'id':'secretary','name':'秘書AI','role':'Gmail・予定・重要通知','room':'secretary','provider':'openai','sprite':'secretary','seat':[39,18]},
 {'id':'planning','name':'経営企画AI','role':'KPI・競合・新規事業分析','room':'planning','provider':'claude','sprite':'planning','seat':[65,18]},
 {'id':'sales','name':'営業AI','role':'見込み客・提案・追客','room':'sales','provider':'openai','sprite':'sales','seat':[87,20]},
 {'id':'accounting','name':'経理AI','role':'請求書・支払期限・入出金','room':'accounting','provider':'openai','sprite':'accounting','seat':[15,61]},
 {'id':'hr','name':'人事AI','role':'採用・面談・人員管理','room':'meeting','provider':'openai','sprite':'hr','seat':[40,61]},
 {'id':'engineer','name':'エンジニアAI','role':'開発・自動化・障害対応','room':'development','provider':'claude','sprite':'engineer','seat':[66,61]},
 {'id':'marketing','name':'マーケAI','role':'SNS・広告・市場分析','room':'marketing','provider':'openai','sprite':'marketing','seat':[87,61]},
]
BY_ID={a['id']:a for a in AGENTS}
