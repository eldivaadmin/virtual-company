import sqlite3, json
from datetime import datetime
from .config import DB_PATH

def conn():
    c=sqlite3.connect(DB_PATH)
    c.row_factory=sqlite3.Row
    return c

def init_db():
    with conn() as c:
        c.executescript('''
        create table if not exists events(id integer primary key autoincrement, ts text not null, agent text not null, kind text not null, message text not null, payload text default '{}');
        create table if not exists tasks(id integer primary key autoincrement, created_at text not null, agent text not null, title text not null, status text not null default 'queued', provider text, result text default '');
        create table if not exists seen_mail(message_id text primary key, seen_at text not null);
        ''')

def add_event(agent,kind,message,payload=None):
    ts=datetime.now().isoformat(timespec='seconds')
    with conn() as c:
        c.execute('insert into events(ts,agent,kind,message,payload) values(?,?,?,?,?)',(ts,agent,kind,message,json.dumps(payload or {},ensure_ascii=False)))
    return {'ts':ts,'agent':agent,'kind':kind,'message':message,'payload':payload or {}}

def recent_events(limit=80):
    with conn() as c:
        rows=c.execute('select * from events order by id desc limit ?',(limit,)).fetchall()
    return [dict(r)|{'payload':json.loads(r['payload'] or '{}')} for r in rows]

def seen_mail(mid):
    with conn() as c:return c.execute('select 1 from seen_mail where message_id=?',(mid,)).fetchone() is not None

def mark_mail(mid):
    with conn() as c:c.execute('insert or ignore into seen_mail(message_id,seen_at) values(?,?)',(mid,datetime.now().isoformat(timespec='seconds')))

def create_task(agent,title,provider='auto'):
    with conn() as c:
        cur=c.execute('insert into tasks(created_at,agent,title,status,provider) values(?,?,?,?,?)',(datetime.now().isoformat(timespec='seconds'),agent,title,'queued',provider))
        return cur.lastrowid

def finish_task(task_id,result,status='done'):
    with conn() as c:c.execute('update tasks set result=?,status=? where id=?',(result,status,task_id))

def task_counts():
    with conn() as c:rows=c.execute('select status,count(*) n from tasks group by status').fetchall()
    return {r['status']:r['n'] for r in rows}
