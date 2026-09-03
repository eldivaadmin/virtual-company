// AI COMPANY OS polish patch 2026-09-03 16:30
(function(){
  function clampDest(t){
    if(!Array.isArray(t)) return t;
    return [Math.max(5,Math.min(94,t[0])),Math.max(8,Math.min(91,t[1]))];
  }
  const originalMoveTo=moveTo;
  moveTo=function(a,t,m,done){ return originalMoveTo(a,clampDest(t),m,done); };

  // LOAD follows actual state. STAMINA is intentionally demo/random until a real fatigue model is defined.
  function reconcileResources(){
    if(!AGENTS || !AGENTS.length) return;
    AGENTS.forEach(a=>{
      const r=res(a), s=(states[a.id]||{}).state||'present';
      const target={present:18,walking:38,working:84,meeting:62,away:7,out:12}[s] ?? 18;
      r.load=Math.max(0,Math.min(100,target + Math.round(Math.random()*8-4)));
      if(!r._demoStamina || Date.now()-r._demoStamina>15000){
        r.stamina=35+Math.floor(Math.random()*66);r._demoStamina=Date.now();
      }
    });
    renderResources();
  }

  function fmtAge(h){ if(h>=48)return Math.round(h/24)+'日前'; if(h>=24)return '約'+Math.round(h/24)+'日前'; return '約'+Math.max(2,Math.round(h))+'時間前'; }
  async function secretaryDeepCheck(){
    try{
      const [waiting,cal]=await Promise.all([j('/api/mail/unreplied?limit=40&days=14').catch(()=>[]),j('/api/calendar').catch(()=>[])]);
      let box=document.getElementById('secretaryWatch');
      if(!box){ box=document.createElement('div');box.id='secretaryWatch';document.getElementById('status').appendChild(box); }
      box.innerHTML=`<h3>秘書ウォッチ</h3><b>未返信候補 ${waiting.length}件</b>${waiting.slice(0,6).map(x=>`<div class="watchItem"><b>${x.subject}</b><br>${x.from}<br><span class="muted">${fmtAge(x.age_hours)}</span></div>`).join('')}`;
      const now=Date.now();
      const imminent=cal.filter(e=>e.start&&e.start.includes('T')).map(e=>({e,ms:new Date(e.start).getTime()-now})).filter(x=>x.ms>=0&&x.ms<=60*60*1000).sort((a,b)=>a.ms-b.ms);
      let a=document.getElementById('secretaryImmediate');
      if(!a){a=document.createElement('div');a.id='secretaryImmediate';document.getElementById('alerts').prepend(a)}
      a.innerHTML=imminent.map(x=>{const min=Math.max(0,Math.round(x.ms/60000)),e=x.e,online=/zoom|meet|teams|オンライン|web会議/i.test(e.summary||''),txt=[e.location||'',e.description||'',e.hangoutLink||''].join(' '),hasUrl=/https?:\/\/\S*(zoom\.us|meet\.google\.com|teams\.microsoft\.com)/i.test(txt),missing=online&&!hasUrl;return `<div class="alert ${min<=10?'critical':''}"><b>秘書AI｜${min}分後</b><br>${e.summary}${missing?'<br>⚠ Web会議URLが見つかりません':''}</div>`}).join('');
    }catch(e){console.warn('secretaryDeepCheck',e)}
  }

  setInterval(reconcileResources,5000);
  setTimeout(reconcileResources,1500);
  setInterval(secretaryDeepCheck,60000);
  setTimeout(secretaryDeepCheck,2500);
})();
