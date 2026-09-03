from datetime import datetime,timedelta,timezone
import re
from . import config
from .db import seen_mail,mark_mail,add_event,seen_calendar,mark_calendar,ceo_report

SCOPES=['https://www.googleapis.com/auth/gmail.readonly','https://www.googleapis.com/auth/calendar.readonly']

def safe(s):return re.sub(r'[^a-zA-Z0-9_.-]','_',s)
def token_path(email):return config.SECRETS_DIR/f'token_{safe(email)}.json'

def _creds(email,interactive=False):
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request
    from google_auth_oauthlib.flow import InstalledAppFlow
    tp=token_path(email);creds=None
    if tp.exists():creds=Credentials.from_authorized_user_file(str(tp),SCOPES)
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request());tp.write_text(creds.to_json(),encoding='utf-8')
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
    urgent_words=['至急','緊急','本日中','今日中','期限','支払','請求','督促','重要','urgent','asap','deadline','payment','invoice','打ち合わせ','商談']
    high=sum(1 for w in urgent_words if w.lower() in text)
    named=bool(config.IMPORTANT_NAME and config.IMPORTANT_NAME.lower() in text)
    if high>=2 or (named and high>=1):return 'critical'
    if high>=1 or named:return 'high'
    return 'normal'

def poll_gmail():
    out=[]
    for email in config.google_accounts().get('mail',[]):
        svc=service('gmail','v1',email)
        if not svc:continue
        res=svc.users().messages().list(userId='me',q='in:inbox is:unread -in:spam -in:trash',maxResults=50).execute()
        for item in reversed(res.get('messages',[])):
            mid=item['id'];key=email+':'+mid
            if seen_mail(key):continue
            msg=svc.users().messages().get(userId='me',id=mid,format='metadata',metadataHeaders=['From','To','Cc','Subject','Date']).execute()
            hdr=msg.get('payload',{}).get('headers',[]);subject=_header(hdr,'Subject');sender=_header(hdr,'From');to=_header(hdr,'To');cc=_header(hdr,'Cc');date=_header(hdr,'Date');snippet=msg.get('snippet','');labels=msg.get('labelIds',[])
            urgency=_urgency(subject,sender,to+' '+cc,snippet,labels);important=urgency in ('critical','high') or 'IMPORTANT' in labels
            payload={'account':email,'message_id':mid,'thread_id':msg.get('threadId'),'from':sender,'to':to,'cc':cc,'subject':subject,'date':date,'snippet':snippet,'labels':labels,'important':important,'urgency':urgency}
            kind='mail_critical' if urgency=='critical' else ('mail_important' if important else 'mail');prefix='🚨 ' if urgency=='critical' else ('⚠️ ' if important else '')
            add_event('秘書AI',kind,f'{prefix}[{email}] {subject or "(件名なし)"}',payload)
            if important:ceo_report('秘書AI','重要メール',f'[{email}] {subject}\nFrom: {sender}\n{snippet[:500]}',urgency)
            mark_mail(key);out.append(payload)
    return out

def unreplied_threads(max_results=30,days=14):
    """Likely unreplied conversations: latest message in an inbox thread is inbound and not automated."""
    out=[]
    auto_words=('no-reply','noreply','do-not-reply','mailer-daemon','notification@','support@em.','news@','newsletter')
    for email in config.google_accounts().get('mail',[]):
        svc=service('gmail','v1',email)
        if not svc:continue
        q=f'in:inbox newer_than:{max(1,int(days))}d -in:spam -in:trash'
        res=svc.users().messages().list(userId='me',q=q,maxResults=max_results).execute()
        seen_threads=set()
        for item in res.get('messages',[]):
            msg=svc.users().messages().get(userId='me',id=item['id'],format='metadata',metadataHeaders=['From','Subject','Date']).execute();tid=msg.get('threadId')
            if not tid or tid in seen_threads:continue
            seen_threads.add(tid)
            th=svc.users().threads().get(userId='me',id=tid,format='metadata',metadataHeaders=['From','Subject','Date']).execute();msgs=th.get('messages',[])
            if not msgs:continue
            last=max(msgs,key=lambda m:int(m.get('internalDate','0') or 0));hdr=last.get('payload',{}).get('headers',[]);sender=_header(hdr,'From');subject=_header(hdr,'Subject');low=sender.lower()
            if email.lower() in low:continue
            if any(w in low for w in auto_words):continue
            ts=int(last.get('internalDate','0') or 0)/1000
            age_hours=max(0,(datetime.now(timezone.utc)-datetime.fromtimestamp(ts,timezone.utc)).total_seconds()/3600) if ts else 0
            if age_hours < 2:continue
            out.append({'account':email,'thread_id':tid,'message_id':last.get('id'),'from':sender,'subject':subject or '(件名なし)','snippet':last.get('snippet',''),'age_hours':round(age_hours,1)})
    out.sort(key=lambda x:x['age_hours'],reverse=True)
    return out[:50]

