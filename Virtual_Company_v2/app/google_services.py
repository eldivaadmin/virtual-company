from datetime import datetime,timedelta,timezone
from pathlib import Path
import re,json
from . import config
from .db import seen_mail,mark_mail,add_event
SCOPES=['https://www.googleapis.com/auth/gmail.modify','https://www.googleapis.com/auth/gmail.send','https://www.googleapis.com/auth/calendar.events']
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
def poll_gmail():
    out=[]
    for email in config.google_accounts().get('mail',[]):
        svc=service('gmail','v1',email)
        if not svc:continue
        res=svc.users().messages().list(userId='me',q='newer_than:2d -in:spam -in:trash',maxResults=30).execute()
        for item in reversed(res.get('messages',[])):
            mid=item['id']; key=email+':'+mid
            if seen_mail(key):continue
            msg=svc.users().messages().get(userId='me',id=mid,format='metadata',metadataHeaders=['From','To','Subject']).execute()
            hdr=msg.get('payload',{}).get('headers',[]); subject=_header(hdr,'Subject'); sender=_header(hdr,'From'); to=_header(hdr,'To'); snippet=msg.get('snippet','')
            important=bool(config.IMPORTANT_NAME and config.IMPORTANT_NAME.lower() in (to+' '+subject+' '+snippet).lower())
            payload={'account':email,'message_id':mid,'from':sender,'to':to,'subject':subject,'snippet':snippet,'important':important}
            add_event('秘書AI','mail_important' if important else 'mail',f'[{email}] 新着メール: {subject or "(件名なし)"}',payload);mark_mail(key);out.append(payload)
    return out
def upcoming_calendar():
    email=config.google_accounts().get('calendar'); svc=service('calendar','v3',email) if email else None
    if not svc:return []
    now=datetime.now(timezone.utc);end=now+timedelta(hours=24)
    res=svc.events().list(calendarId='primary',timeMin=now.isoformat(),timeMax=end.isoformat(),singleEvents=True,orderBy='startTime',maxResults=20).execute()
    return [{'account':email,'id':e.get('id'),'summary':e.get('summary','予定'),'start':e.get('start',{}).get('dateTime') or e.get('start',{}).get('date')} for e in res.get('items',[])]
