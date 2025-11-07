
function startLiveEvents(wsUrl){
  const box = document.getElementById('live');
  function log(o){
    const pre = document.createElement('pre');
    pre.textContent = typeof o === 'string' ? o : JSON.stringify(o, null, 2);
    box.prepend(pre);
    while (box.childElementCount > 20) box.removeChild(box.lastChild);
  }
  try{
    const ws = new WebSocket(wsUrl);
    ws.onopen = () => log('WS connected');
    ws.onmessage = (ev) => { try{ log(JSON.parse(ev.data)); } catch{ log(ev.data); } };
    ws.onclose = () => log('WS closed');
    ws.onerror = () => log('WS error');
  } catch(e){ log('WS init failed: '+e.message); }
}
