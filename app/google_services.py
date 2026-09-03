from datetime import datetime,timedelta,timezone
from pathlib import Path
import re,json
from . import config
from .db import seen_mail,mark_mail,add_event,seen_calendar,mark_calendar
SCOPES=['https://www.googleapis.com/auth/gmail.readonly','https://www.googleapis.com/auth/calendar.readonly']
def safe(s):return re.sub(r'[^a-zA-Z0-9_.-]','_',s)
def token_path(email):return config.SECRETS_DIR/f'token_{safe(email)}.json'
def _creds(email,interactive=False):
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request
    from google_auth_oauthlib.flow import InstalledAppFlow
    tp=token_path(email);creds=None
    if tp.exists():creds=Credentials.from_authorized_user_file(str(tp),SCOPES)
    if creds and creds.expired and creds.refresh_token:creds.refresh(Request());tp.write_text(creds.to_json(),encoding='utf-8')
    if (not creds or not creds.valid) and interactive:
        if not config.GOOGLE_CREDENTIALS.exists():raise FileNotFoundError('secrets/credentials.json がありません')
        flow=InstalledAppFlow.from_client_secrets_file(str(config.GOOGLE_CREDENTIALS),SCOPES)
        creds=flow.run_local_server(port=0,prompt='select_account',login_hint=email)
        tp.write_text(creds.to_json(),encoding='utf-8')
    return creds if creds and creds.valid else None
def authorize_account(email):return bool(_creds(email,True))
def service(api,ver,email):
    c=_creds(email,False)
    if not c:return None
    from googleapiclient.discovery import build
    return build(api,ver,credentials=c,cache_discovery=False)
def account_status():
    a=config.google_accounts(); emails=list(a.get('mail',[]))+([a.get('calendar')] if a.get('calendar') else [])
    return {e:token_path(e).exists() for e in dict.fromkeys(emails)}
def _header(headers,name):
    for h in headers:
        if h.get('name','').lower()==name.lower():return h.get('value','')
    return ''
def _urgency(subject,sender,to,snippet,labels=None):
    text=(' '.join([subject or '',sender or '',to or '',snippet or ''])).lower()
    urgent_words=['至急','緊急','本日中','今日中','期限','支払','請求','督促','重要','urgent','asap','deadline','payment','invoice']
    high=sum(1 for w in urgent_words if w.lower() in text)
    named=bool(config.IMPORTANT_NAME and config.IMPORTANT_NAME.lower() in text)
    if high>=2 or (named and high>=1): return 'critical'
    if high>=1 or named: return 'high'
    return 'normal'

def poll_gmail():
    out=[]
    for email in config.google_accounts().get('mail',[]):
        svc=service('gmail','v1',email)
        if not svc:
            continue
        # INBOX only: do not treat Sent/Archive as a new incoming message.
        res=svc.users().messages().list(userId='me',q='in:inbox is:unread -in:spam -in:trash',maxResults=50).execute()
        for item in reversed(res.get('messages',[])):
            mid=item['id']; key=email+':'+mid
            if seen_mail(key):continue
            msg=svc.users().messages().get(userId='me',id=mid,format='metadata',
                metadataHeaders=['From','To','Cc','Subject','Date']).execute()
            hdr=msg.get('payload',{}).get('headers',[])
            subject=_header(hdr,'Subject'); sender=_header(hdr,'From'); to=_header(hdr,'To')
            cc=_header(hdr,'Cc'); date=_header(hdr,'Date'); snippet=msg.get('snippet','')
            labels=msg.get('labelIds',[])
            urgency=_urgency(subject,sender,to+' '+cc,snippet,labels)
            important=urgency in ('critical','high') or 'IMPORTANT' in labels
            payload={'account':email,'message_id':mid,'thread_id':msg.get('threadId'),
                'from':sender,'to':to,'cc':cc,'subject':subject,'date':date,'snippet':snippet,
                'labels':labels,'important':important,'urgency':urgency}
            kind='mail_critical' if urgency=='critical' else ('mail_important' if important else 'mail')
            prefix='🚨 ' if urgency=='critical' else ('⚠️ ' if important else '')
            add_event('秘書AI',kind,f'{prefix}[{email}] {subject or "(件名なし)"}',payload)
            mark_mail(key);out.append(payload)
    return out

def google_health():
    accounts=config.google_accounts()
    mail={}
    for email in accounts.get('mail',[]):
        c=_creds(email,False)
        mail[email]={'authorized':bool(c),'token':token_path(email).exists()}
    cal_email=accounts.get('calendar')
    c=_creds(cal_email,False) if cal_email else None
    return {'mail':mail,'calendar':{'email':cal_email,'authorized':bool(c),'token':token_path(cal_email).exists() if cal_email else False}}

def upcoming_calendar():
    email=config.google_accounts().get('calendar'); svc=service('calendar','v3',email) if email else None
    if not svc:return []
    now=datetime.now(timezone.utc);end=now+timedelta(days=7)
    res=svc.events().list(calendarId='primary',timeMin=now.isoformat(),timeMax=end.isoformat(),singleEvents=True,orderBy='startTime',maxResults=50).execute()
    return [{'account':email,'id':e.get('id'),'summary':e.get('summary','予定'),'start':e.get('start',{}).get('dateTime') or e.get('start',{}).get('date'),'end':e.get('end',{}).get('dateTime') or e.get('end',{}).get('date'),'location':e.get('location',''),'description':e.get('description',''),'htmlLink':e.get('htmlLink',''),'attendees':[x.get('email') for x in e.get('attendees',[]) if x.get('email')]} for e in res.get('items',[])]

def calendar_triggers():
    rows=upcoming_calendar();out=[]
    now=datetime.now(timezone.utc)
    for e in rows:
        s=e.get('start')
        if not s or 'T' not in s: continue
        try: dt=datetime.fromisoformat(s.replace('Z','+00:00'))
        except Exception: continue
        mins=(dt.astimezone(timezone.utc)-now).total_seconds()/60
        for threshold in (60,30,10):
            if 0 <= mins <= threshold:
                key=f"{e.get('id')}:{s}:{threshold}m"
                if not seen_calendar(key):
                    urgent='critical' if threshold==10 else ('high' if threshold==30 else 'normal')
                    payload=e|{'minutes_until':max(0,round(mins)),'urgency':urgent,'threshold':threshold}
                    kind='meeting_critical' if urgent=='critical' else 'meeting'
                    add_event('秘書AI',kind,f"{'🚨 ' if urgent=='critical' else ''}{e.get('summary','予定')} が約{max(0,round(mins))}分後です",payload)
                    mark_calendar(key);out.append(payload)
                break
    return out
