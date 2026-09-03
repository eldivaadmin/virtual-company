AGENTS=[
 {'id':'secretary','name':'秘書AI','role':'Gmail・予定・重要通知','room':'mail','provider':'openai','color':'pink'},
 {'id':'planning','name':'経営企画AI','role':'KPI・競合・新規事業分析','room':'planning','provider':'claude','color':'black'},
 {'id':'accounting','name':'経理AI','role':'請求書・支払期限・入出金','room':'accounting','provider':'openai','color':'teal'},
 {'id':'legal','name':'法務AI','role':'契約書・更新期限・リスク確認','room':'legal','provider':'claude','color':'green'},
 {'id':'sales','name':'営業AI','role':'見込み客・提案・追客','room':'sales','provider':'openai','color':'black'},
 {'id':'research','name':'リサーチAI','role':'企業・人物・市場調査','room':'research','provider':'openai','color':'red'},
 {'id':'affiliate','name':'Affiliate AI','role':'SEO・順位・案件・収益','room':'affiliate','provider':'openai','color':'gold'},
 {'id':'content','name':'コンテンツAI','role':'記事・構成・原稿制作','room':'content','provider':'claude','color':'pink'},
 {'id':'ai','name':'AI研究員','role':'新モデル・AIツール研究','room':'ai','provider':'openai','color':'white'},
 {'id':'web','name':'WebディレクターAI','role':'サイト改善・アクセス分析','room':'web','provider':'claude','color':'purple'},
 {'id':'pm','name':'管理AI','role':'案件進捗・遅延・優先順位','room':'lobby','provider':'openai','color':'blue'},
 {'id':'health','name':'健康管理AI','role':'水分・運動・プロテイン','room':'lobby','provider':'openai','color':'green'},
]
BY_ID={a['id']:a for a in AGENTS}
