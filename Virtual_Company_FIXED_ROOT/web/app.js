
let AGENTS=[], paused=false, states={}, lastEventId=0;
const office=document.getElementById('office');
const DEST={
  entrance:[11,88], ceo:[16,18], secretary:[39,18], planning:[65,18], sales:[87,20],
  accounting:[15,61], meeting:[40,61], development:[66,61], marketing:[87,61],
  mail:[35,36], hallway:[50,42], coffee:[88,88], report:[24,27]
};
async function j(url,opt){let r=await fetch(url,opt);if(!r.ok)throw new Error(await r.text());return r.json()}
function spritePath(a,kind,dir='down',frame=1){
  if(kind==='work') return `/assets/characters/${a.sprite}/work.png?v=HD-20260901-1848`;
  if(kind==='idle') return `/assets/characters/${a.sprite}/idle.png?v=HD-20260901-1848`;
  return `/assets/characters/${a.sprite}/walk_${dir}_${frame}.png?v=HD-20260901-1848`;
}
function setState(a,state,label){
  states[a.id]=states[a.id]||{};
  states[a.id].state=state;
  let e=document.getElementById('a-'+a.id);
  if(e){e.dataset.state=state;e.querySelector('.status').textContent=label||state}
}
function faceDir(dx,dy){if(Math.abs(dx)>Math.abs(dy))return dx<0?'left':'right';return dy<0?'up':'down'}
function moveTo(a,dest,msg,after){
  if(paused)return;
  const e=document.getElementById('a-'+a.id), target=DEST[dest]||dest;
  if(!e||!target)return;
  const s=states[a.id]||{x:a.seat[0],y:a.seat[1]};
  const sx=s.x??a.seat[0], sy=s.y??a.seat[1], tx=target[0],ty=target[1];
  const dir=faceDir(tx-sx,ty-sy), start=performance.now(), dur=Math.max(700,Math.hypot(tx-sx,ty-sy)*55);
  setState(a,'walking','移動中');
  if(msg){e.querySelector('.bubble').textContent=msg;e.classList.add('talk');setTimeout(()=>e.classList.remove('talk'),2600)}
  function tick(now){
    if(paused){requestAnimationFrame(tick);return}
    let p=Math.min(1,(now-start)/dur), ease=p<.5?2*p*p:1-Math.pow(-2*p+2,2)/2;
    let x=sx+(tx-sx)*ease,y=sy+(ty-sy)*ease;
    states[a.id].x=x;states[a.id].y=y;e.style.left=x+'%';e.style.top=y+'%';
    let f=Math.floor(now/180)%3;e.querySelector('img').src=spritePath(a,'walk',dir,f);
    if(p<1)requestAnimationFrame(tick);else{
      states[a.id].x=tx;states[a.id].y=ty;
      e.querySelector('img').src=spritePath(a,'idle');setState(a,'present','在席');
      if(after)after();
    }
  } requestAnimationFrame(tick);
}
function workAt(a,dest,label='作業中'){
  moveTo(a,dest,label,()=>{let e=document.getElementById('a-'+a.id);e.querySelector('img').src=spritePath(a,'work');setState(a,'working',label)})
}
function goOut(a){
  moveTo(a,'entrance','外出します',()=>{let e=document.getElementById('a-'+a.id);e.classList.add('hiddenAgent');setState(a,'out','外出中')})
}
function returnOffice(a){
  let e=document.getElementById('a-'+a.id);e.classList.remove('hiddenAgent');states[a.id].x=DEST.entrance[0];states[a.id].y=DEST.entrance[1];
  e.style.left=DEST.entrance[0]+'%';e.style.top=DEST.entrance[1]+'%';moveTo(a,a.seat,'戻りました',()=>workAt(a,a.seat,'在席'))
}
function renderAgent(a){
  const persisted=(a.presence&&a.presence.state)||'present';
  states[a.id]={x:a.seat[0],y:a.seat[1],state:persisted};
  let e=document.createElement('div');e.className='spriteAgent';e.id='a-'+a.id;e.style.left=a.seat[0]+'%';e.style.top=a.seat[1]+'%';
  e.innerHTML=`<div class="bubble">${a.role}</div><img src="${spritePath(a,'idle')}" draggable="false"><div class="tag">${a.name}<span class="status">在席</span></div>`;
  e.onclick=()=>selectAgent(a);document.getElementById('sprites').appendChild(e);
  if(persisted==='out'){e.classList.add('hiddenAgent');setState(a,'out','外出中')}
  else if(persisted==='away'){states[a.id].x=DEST.coffee[0];states[a.id].y=DEST.coffee[1];e.style.left=DEST.coffee[0]+'%';e.style.top=DEST.coffee[1]+'%';setState(a,'away','離席中')}
  else if(persisted==='meeting'){states[a.id].x=DEST.meeting[0];states[a.id].y=DEST.meeting[1];e.style.left=DEST.meeting[0]+'%';e.style.top=DEST.meeting[1]+'%';setState(a,'meeting','会議中')}
  else setState(a,'present','在席');
}
function selectAgent(a){
  document.getElementById('agent').value=a.id;
  document.getElementById('selected').innerHTML=`<b>${a.name}</b><small>${a.role}</small>
  <div class="presenceBtns"><button onclick="presence('${a.id}','present')">在席</button><button onclick="presence('${a.id}','away')">離席</button><button onclick="presence('${a.id}','out')">外出</button><button onclick="presence('${a.id}','meeting')">会議</button></div>`;
}
window.presence=async(id,state)=>{
  let a=AGENTS.find(x=>x.id===id);if(!a)return;
  await j('/api/presence',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({agent_id:id,state})});
  if(state==='out')goOut(a);
  else if(state==='present')returnOffice(a);
  else if(state==='away')moveTo(a,'coffee','離席中',()=>setState(a,'away','離席中'));
  else if(state==='meeting')moveTo(a,'meeting','会議へ',()=>setState(a,'meeting','会議中'));
}
function reactEvent(x){
  let sec=AGENTS.find(a=>a.id==='secretary'), acc=AGENTS.find(a=>a.id==='accounting'), ceo=AGENTS.find(a=>a.id==='ceo'), hr=AGENTS.find(a=>a.id==='hr');
  if(x.kind==='mail_important'&&sec){
    workAt(sec,'mail','メール確認中');
    setTimeout(()=>moveTo(sec,'report','CEOへ報告',()=>setState(sec,'reporting','報告中')),2200);
  }
  if(x.kind==='deadline'&&acc){workAt(acc,'accounting','請求確認中');setTimeout(()=>moveTo(acc,'report','CEOへ報告'),2200)}
  if(x.kind==='meeting'&&hr){moveTo(hr,'meeting','会議準備',()=>setState(hr,'meeting','会議中'))}
  if(x.kind==='task_start'){let a=AGENTS.find(a=>a.name===x.agent);if(a)workAt(a,a.seat,'実タスク処理中')}
  if(x.kind==='task_done'){let a=AGENTS.find(a=>a.name===x.agent);if(a){moveTo(a,'report','タスク完了報告');setTimeout(()=>moveTo(a,a.seat),2600)}}
}
async function refresh(){
 try{
  let st=await j('/api/status');document.getElementById('conn').textContent='● ローカル稼働中';document.getElementById('conn').className='ok';
  document.getElementById('status').innerHTML=`Gmail監視: <b class="ok">2アカウント</b><br>Calendar: <b class="ok">集約1アカウント</b><br>OpenAI: ${st.openai?'設定済':'未設定'}<br>Claude: ${st.claude?'設定済':'未設定'}`;
  let ev=await j('/api/events?limit=35'),logs=document.getElementById('logs');logs.innerHTML='';document.getElementById('alerts').innerHTML='';
  try{
    let cal=await j('/api/calendar'), ce=document.getElementById('cal');ce.innerHTML='';
    cal.slice(0,8).forEach(x=>{let d=document.createElement('div');d.className='log';let s=x.start||'';d.innerHTML='<b>'+x.summary+'</b><br>'+s.replace('T',' ').slice(0,16);ce.appendChild(d)})
  }catch(_){}
  [...ev].reverse().forEach(x=>{ if(x.id && x.id>lastEventId){reactEvent(x);lastEventId=x.id} });
  ev.forEach(x=>{let d=document.createElement('div');d.className='log';d.innerHTML='<time>'+x.ts.slice(11,16)+'</time> <b>'+x.agent+'</b><br>'+x.message;logs.appendChild(d);
   if(['mail_important','deadline','meeting','error'].includes(x.kind)){let q=document.createElement('div');q.className='alert';q.textContent=x.agent+'｜'+x.message;document.getElementById('alerts').appendChild(q)}
  });
 }catch(e){document.getElementById('conn').textContent='● サーバー未接続';document.getElementById('conn').className='bad'}
}
async function boot(){
 AGENTS=await j('/api/agents');let sel=document.getElementById('agent'),al=document.getElementById('alist');
 AGENTS.forEach(a=>{renderAgent(a);let o=document.createElement('option');o.value=a.id;o.textContent=a.name;sel.appendChild(o);
  let b=document.createElement('button');b.className='employee';b.innerHTML=`${a.name}<span>${a.role}</span>`;b.onclick=()=>selectAgent(a);al.appendChild(b)});
 selectAgent(AGENTS[0]);await refresh();setInterval(refresh,4000);
}
document.querySelectorAll('[data-sim]').forEach(b=>b.onclick=async()=>{await j('/api/simulate',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({kind:b.dataset.sim})});setTimeout(refresh,300)});
document.getElementById('gmail').onclick=async()=>{await j('/api/check/gmail',{method:'POST'});refresh()};
document.getElementById('calendar').onclick=async()=>{await j('/api/check/calendar',{method:'POST'});refresh()};
document.getElementById('pause').onclick=e=>{paused=!paused;e.target.textContent=paused?'▶ 再開':'⏸ 一時停止'};
document.getElementById('runTask').onclick=async()=>{
 let result=document.getElementById('result'),a=AGENTS.find(x=>x.id===document.getElementById('agent').value);result.textContent='実行中…';if(a)workAt(a,a.seat,'実タスク処理中');
 try{let data=await j('/api/task',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({agent_id:a.id,prompt:document.getElementById('prompt').value,provider:document.getElementById('provider').value||null})});result.textContent=data.result}
 catch(e){result.textContent='エラー: '+e.message}
};
setInterval(()=>document.getElementById('clock').textContent=new Date().toLocaleString('ja-JP'),1000);boot();
