from datetime import datetime,timedelta,timezone
from .config import GOOGLE_CREDENTIALS,GOOGLE_TOKEN,IMPORTANT_NAME
from .db import seen_mail,mark_mail,add_event
SCOPES=['https://www.googleapis.com/auth/gmail.modify','https://www.googleapis.com/auth/gmail.send','https://www.googleapis.com/auth/calendar.events']

def _creds(interactive=False):
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request
    from google_auth_oauthlib.flow import InstalledAppFlow
    creds=None
    if GOOGLE_TOKEN.exists():creds=Credentials.from_authorized_user_file(str(GOOGLE_TOKEN),SCOPES)
    if creds and creds.expired and creds.refresh_token:creds.refresh(Request())
    if (not creds or not creds.valid) and interactive:
        if not GOOGLE_CREDENTIALS.exists():raise FileNotFoundError('secrets/credentials.json がありません')
        flow=InstalledAppFlow.from_client_secrets_file(str(GOOGLE_CREDENTIALS),SCOPES)
        creds=flow.run_local_server(port=0)
        GOOGLE_TOKEN.write_text(creds.to_json(),encoding='utf-8')
    return creds if creds and creds.valid else None

def authorize():return bool(_creds(True))

def gmail_service():
    creds=_creds(False)
    if not creds:return None
    from googleapiclient.discovery import build
    return build('gmail','v1',credentials=creds,cache_discovery=False)

def calendar_service():
    creds=_creds(False)
    if not creds:return None
    from googleapiclient.discovery import build
    return build('calendar','v3',credentials=creds,cache_discovery=False)

def _header(headers,name):
    for h in headers:
        if h.get('name','').lower()==name.lower():return h.get('value','')
    return ''

def poll_gmail():
    svc=gmail_service()
    if not svc:return []
    res=svc.users().messages().list(userId='me',q='newer_than:2d',maxResults=20).execute();out=[]
    for item in reversed(res.get('messages',[])):
        mid=item['id']
        if seen_mail(mid):continue
        msg=svc.users().messages().get(userId='me',id=mid,format='metadata',metadataHeaders=['From','To','Subject']).execute()
        hdr=msg.get('payload',{}).get('headers',[]);subject=_header(hdr,'Subject');sender=_header(hdr,'From');to=_header(hdr,'To');snippet=msg.get('snippet','')
        important=bool(IMPORTANT_NAME and IMPORTANT_NAME.lower() in (to+' '+subject+' '+snippet).lower())
        payload={'message_id':mid,'from':sender,'to':to,'subject':subject,'snippet':snippet,'important':important}
        add_event('秘書AI','mail_important' if important else 'mail',f'新着メール: {subject or "(件名なし)"}',payload);mark_mail(mid);out.append(payload)
    return out

def upcoming_calendar():
    svc=calendar_service()
    if not svc:return []
    now=datetime.now(timezone.utc);end=now+timedelta(hours=24)
    res=svc.events().list(calendarId='primary',timeMin=now.isoformat(),timeMax=end.isoformat(),singleEvents=True,orderBy='startTime',maxResults=20).execute()
    return [{'id':e.get('id'),'summary':e.get('summary','予定'),'start':e.get('start',{}).get('dateTime') or e.get('start',{}).get('date')} for e in res.get('items',[])]
