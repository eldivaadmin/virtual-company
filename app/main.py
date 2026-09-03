from pathlib import Path
import json
from fastapi import FastAPI,HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from apscheduler.schedulers.background import BackgroundScheduler
from .db import init_db,add_event,recent_events,create_task,finish_task,task_counts,set_presence,get_presence,ceo_report,ceo_inbox,set_agent_load,agent_loads
from .agents import AGENTS,BY_ID
from .llm import route
from .google_services import authorize_account,upcoming_calendar,account_status,google_health,unreplied_threads
from .jobs import install_jobs,job_gmail,job_calendar
from . import config
BASE=Path(__file__).resolve().parent.parent
app=FastAPI(title='AI COMPANY OS Local');scheduler=BackgroundScheduler()
class TaskIn(BaseModel):agent_id:str;prompt:str;provider:str|None=None
class SimIn(BaseModel):kind:str='mail'
class GoogleCredsIn(BaseModel):content:str
class PresenceIn(BaseModel):agent_id:str;state:str='present'
@app.on_event('startup')
def startup():init_db();add_event('SYSTEM','boot','AI COMPANY OS 起動');install_jobs(scheduler);scheduler.start()
@app.on_event('shutdown')
def shutdown():
 if scheduler.running:scheduler.shutdown(wait=False)
@app.get('/api/build')
def build():return {'build':'DASHBOARD-RIG-20260903-1630','root':str(BASE)}
@app.get('/api/status')
def status():return {'ok':True,'agents':len(AGENTS),'tasks':task_counts(),'openai':bool(config.OPENAI_API_KEY),'claude':bool(config.ANTHROPIC_API_KEY),'gemini':bool(getattr(config,'GOOGLE_API_KEY','')),'google_credentials':config.GOOGLE_CREDENTIALS.exists(),'google_accounts':config.google_accounts(),'google_status':account_status()}
@app.get('/api/agents')
def agents():
 p=get_presence();return [a|{'presence':p.get(a['id'],{'state':'present'})} for a in AGENTS]
@app.get('/api/events')
def events(limit:int=80):return recent_events(limit)
@app.get('/api/calendar')
def calendar():return upcoming_calendar()
@app.get('/api/google/health')
def google_health_api():return google_health()
@app.get('/api/resources')
def resources():
 current=agent_loads();return {a['id']:current.get(a['id'],{'agent_id':a['id'],'load':0,'stamina':100}) for a in AGENTS}
@app.get('/api/ceo/inbox')
def ceo_inbox_api(limit:int=30):return ceo_inbox(limit)
@app.get('/api/social')
def social_api(force:bool=False):
 from .social_stats import social_stats
 return social_stats(force)
@app.get('/api/mail/unreplied')
def mail_unreplied(limit:int=30,days:int=14):return unreplied_threads(max_results=max(10,min(limit,100)),days=max(1,min(days,90)))
@app.post('/api/google/credentials')
def save_google_credentials(body:GoogleCredsIn):
 try:
  data=json.loads(body.content)
  if not isinstance(data,dict) or not ('installed' in data or 'web' in data):raise ValueError('OAuth client JSONではありません')
  config.SECRETS_DIR.mkdir(parents=True,exist_ok=True);config.GOOGLE_CREDENTIALS.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8');return {'ok':True}
 except Exception as e:raise HTTPException(400,f'credentials.json: {e}')
_google_auth_state={}
@app.post('/api/google/connect/{email}')
def connect_google(email:str):
 allowed=set(config.google_accounts().get('mail',[]));cal=config.google_accounts().get('calendar')
 if cal:allowed.add(cal)
 if email not in allowed:raise HTTPException(400,'許可されていないアカウントです')
 if not config.GOOGLE_CREDENTIALS.exists():raise HTTPException(400,'先にGoogle OAuth JSONを登録してください')
 import threading
 _google_auth_state[email]='starting'
 def worker():
  try:_google_auth_state[email]='connected' if authorize_account(email) else 'failed'
  except Exception as e:_google_auth_state[email]='error: '+str(e)
 threading.Thread(target=worker,daemon=True).start();return {'ok':True,'status':'starting'}
@app.get('/api/google/connect-status')
def google_connect_status():return _google_auth_state
@app.get('/api/mail/summary')
def mail_summary():
 from .google_services import service
 result={}
 for email in config.google_accounts().get('mail',[]):
  svc=service('gmail','v1',email)
  if not svc:result[email]={'connected':False,'unread':None,'important_unread':None};continue
  q1=svc.users().messages().list(userId='me',q='in:inbox is:unread -in:spam -in:trash',maxResults=1).execute();q2=svc.users().messages().list(userId='me',q='in:inbox is:unread is:important -in:spam -in:trash',maxResults=1).execute();result[email]={'connected':True,'unread':q1.get('resultSizeEstimate',0),'important_unread':q2.get('resultSizeEstimate',0)}
 return result
@app.post('/api/check/gmail')
def check_gmail():job_gmail();return {'ok':True}
@app.post('/api/check/calendar')
def check_calendar():job_calendar();return {'ok':True}
@app.post('/api/task')
def task(body:TaskIn):
 a=BY_ID.get(body.agent_id)
 if not a:raise HTTPException(404,'agent not found')
 provider=body.provider or a['provider'];tid=create_task(a['name'],body.prompt,provider);set_agent_load(a['id'],85,80);add_event(a['name'],'task_start',body.prompt,{'task_id':tid,'provider':provider});system=f"あなたはAI COMPANY OSの{a['name']}です。担当は『{a['role']}』。使命は『{a.get('mission','')}』。社長向けに実務でそのまま使える成果物を日本語で返してください。事実と推測を分けてください。"
 try:
  result=route(provider,system,body.prompt);finish_task(tid,result);set_agent_load(a['id'],10,76);add_event(a['name'],'task_done',f'タスク完了: {body.prompt[:80]}',{'task_id':tid,'result':result,'provider':provider});ceo_report(a['name'],'タスク完了',result[:1200]);return {'task_id':tid,'result':result,'provider':provider}
 except Exception as e:
  finish_task(tid,str(e),'error');set_agent_load(a['id'],0,70);add_event(a['name'],'error',str(e),{'task_id':tid});ceo_report(a['name'],'タスクエラー',str(e),'error');raise HTTPException(500,str(e))
@app.post('/api/presence')
def presence(body:PresenceIn):
 a=BY_ID.get(body.agent_id)
 if not a:raise HTTPException(404,'agent not found')
 labels={'present':'在席','away':'離席','out':'外出','meeting':'会議中','working':'作業中'};set_presence(body.agent_id,body.state);add_event(a['name'],'presence',labels.get(body.state,body.state),{'agent_id':body.agent_id,'state':body.state});return {'ok':True,'agent_id':body.agent_id,'state':body.state}
@app.post('/api/simulate')
def simulate(body:SimIn):
 mapping={'mail':('秘書AI','mail_important','重要メールを検出しました'),'accounting':('経理AI','deadline','支払期限が近い請求を検出'),'meeting':('秘書AI','meeting','会議30分前です')};return add_event(*mapping.get(body.kind,mapping['mail']))
app.mount('/assets',StaticFiles(directory=BASE/'assets'),name='assets');app.mount('/static',StaticFiles(directory=BASE/'web'),name='static')
@app.get('/google-setup')
def google_setup_page():return FileResponse(BASE/'web'/'google_setup.html',headers={'Cache-Control':'no-store'})
@app.get('/')
def index():return FileResponse(BASE/'web'/'index.html',headers={'Cache-Control':'no-store, no-cache, must-revalidate, max-age=0'})
