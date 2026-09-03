import sqlite3,json
from datetime import datetime
from .config import DB_PATH
def conn():
 c=sqlite3.connect(DB_PATH);c.row_factory=sqlite3.Row;return c
def init_db():
 with conn() as c:c.executescript('''
 create table if not exists events(id integer primary key autoincrement,ts text not null,agent text not null,kind text not null,message text not null,payload text default '{}');
 create table if not exists tasks(id integer primary key autoincrement,created_at text not null,agent text not null,title text not null,status text not null default 'queued',provider text,result text default '');
 create table if not exists seen_mail(message_id text primary key,seen_at text not null);
 create table if not exists presence(agent_id text primary key,state text not null,updated_at text not null);
 create table if not exists seen_calendar(event_key text primary key,seen_at text not null);
 create table if not exists ceo_inbox(id integer primary key autoincrement,ts text not null,agent text not null,title text not null,body text not null,severity text not null default 'info',read integer not null default 0);
 create table if not exists agent_runtime(agent_id text primary key,load integer not null default 0,stamina integer not null default 100,updated_at text not null);''')
def add_event(agent,kind,message,payload=None):
 ts=datetime.now().isoformat(timespec='seconds')
 with conn() as c:c.execute('insert into events(ts,agent,kind,message,payload) values(?,?,?,?,?)',(ts,agent,kind,message,json.dumps(payload or {},ensure_ascii=False)))
 return {'ts':ts,'agent':agent,'kind':kind,'message':message,'payload':payload or {}}
def recent_events(limit=80):
 with conn() as c:rows=c.execute('select * from events order by id desc limit ?',(limit,)).fetchall()
 return [dict(r)|{'payload':json.loads(r['payload'] or '{}')} for r in rows]
def seen_mail(mid):
 with conn() as c:return c.execute('select 1 from seen_mail where message_id=?',(mid,)).fetchone() is not None
def mark_mail(mid):
 with conn() as c:c.execute('insert or ignore into seen_mail(message_id,seen_at) values(?,?)',(mid,datetime.now().isoformat(timespec='seconds')))
def create_task(agent,title,provider='auto'):
 with conn() as c:return c.execute('insert into tasks(created_at,agent,title,status,provider) values(?,?,?,?,?)',(datetime.now().isoformat(timespec='seconds'),agent,title,'queued',provider)).lastrowid
def finish_task(task_id,result,status='done'):
 with conn() as c:c.execute('update tasks set result=?,status=? where id=?',(result,status,task_id))
def task_counts():
 with conn() as c:rows=c.execute('select status,count(*) n from tasks group by status').fetchall()
 return {r['status']:r['n'] for r in rows}
def set_presence(agent_id,state):
 ts=datetime.now().isoformat(timespec='seconds')
 with conn() as c:c.execute('insert into presence(agent_id,state,updated_at) values(?,?,?) on conflict(agent_id) do update set state=excluded.state,updated_at=excluded.updated_at',(agent_id,state,ts))
 return {'agent_id':agent_id,'state':state,'updated_at':ts}
def get_presence():
 with conn() as c:rows=c.execute('select agent_id,state,updated_at from presence').fetchall()
 return {r['agent_id']:{'state':r['state'],'updated_at':r['updated_at']} for r in rows}
def seen_calendar(key):
 with conn() as c:return c.execute('select 1 from seen_calendar where event_key=?',(key,)).fetchone() is not None
def mark_calendar(key):
 with conn() as c:c.execute('insert or ignore into seen_calendar(event_key,seen_at) values(?,?)',(key,datetime.now().isoformat(timespec='seconds')))
def recent_real_events(limit=50):return recent_events(limit)
def ceo_report(agent,title,body,severity='info'):
 ts=datetime.now().isoformat(timespec='seconds')
 with conn() as c:c.execute('insert into ceo_inbox(ts,agent,title,body,severity,read) values(?,?,?,?,?,0)',(ts,agent,title,body,severity))
 return {'ts':ts,'agent':agent,'title':title,'body':body,'severity':severity}
def ceo_inbox(limit=30):
 with conn() as c:rows=c.execute('select * from ceo_inbox order by id desc limit ?',(limit,)).fetchall()
 return [dict(r) for r in rows]
def set_agent_load(agent_id,load=None,stamina=None):
 ts=datetime.now().isoformat(timespec='seconds')
 with conn() as c:
  old=c.execute('select load,stamina from agent_runtime where agent_id=?',(agent_id,)).fetchone();load=max(0,min(100,int(load if load is not None else (old['load'] if old else 0))));stamina=max(0,min(100,int(stamina if stamina is not None else (old['stamina'] if old else 100))));c.execute('insert into agent_runtime(agent_id,load,stamina,updated_at) values(?,?,?,?) on conflict(agent_id) do update set load=excluded.load,stamina=excluded.stamina,updated_at=excluded.updated_at',(agent_id,load,stamina,ts))
 return {'agent_id':agent_id,'load':load,'stamina':stamina,'updated_at':ts}
def agent_loads():
 with conn() as c:rows=c.execute('select agent_id,load,stamina,updated_at from agent_runtime').fetchall()
 return {r['agent_id']:dict(r) for r in rows}
