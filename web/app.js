
const BUILD='COMPLETEFIX-20260901-1948';
let AGENTS=[], paused=false, states={}, lastEventId=0, busyUntil={};
const DEST={
  entrance:[11,88], ceo:[16,18], secretary:[39,18], planning:[65,18], sales:[87,20],
  accounting:[15,61], meeting:[40,61], development:[66,61], marketing:[87,61],
  mail:[35,36], hallway:[50,43], hallwayLeft:[28,43], hallwayRight:[73,43],
  coffee:[88,87], report:[25,29]
};
async function j(url,opt){const r=await fetch(url,opt);if(!r.ok)throw new Error(await r.text());return r.json()}
function spritePath(a,kind,dir='down',frame=1){
  const base=`/assets/characters_hd2/${a.sprite}/`;
  if(kind==='work')return base+`work.png?v=${BUILD}`;
  if(kind==='idle')return base+`idle.png?v=${BUILD}`;
  return base+`walk_${dir}_${frame}.png?v=${BUILD}`;
}
function setState(a,state,label){
  states[a.id]=states[a.id]||{};
  states[a.id].state=state;
  const e=document.getElementById('a-'+a.id);
  if(e){
    e.dataset.state=state;
    const s=e.querySelector('.status');
    if(s)s.textContent=label||state;
  }
}
function faceDir(dx,dy){
  if(Math.abs(dx)>Math.abs(dy))return dx<0?'left':'right';
  return dy<0?'up':'down';
}
function speak(a,msg,ms=2300){
  const e=document.getElementById('a-'+a.id);if(!e)return;
  const b=e.querySelector('.bubble');if(!b)return;
  b.textContent=msg;e.classList.add('talk');
  setTimeout(()=>e.classList.remove('talk'),ms);
}
function moveTo(a,target,msg,after){
  if(!a)return;
  const e=document.getElementById('a-'+a.id);if(!e)return;
  const dest=Array.isArray(target)?target:(DEST[target]||a.seat);
  const s=states[a.id]||{x:a.seat[0],y:a.seat[1]};
  const sx=Number.isFinite(s.x)?s.x:a.seat[0], sy=Number.isFinite(s.y)?s.y:a.seat[1];
  const tx=dest[0],ty=dest[1],dir=faceDir(tx-sx,ty-sy);
  const distance=Math.hypot(tx-sx,ty-sy),duration=Math.max(1300,distance*78);
  const started=performance.now();
  busyUntil[a.id]=Date.now()+duration+500;
  setState(a,'walking','移動中');
  if(msg)speak(a,msg);
  function frame(now){
    if(paused){requestAnimationFrame(frame);return}
    const p=Math.min(1,(now-started)/duration);
    const q=p<.5?2*p*p:1-Math.pow(-2*p+2,2)/2;
    const x=sx+(tx-sx)*q,y=sy+(ty-sy)*q;
    states[a.id].x=x;states[a.id].y=y;
    e.style.left=x+'%';e.style.top=y+'%';
    const img=e.querySelector('img');
    img.src=spritePath(a,'walk',dir,Math.floor(now/135)%3);
    img.style.transform=`translateY(${Math.floor(now/135)%2?'-2px':'0px'})`;
    if(p<1)requestAnimationFrame(frame);
    else{
      states[a.id].x=tx;states[a.id].y=ty;
      e.querySelector('img').src=spritePath(a,'idle');
      setState(a,'present','在席');
      if(after)after();
    }
  }
  requestAnimationFrame(frame);
}
function movePath(a,points,msg,done){
  let i=0;
  function next(){
    if(i>=points.length){if(done)done();return}
    moveTo(a,points[i++],i===1?msg:null,next);
  }
  next();
}
function workAt(a,target,label='作業中'){
  moveTo(a,target,label,()=>{
    const e=document.getElementById('a-'+a.id);
    if(e)e.querySelector('img').src=spritePath(a,'work');
    setState(a,'working',label);
    busyUntil[a.id]=Date.now()+7000;
  });
}
function returnSeat(a,msg='自席へ戻ります'){
  movePath(a,['hallway',a.seat],msg,()=>setState(a,'present','在席'));
}
function goOut(a){
  movePath(a,['hallway','entrance'],'外出します',()=>{
    const e=document.getElementById('a-'+a.id);if(e)e.classList.add('hiddenAgent');
    setState(a,'out','外出中');busyUntil[a.id]=Date.now()+99999999;
  });
}
function returnOffice(a){
  const e=document.getElementById('a-'+a.id);if(!e)return;
  e.classList.remove('hiddenAgent');
  states[a.id].x=DEST.entrance[0];states[a.id].y=DEST.entrance[1];
  e.style.left=DEST.entrance[0]+'%';e.style.top=DEST.entrance[1]+'%';
  busyUntil[a.id]=0;
  movePath(a,['hallway',a.seat],'帰社しました',()=>setState(a,'present','在席'));
}
function renderAgent(a){
  const persisted=(a.presence&&a.presence.state)||'present';
  states[a.id]={x:a.seat[0],y:a.seat[1],state:persisted};
  const e=document.createElement('div');
  e.className='spriteAgent';e.id='a-'+a.id;
  e.style.left=a.seat[0]+'%';e.style.top=a.seat[1]+'%';
  e.innerHTML=`<div class="bubble">${a.role}</div>
  <img src="${spritePath(a,'idle')}" draggable="false" alt="${a.name}">
  <div class="tag">${a.name}<span class="status">在席</span></div>`;
  document.getElementById('sprites').appendChild(e);
  e.addEventListener('click',()=>selectAgent(a));
  if(persisted==='out'){e.classList.add('hiddenAgent');setState(a,'out','外出中')}
  else if(persisted==='away'){
    states[a.id].x=DEST.coffee[0];states[a.id].y=DEST.coffee[1];
    e.style.left=DEST.coffee[0]+'%';e.style.top=DEST.coffee[1]+'%';setState(a,'away','離席中')
  } else if(persisted==='meeting'){
    states[a.id].x=DEST.meeting[0];states[a.id].y=DEST.meeting[1];
    e.style.left=DEST.meeting[0]+'%';e.style.top=DEST.meeting[1]+'%';setState(a,'meeting','会議中')
  } else setState(a,'present','在席');
}
function selectAgent(a){
  const sel=document.getElementById('agent');if(sel)sel.value=a.id;
  const el=document.getElementById('selected');if(!el)return;
  el.innerHTML=`<b>${a.name}</b><small>${a.role}</small>
  <div class="presenceBtns">
   <button data-p="present">在席</button><button data-p="away">離席</button>
   <button data-p="out">外出</button><button data-p="meeting">会議</button>
  </div>`;
  el.querySelectorAll('[data-p]').forEach(b=>b.addEventListener('click',()=>presence(a.id,b.dataset.p)));
}
async function presence(id,state){
  const a=AGENTS.find(x=>x.id===id);if(!a)return;
  await j('/api/presence',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({agent_id:id,state})});
  if(state==='out')goOut(a);
  else if(state==='present')returnOffice(a);
  else if(state==='away')movePath(a,['hallway','coffee'],'少し離席します',()=>setState(a,'away','離席中'));
  else if(state==='meeting')movePath(a,['hallway','meeting'],'会議室へ移動',()=>setState(a,'meeting','会議中'));
}
function reactEvent(x){
  const sec=AGENTS.find(a=>a.id==='secretary'),acc=AGENTS.find(a=>a.id==='accounting'),hr=AGENTS.find(a=>a.id==='hr');
  if(x.kind==='mail_critical'&&sec){
    const e=document.getElementById('a-'+sec.id); if(e)e.classList.add('urgentAgent');
    speak(sec,'🚨 緊急メールです！',3500);
    movePath(sec,['hallway','mail'],'至急確認します',()=>{
      setState(sec,'working','緊急メール確認');
      setTimeout(()=>movePath(sec,['hallway','report'],'社長、緊急です！',()=>{
        speak(sec,'すぐ確認してください',3500);
        setTimeout(()=>{if(e)e.classList.remove('urgentAgent');returnSeat(sec)},2800)
      }),1200);
    });
  }
  if(x.kind==='mail_important'&&sec){
    movePath(sec,['hallway','mail'],'新着メールを確認します',()=>{
      const e=document.getElementById('a-'+sec.id);if(e)e.querySelector('img').src=spritePath(sec,'work');
      setState(sec,'working','メール確認中');
      setTimeout(()=>movePath(sec,['hallway','report'],'CEOへ報告します',()=>setTimeout(()=>returnSeat(sec),2200)),2400);
    });
  }
  if((x.kind==='deadline'||x.kind==='accounting')&&acc){
    workAt(acc,acc.seat,'経理処理中');
    setTimeout(()=>movePath(acc,['hallway','report'],'CEOへ経理報告',()=>setTimeout(()=>returnSeat(acc),1800)),2600);
  }
  if((x.kind==='meeting'||x.kind==='meeting_critical')&&sec){
    const urgent=x.kind==='meeting_critical';
    const e=document.getElementById('a-'+sec.id);if(urgent&&e)e.classList.add('urgentAgent');
    movePath(sec,['hallway','report'],urgent?'🚨 会議10分前です！':'予定をお知らせします',()=>{
      speak(sec,urgent?'会議まで10分です！':'予定があります',urgent?3500:2200);
      setTimeout(()=>{if(e)e.classList.remove('urgentAgent');returnSeat(sec)},urgent?2600:1800);
    });
  }
  if(x.kind==='task_start'){
    const a=AGENTS.find(a=>a.name===x.agent);if(a)workAt(a,a.seat,'実タスク処理中');
  }
  if(x.kind==='task_done'){
    const a=AGENTS.find(a=>a.name===x.agent);
    if(a)movePath(a,['hallway','report'],'タスク完了を報告',()=>setTimeout(()=>returnSeat(a),1600));
  }
}
function ambientMotion(){
  if(paused||!AGENTS.length)return;
  const candidates=AGENTS.filter(a=>{
    const s=states[a.id]?.state;
    return s==='present' && Date.now()>(busyUntil[a.id]||0);
  });
  if(!candidates.length)return;
  const a=candidates[Math.floor(Math.random()*candidates.length)];
  const places=a.id==='secretary'?['mail','hallwayLeft','coffee']:
    a.id==='ceo'?['hallway','hallwayLeft']:
    ['hallway','hallwayLeft','hallwayRight','coffee'];
  const dest=places[Math.floor(Math.random()*places.length)];
  movePath(a,['hallway',dest],'移動中',()=>setTimeout(()=>returnSeat(a),1800+Math.random()*2200));
}
async function refresh(){
  try{
    const st=await j('/api/status');
    let gh=null,ms=null;try{gh=await j('/api/google/health')}catch(_){} try{ms=await j('/api/mail/summary')}catch(_){}
    const conn=document.getElementById('conn');conn.textContent='● '+BUILD;conn.className='ok';
    document.getElementById('status').innerHTML=
      `Gmail:<br>${gh?Object.entries(gh.mail).map(([k,v])=>{
        const c=ms&&ms[k];
        if(!v.authorized)return `<b class="bad">${k}: 未接続</b>`;
        return `<b class="ok">${k}: 接続</b>${c?`<br><span class="mailCount">未読 ${c.unread} / 重要未読 ${c.important_unread}</span>`:''}`;
      }).join('<br>'):'確認中'}<br>Calendar:<br>${gh?`<b class="${gh.calendar.authorized?'ok':'bad'}">${gh.calendar.email}: ${gh.calendar.authorized?'接続':'未接続'}</b>`:'確認中'}<br>OpenAI: ${st.openai?'設定済':'未設定'}<br>Claude: ${st.claude?'設定済':'未設定'}`;
    const ev=await j('/api/events?limit=35');
    const logs=document.getElementById('logs');logs.innerHTML='';
    document.getElementById('alerts').innerHTML='';
    [...ev].reverse().forEach(x=>{if(x.id&&x.id>lastEventId){reactEvent(x);lastEventId=x.id}});
    ev.forEach(x=>{
      const d=document.createElement('div');d.className='log';
      d.innerHTML=`<time>${x.ts.slice(11,16)}</time> <b>${x.agent}</b><br>${x.message}`;
      logs.appendChild(d);
      if(['mail_important','deadline','meeting','error'].includes(x.kind)){
        const q=document.createElement('div');q.className='alert';q.textContent=x.agent+'｜'+x.message;
        document.getElementById('alerts').appendChild(q);
      }
    });
    try{
      const cal=await j('/api/calendar'),ce=document.getElementById('cal');ce.innerHTML='';
      cal.slice(0,8).forEach(x=>{
        const d=document.createElement('div');d.className='log';
        d.innerHTML=`<b>${x.summary}</b><br>${(x.start||'').replace('T',' ').slice(0,16)}`;
        ce.appendChild(d);
      });
    }catch(_){}
  }catch(e){
    const conn=document.getElementById('conn');conn.textContent='● サーバー未接続';conn.className='bad';
  }
}
async function boot(){
  AGENTS=await j('/api/agents');
  const sel=document.getElementById('agent'),al=document.getElementById('alist');
  AGENTS.forEach(a=>{
    renderAgent(a);
    const o=document.createElement('option');o.value=a.id;o.textContent=a.name;sel.appendChild(o);
    const b=document.createElement('button');b.className='employee';
    b.innerHTML=`${a.name}<span>${a.role}</span>`;b.addEventListener('click',()=>selectAgent(a));al.appendChild(b);
  });
  if(AGENTS.length)selectAgent(AGENTS[0]);
  await refresh();
  setInterval(refresh,4000);
  setInterval(ambientMotion,4500);
  setTimeout(ambientMotion,900);
}
document.querySelectorAll('[data-sim]').forEach(b=>b.addEventListener('click',async()=>{
  await j('/api/simulate',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({kind:b.dataset.sim})});setTimeout(refresh,300)
}));
document.getElementById('gmail').addEventListener('click',async()=>{await j('/api/check/gmail',{method:'POST'});refresh()});
document.getElementById('calendar').addEventListener('click',async()=>{await j('/api/check/calendar',{method:'POST'});refresh()});
document.getElementById('pause').addEventListener('click',e=>{paused=!paused;e.target.textContent=paused?'▶ 再開':'⏸ AI会社を一時停止'});
document.getElementById('runTask').addEventListener('click',async()=>{
  const result=document.getElementById('result'),a=AGENTS.find(x=>x.id===document.getElementById('agent').value);
  result.textContent='実行中…';if(a)workAt(a,a.seat,'実タスク処理中');
  try{
    const data=await j('/api/task',{method:'POST',headers:{'Content-Type':'application/json'},
      body:JSON.stringify({agent_id:a.id,prompt:document.getElementById('prompt').value,provider:document.getElementById('provider').value||null})});
    result.textContent=data.result;
  }catch(e){result.textContent='エラー: '+e.message}
});
setInterval(()=>document.getElementById('clock').textContent=new Date().toLocaleString('ja-JP'),1000);
boot().catch(e=>{console.error(e);document.getElementById('conn').textContent='起動エラー: '+e.message});
