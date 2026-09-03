import json, os, time
from urllib.request import Request, urlopen
from .config import DATA_DIR
CACHE=DATA_DIR/'social_cache.json'
X_URL=os.getenv('X_PROFILE_URL','https://x.com/hi_chronos')
NOTE_URL=os.getenv('NOTE_PROFILE_URL','https://note.com/hi_chronos')
def _get(url):
 with urlopen(Request(url,headers={'User-Agent':'Mozilla/5.0'}),timeout=8) as r:return r.read().decode('utf-8','replace')
def note_stats():
 handle=NOTE_URL.rstrip('/').split('/')[-1]
 out={'profile_url':NOTE_URL,'available':False,'article_count':None,'followers':None,'recent':[],'top_liked':None}
 try:
  profile=json.loads(_get('https://note.com/api/v2/creators/'+handle)).get('data',{})
  notes=json.loads(_get('https://note.com/api/v2/creators/'+handle+'/contents?kind=note&page=1')).get('data',{}).get('contents') or []
  items=[{'title':n.get('name') or '記事','likes':n.get('likeCount') or 0} for n in notes[:12]]
  out.update({'available':True,'article_count':profile.get('noteCount'),'followers':profile.get('followerCount'),'recent':items[:6],'top_liked':max(items,key=lambda x:x['likes']) if items else None})
 except Exception as e:out['error']=str(e)
 return out
def x_stats():
 return {'profile_url':X_URL,'available':False,'source':'X API token required for reliable metrics','followers':None,'post_count':None,'top_liked':None,'recent':[]}
def social_stats(force=False):
 try:
  cached=json.loads(CACHE.read_text(encoding='utf-8'))
  if not force and int(time.time())-int(cached.get('fetched_at',0))<120:return cached
 except Exception:pass
 data={'fetched_at':int(time.time()),'x':x_stats(),'note':note_stats()}
 try:CACHE.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
 except Exception:pass
 return data
