
(function(){
  const sessionId = (crypto && crypto.randomUUID) ? crypto.randomUUID() : String(Math.random()).slice(2);

  function flags(){
    return {
      headless: !!document.getElementById('sim_headless')?.checked,
      proxy_vpn_tor: !!document.getElementById('sim_proxy')?.checked,
      lang_mismatch: !!document.getElementById('sim_lang_mismatch')?.checked
    };
  }

  // Passive env signals
  const env = {
    ua: navigator.userAgent,
    lang: navigator.language,
    tz: Intl.DateTimeFormat().resolvedOptions().timeZone,
    platform: navigator.platform,
    hwc: navigator.hardwareConcurrency || null,
    screen: { w: screen.width, h: screen.height, dpr: devicePixelRatio }
  };

  // Behavior buffers
  const mouse = [];
  const keys = [];
  let lastMoveTs = 0;
  document.addEventListener('mousemove', (e) => {
    const now = performance.now();
    const dt = lastMoveTs ? (now - lastMoveTs) : 0;
    lastMoveTs = now;
    mouse.push({ x: e.clientX, y: e.clientY, t: now, dt });
    if (mouse.length > 1200) mouse.shift();
  }, { passive: true });

  document.addEventListener('keydown', (e) => {
    keys.push({ k: e.key, t: performance.now() });
    if (keys.length > 600) keys.shift();
  }, { passive: true });

  document.addEventListener('paste', () => {
    window.__pasteCount = (window.__pasteCount || 0) + 1;
  });

  async function postJSON(url, body){
    const res = await fetch(url, { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify(body) });
    if(!res.ok) throw new Error('HTTP '+res.status);
    return await res.json();
  }

  function showDecision(dec){
    const el = document.getElementById('decision');
    if (!el) return;
    el.textContent = `Action: ${dec.action}  |  Reasons: ${(dec.reasons||[]).join(', ')}`;
  }

  // ---- Behavioral Challenge ----
  const modal = {
    root: null, canvas: null, ctx: null, msg: null,
    path: null, dragging: false, points: [], started: false, startTs: 0
  };

  function rand(n){ return Math.floor(Math.random()*n); }

  function bezierPath(w,h){
    // Random-ish start/end and two control points
    const start = {x: 40, y: 40+rand(h-80)};
    const end = {x: w-40, y: 40+rand(h-80)};
    const c1 = {x: 40+rand(w/2-60), y: 40+rand(h-80)};
    const c2 = {x: w/2+rand(w/2-60), y: 40+rand(h-80)};

    // Sample curve to polyline for distance checks
    const samples = [];
    for(let t=0;t<=1.0;t+=0.01){
      const x = (1-t)**3*start.x + 3*(1-t)**2*t*c1.x + 3*(1-t)*t**2*c2.x + t**3*end.x;
      const y = (1-t)**3*start.y + 3*(1-t)**2*t*c1.y + 3*(1-t)*t**2*c2.y + t**3*end.y;
      samples.push({x,y});
    }
    return {start,end,c1,c2,samples};
  }

  function drawPath(ctx, path){
    const {start,end,c1,c2} = path;
    ctx.clearRect(0,0,ctx.canvas.width, ctx.canvas.height);
    // guide region
    ctx.save();
    ctx.strokeStyle = '#334155';
    ctx.lineWidth = 14; // wide lane
    ctx.beginPath();
    ctx.moveTo(start.x,start.y);
    ctx.bezierCurveTo(c1.x,c1.y,c2.x,c2.y,end.x,end.y);
    ctx.stroke();
    ctx.restore();

    // actual curve
    ctx.save();
    ctx.strokeStyle = '#22d3ee';
    ctx.lineWidth = 3;
    ctx.beginPath();
    ctx.moveTo(start.x,start.y);
    ctx.bezierCurveTo(c1.x,c1.y,c2.x,c2.y,end.x,end.y);
    ctx.stroke();
    ctx.restore();
  }

  function dist2(a,b){ const dx=a.x-b.x, dy=a.y-b.y; return Math.sqrt(dx*dx+dy*dy); }

  async function openChallenge(collectorBase){
    modal.root = document.getElementById('challengeModal');
    modal.canvas = document.getElementById('challengeCanvas');
    modal.ctx = modal.canvas.getContext('2d');
    modal.msg = document.getElementById('challengeMsg');
    modal.points = []; modal.started=false; modal.dragging=false; modal.startTs=0;
    modal.path = bezierPath(modal.canvas.width, modal.canvas.height);
    drawPath(modal.ctx, modal.path);
    modal.root.classList.remove('hidden');

    const dot = {x: modal.path.start.x, y: modal.path.start.y, r: 7};

    function draw(){
      drawPath(modal.ctx, modal.path);
      // draw dot
      modal.ctx.save();
      modal.ctx.fillStyle = '#3b82f6';
      modal.ctx.beginPath();
      modal.ctx.arc(dot.x, dot.y, dot.r, 0, Math.PI*2);
      modal.ctx.fill();
      modal.ctx.restore();
    }

    function onMove(ev){
      if (!modal.dragging) return;
      const rect = modal.canvas.getBoundingClientRect();
      dot.x = ev.clientX - rect.left; dot.y = ev.clientY - rect.top;
      draw();
      const now = performance.now();
      if (!modal.started){ modal.started = true; modal.startTs = now; }
      modal.points.push({x:dot.x, y:dot.y, t: now});
    }

    function onDown(ev){
      const rect = modal.canvas.getBoundingClientRect();
      const p = {x: ev.clientX-rect.left, y: ev.clientY-rect.top};
      if (dist2(p, {x: modal.path.start.x, y: modal.path.start.y}) < 15){
        modal.dragging = true; modal.msg.textContent = 'Keep the dot on the path…';
      }
    }
    function onUp(){ modal.dragging = false; }

    modal.canvas.addEventListener('mousemove', onMove);
    modal.canvas.addEventListener('mousedown', onDown);
    window.addEventListener('mouseup', onUp);

    document.getElementById('restartBtn').onclick = () => {
      modal.points = []; modal.started=false; modal.dragging=false; modal.startTs=0; draw(); modal.msg.textContent='Restarted.';
    };
    document.getElementById('cancelBtn').onclick = () => {
      modal.root.classList.add('hidden');
    };

    // Finish when near end
    const finishChecker = setInterval(async () => {
      if (!modal.started || modal.points.length < 20) return;
      const last = modal.points[modal.points.length-1];
      if (dist2(last, modal.path.end) < 18){
        clearInterval(finishChecker);
        modal.msg.textContent = 'Checking…';
        try {
          const payload = {
            session_id: sessionId,
            ts: new Date().toISOString(),
            path_spec: {start: modal.path.start, end: modal.path.end, c1: modal.path.c1, c2: modal.path.c2},
            trail: modal.points,
            env_flags: flags()
          };
          const res = await postJSON(collectorBase + '/challenge', payload);
          modal.msg.textContent = res.passed ? 'Passed ✅' : 'Failed ❌';
          setTimeout(()=> modal.root.classList.add('hidden'), 1000);
          const decEl = document.getElementById('decision');
          if (decEl) decEl.textContent = res.passed ? 'Action: allow (post-challenge)' : 'Action: deny (post-challenge)';
        } catch (e){ modal.msg.textContent = 'Error: '+e.message; }
      }
    }, 250);

    draw();
  }

  window.attachPaymentForm = function(formId, opts){
    const base = (opts && opts.collectorBase) || '';
    const form = document.getElementById(formId);

    form.addEventListener('submit', async (e) => {
      e.preventDefault();
      const formData = Object.fromEntries(new FormData(form).entries());
      const snap = {
        session_id: sessionId,
        ts: new Date().toISOString(),
        channel: 'web',
        env: {...env, flags: flags()},
        behavior: {
          mouse: mouse.slice(-800),
          keys: keys.slice(-400),
          paste_count: window.__pasteCount || 0
        },
        journey: {
          amount: formData.amount,
          beneficiary: formData.beneficiary,
          new_beneficiary: true
        }
      };
      try{
        const res = await postJSON(base + '/collect', snap);
        const dec = res.decision || {};
        const el = document.getElementById('decision');
        el.textContent = `Action: ${dec.action}  |  Reasons: ${(dec.reasons||[]).join(', ')}`;
        if (dec.action === 'step_up_behavior_challenge'){
          await openChallenge(base);
        } else if (dec.action === 'step_up_webauthn'){
          alert('Step-Up suggested: WebAuthn (placeholder in local demo)');
        } else {
          alert('Submitted! Action: '+dec.action+' — Check Dashboard http://localhost:8501');
          form.reset();
        }
      } catch(err){
        alert('Error: '+err.message);
      }
    });
  };
})();