def google_health():
    accounts=config.google_accounts();mail={}
    for email in accounts.get('mail',[]):
        c=_creds(email,False);mail[email]={'authorized':bool(c),'token':token_path(email).exists()}
    cal_email=accounts.get('calendar');c=_creds(cal_email,False) if cal_email else None
    return {'mail':mail,'calendar':{'email':cal_email,'authorized':bool(c),'token':token_path(cal_email).exists() if cal_email else False}}

def upcoming_calendar():
    email=config.google_accounts().get('calendar');svc=service('calendar','v3',email) if email else None
    if not svc:return []
    now=datetime.now(timezone.utc);end=now+timedelta(days=7)
    res=svc.events().list(calendarId='primary',timeMin=now.isoformat(),timeMax=end.isoformat(),singleEvents=True,orderBy='startTime',maxResults=50).execute()
    return [{'account':email,'id':e.get('id'),'summary':e.get('summary','予定'),'start':e.get('start',{}).get('dateTime') or e.get('start',{}).get('date'),'end':e.get('end',{}).get('dateTime') or e.get('end',{}).get('date'),'location':e.get('location',''),'description':e.get('description',''),'hangoutLink':e.get('hangoutLink',''),'conferenceData':e.get('conferenceData',{}),'htmlLink':e.get('htmlLink',''),'attendees':[x.get('email') for x in e.get('attendees',[]) if x.get('email')]} for e in res.get('items',[])]

def _online_link(e):
    text=' '.join([e.get('location',''),e.get('description',''),e.get('hangoutLink','')])
    return bool(re.search(r'https?://\S*(zoom\.us|meet\.google\.com|teams\.microsoft\.com)\S*',text,re.I) or e.get('conferenceData'))

def calendar_triggers():
    rows=upcoming_calendar();out=[];now=datetime.now(timezone.utc)
    for e in rows:
        s=e.get('start')
        if not s or 'T' not in s:continue
        try:dt=datetime.fromisoformat(s.replace('Z','+00:00'))
        except Exception:continue
        mins=(dt.astimezone(timezone.utc)-now).total_seconds()/60
        if mins < 0:continue
        # Each threshold is independent. Previously a seen 60-min trigger prevented 30/10-min alerts.
        for threshold in (60,30,10):
            if mins <= threshold:
                key=f"{e.get('id')}:{s}:{threshold}m"
                if seen_calendar(key):continue
                urgent='critical' if threshold==10 else ('high' if threshold==30 else 'normal');payload=e|{'minutes_until':max(0,round(mins)),'urgency':urgent,'threshold':threshold};kind='meeting_critical' if urgent=='critical' else 'meeting'
                add_event('秘書AI',kind,f"{'🚨 ' if urgent=='critical' else '⚠️ ' if urgent=='high' else ''}{e.get('summary','予定')} が約{max(0,round(mins))}分後です",payload);mark_calendar(key);out.append(payload)
                if threshold<=30:ceo_report('秘書AI','会議リマインド',f"{e.get('summary','予定')} が約{max(0,round(mins))}分後です",urgent)
        # Online meeting title but no actual URL / visit meeting without location.
        if 0 <= mins <= 90:
            title=(e.get('summary') or '').lower();online=any(w in title for w in ('zoom','meet','teams','オンライン','web会議'))
            missing=(online and not _online_link(e)) or (not online and not e.get('location') and any(w in title for w in ('訪問','打ち合わせ','商談','面談')))
            if missing:
                key=f"{e.get('id')}:{s}:missing-info"
                if not seen_calendar(key):
                    msg=f"⚠️ {e.get('summary','予定')}：{'Web会議URL' if online else '訪問先/場所'}が見つかりません"
                    add_event('秘書AI','meeting_critical',msg,e|{'minutes_until':max(0,round(mins)),'missing_info':True});ceo_report('秘書AI','予定情報不足',msg,'high');mark_calendar(key);out.append(e)
    return out
