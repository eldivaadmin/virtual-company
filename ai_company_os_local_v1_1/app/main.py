from pathlib import Path
from fastapi import FastAPI,HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from apscheduler.schedulers.background import BackgroundScheduler
from .db import init_db,add_event,recent_events,create_task,finish_task,task_counts
from .agents import AGENTS,BY_ID
from .llm import route
from .google_services import authorize,upcoming_calendar
from .jobs import install_jobs,job_gmail,job_calendar
from . import config
BASE=Path(__file__).resolve().parent.parent
app=FastAPI(title='AI COMPANY OS Local')
scheduler=BackgroundScheduler()
class TaskIn(BaseModel):
    agent_id:str
    prompt:str
    provider:str|None=None
class SimIn(BaseModel):kind:str='mail'
@app.on_event('startup')
def startup():
    init_db();add_event('SYSTEM','boot','AI COMPANY OS 起動');install_jobs(scheduler);scheduler.start()
@app.on_event('shutdown')
def shutdown():
    if scheduler.running:scheduler.shutdown(wait=False)
@app.get('/api/status')
def status():return {'ok':True,'agents':len(AGENTS),'tasks':task_counts(),'openai':bool(config.OPENAI_API_KEY),'claude':bool(config.ANTHROPIC_API_KEY),'google_credentials':config.GOOGLE_CREDENTIALS.exists(),'google_authorized':config.GOOGLE_TOKEN.exists(),'gmail_poll_minutes':config.GMAIL_POLL_MINUTES}
@app.get('/api/agents')
def agents():return AGENTS
@app.get('/api/events')
def events(limit:int=80):return recent_events(limit)
@app.get('/api/calendar')
def calendar():return upcoming_calendar()
@app.post('/api/google/authorize')
def google_authorize():
    try:return {'ok':authorize()}
    except Exception as e:raise HTTPException(400,str(e))
@app.post('/api/check/gmail')
def check_gmail():job_gmail();return {'ok':True}
@app.post('/api/check/calendar')
def check_calendar():job_calendar();return {'ok':True}
@app.post('/api/task')
def task(body:TaskIn):
    a=BY_ID.get(body.agent_id)
    if not a:raise HTTPException(404,'agent not found')
    provider=body.provider or a['provider'];tid=create_task(a['name'],body.prompt,provider);add_event(a['name'],'task_start',body.prompt,{'task_id':tid,'provider':provider})
    system=f"あなたはAI COMPANY OSの{a['name']}です。担当は『{a['role']}』。社長向けに実務でそのまま使える成果物を日本語で返してください。事実と推測を分けてください。"
    try:
        result=route(provider,system,body.prompt);finish_task(tid,result);add_event(a['name'],'task_done',f'タスク完了: {body.prompt[:80]}',{'task_id':tid,'result':result,'provider':provider});return {'task_id':tid,'result':result,'provider':provider}
    except Exception as e:
        finish_task(tid,str(e),'error');add_event(a['name'],'error',str(e),{'task_id':tid});raise HTTPException(500,str(e))
@app.post('/api/simulate')
def simulate(body:SimIn):
    mapping={'mail':('秘書AI','mail_important','重要メールを検出しました'),'accounting':('経理AI','deadline','支払期限が近い請求を検出'),'meeting':('管理AI','meeting','会議30分前です')}
    return add_event(*mapping.get(body.kind,mapping['mail']))
app.mount('/assets',StaticFiles(directory=BASE/'assets'),name='assets')
app.mount('/static',StaticFiles(directory=BASE/'web'),name='static')
@app.get('/')
def index():return FileResponse(BASE/'web'/'index.html')
