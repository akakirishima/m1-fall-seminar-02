'use strict';
const $ = id => document.getElementById(id);
const LABELS = {present:'介入あり', absent:'介入なし', uncertain:'判定不能'};
const CACHE_PREFIX = 'infant-frame-annotation-v1:';
let state = null, files = [], cacheKey = '', image = null, ready = false;
let drawing = false, points = [], displayToken = 0, selectionToken = 0, busy = false;
const canvas = $('canvas'), ctx = canvas.getContext('2d');
const tell = text => { $('message').textContent = text; };
const hasLabels = () => state && Object.keys(state.labels).length > 0;
const current = () => state?.manifest[state.index];
const idOf = m => m.sha256 + '|' + m.path;
function validKeys(keys) {
  return keys && Object.keys(LABELS).every(k => typeof keys[k] === 'string' && /^[a-z0-9]$/.test(keys[k])) && new Set(Object.values(keys)).size === 3;
}
function validPolygon(roi) {
  if (!roi || !Number.isInteger(roi.width) || !Number.isInteger(roi.height) || roi.width <= 0 || roi.height <= 0 || !Array.isArray(roi.points) || roi.points.length < 3) return false;
  const p = roi.points;
  if (!p.every(a => Array.isArray(a) && a.length === 2 && a.every(x => typeof x === 'number' && Number.isFinite(x) && x >= 0 && x <= 1))) return false;
  if (new Set(p.map(a=>a.join(','))).size !== p.length) return false;
  const cross = (a,b,c) => (b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0]);
  const between = (a,b,c) => Math.min(a[0],b[0]) <= c[0] && c[0] <= Math.max(a[0],b[0]) && Math.min(a[1],b[1]) <= c[1] && c[1] <= Math.max(a[1],b[1]);
  for (let i=0;i<p.length;i++) for (let j=i+1;j<p.length;j++) {
    if (j===i+1 || (i===0 && j===p.length-1)) continue;
    const a=p[i], b=p[(i+1)%p.length], c=p[j], d=p[(j+1)%p.length];
    const x=cross(a,b,c), y=cross(a,b,d), z=cross(c,d,a), w=cross(c,d,b);
    if ((x*y<0 && z*w<0) || (x===0 && between(a,b,c)) || (y===0 && between(a,b,d)) || (z===0 && between(c,d,a)) || (w===0 && between(c,d,b))) return false;
  }
  return Math.abs(p.reduce((sum,a,i)=> {const b=p[(i+1)%p.length];return sum+a[0]*b[1]-b[0]*a[1];},0)) > 0.00001;
}
function validateProject(s, manifest) {
  if (!s || s.schema_version !== 'frame-annotation-v1' || JSON.stringify(s.manifest) !== JSON.stringify(manifest)) throw Error('選択した画像と保存データが一致しません。元と同じ画像一式を選んでください。');
  if (!['roi','full_frame',null].includes(s.scope) || !validKeys(s.keys) || !Number.isInteger(s.index) || s.index<0 || s.index>=manifest.length) throw Error('作業設定が不正です。');
  if (s.scope==='roi' ? !validPolygon(s.roi) : s.roi!==null) throw Error('ROIが不正です。');
  if (!s.labels || typeof s.labels!=='object' || Array.isArray(s.labels) || !s.notes || typeof s.notes!=='object' || Array.isArray(s.notes)) throw Error('ラベル形式が不正です。');
  const ids=new Set(manifest.map(idOf));
  for (const [id,note] of Object.entries(s.notes)) if (!ids.has(id) || typeof note!=='string') throw Error('メモ形式が不正です。');
  for (const [id,a] of Object.entries(s.labels)) if (!ids.has(id) || !a || !Object.hasOwn(LABELS,a.label) || typeof a.updated_at!=='string' || !Number.isInteger(a.width) || !Number.isInteger(a.height) || a.width<=0 || a.height<=0 || (a.label==='uncertain' && !s.notes[id]?.trim()) || (s.scope==='roi' && (s.roi.width!==a.width || s.roi.height!==a.height))) throw Error('ラベルの内容が不正です。');
  if (Object.keys(s.labels).length && !s.scope) throw Error('判定範囲がありません。');
  return s;
}
function save() {
  if (!state || !cacheKey) return;
  try { localStorage.setItem(cacheKey, JSON.stringify(state)); $('saveStatus').textContent='ブラウザへ自動保存済み。終了前にJSONも保存してください。'; }
  catch { $('saveStatus').textContent='自動保存できません。必ずJSONを保存してください。'; }
}
function syncKeys() {
  const keys=state?.keys || {present:'1',absent:'2',uncertain:'3'};
  for (const [k,field] of Object.entries({present:'keyPresent',absent:'keyAbsent',uncertain:'keyUncertain'})) { $(field).value=keys[k]; $(k).querySelector('kbd').textContent=keys[k]; }
}
function update() {
  const counts={present:0,absent:0,uncertain:0};
  for (const a of Object.values(state?.labels || {})) counts[a.label]++;
  for (const k of Object.keys(counts)) $('count'+k[0].toUpperCase()+k.slice(1)).textContent=counts[k];
  $('countPending').textContent=(files.length-Object.values(counts).reduce((a,b)=>a+b,0));
  const total=counts.present+counts.absent;
  $('ratio').textContent=total ? (100*counts.present/total).toFixed(1)+'%' : '—';
  $('position').textContent=state ? `${state.index+1} / ${files.length}` : '0 / 0';
  $('filename').textContent=current()?.path || '画像を選択すると、ここに表示します';
  const label=state?.labels[idOf(current() || {})]?.label;
  $('currentLabel').textContent=label ? LABELS[label] : '未ラベル';
  $('scope').textContent=drawing ? `頂点 ${points.length} 個：囲み終えたらROI確定` : state?.scope==='roi' ? '共通ROI内を判定（緑の枠）' : state?.scope==='full_frame' ? '全画面を判定' : '判定範囲を設定してください';
  const dimensionsOK=!state?.roi || (image?.naturalWidth===state.roi.width && image?.naturalHeight===state.roi.height);
  for (const k of Object.keys(LABELS)) $(k).disabled=busy || !ready || !state?.scope || drawing || !dimensionsOK;
  $('prev').disabled=busy || !state || state.index===0 || drawing;
  $('next').disabled=busy || !state || state.index===files.length-1 || drawing;
  $('roiStart').disabled=busy || !ready || !!hasLabels() || drawing;
  $('fullFrame').disabled=busy || !ready || !!hasLabels() || drawing;
  $('roiFinish').disabled=!drawing || points.length<3;
  $('roiCancel').disabled=!drawing;
  $('exportJson').disabled=busy || !state;
  $('exportCsv').disabled=busy || !state;
  canvas.style.cursor=drawing ? 'crosshair' : 'default';
}
function draw() {
  if (!image || !ready) return;
  canvas.width=image.naturalWidth; canvas.height=image.naturalHeight;
  ctx.drawImage(image,0,0);
  const p=drawing ? points : state.roi?.points;
  if (!p?.length) return;
  const scale=Math.max(1,canvas.width/700);
  ctx.strokeStyle='#63f4b2';ctx.fillStyle='rgba(80,230,170,.12)';ctx.lineWidth=2*scale;
  ctx.beginPath();p.forEach((a,i)=>ctx[i?'lineTo':'moveTo'](a[0]*canvas.width,a[1]*canvas.height));
  if(!drawing)ctx.closePath();ctx.stroke();if(!drawing)ctx.fill();
  for(const a of p){ctx.beginPath();ctx.arc(a[0]*canvas.width,a[1]*canvas.height,3*scale,0,Math.PI*2);ctx.fillStyle='#63f4b2';ctx.fill();}
}
function show() {
  if (!state) return;
  const token=++displayToken;
  ready=false;image=null;canvas.hidden=true;$('empty').hidden=false;
  $('empty').firstElementChild.textContent='画像を読み込み中…';
  $('note').value=state.notes[idOf(current())] || '';
  update();
  const url=URL.createObjectURL(files[state.index]);
  const nextImage=new Image();
  nextImage.onload=()=>{
    URL.revokeObjectURL(url);if(token!==displayToken)return;
    image=nextImage;ready=true;canvas.hidden=false;$('empty').hidden=true;draw();update();
    if(state.roi && (image.naturalWidth!==state.roi.width || image.naturalHeight!==state.roi.height)) tell('ROI設定時と画像サイズが違うため、ラベル入力を停止しました。この画像は別の作業セットに分けてください。');
  };
  nextImage.onerror=()=>{URL.revokeObjectURL(url);if(token!==displayToken)return;$('empty').firstElementChild.textContent='この画像を表示できません';tell('画像の形式やファイルを確認してください。この画像は未ラベルのまま残ります。');};
  nextImage.src=url;
}
async function selectImages(event) {
  const chosen=Array.from(event.target.files).filter(f=>f.type.startsWith('image/') || /\.(png|jpe?g|webp|bmp|gif|avif)$/i.test(f.name));
  event.target.value='';
  if(!chosen.length)return tell('表示できる画像を選んでください。動画は抽出した画像を選択してください。');
  if(state)save();
  const token=++selectionToken;busy=true;update();
  chosen.sort((a,b)=>(a.webkitRelativePath||a.name).localeCompare(b.webkitRelativePath||b.name,'ja',{numeric:true}));
  try {
    const manifest=[];const kept=[];const seen=new Set();
    for(let i=0;i<chosen.length;i++) {
      tell(`画像の内容を確認中 ${i+1} / ${chosen.length}`);
      const f=chosen[i];const sha=Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',await f.arrayBuffer())),x=>x.toString(16).padStart(2,'0')).join('');
      if(token!==selectionToken)return;
      const m={path:f.webkitRelativePath||f.name,size:f.size,sha256:sha};
      if(!seen.has(idOf(m))){manifest.push(m);kept.push(f);seen.add(idOf(m));}
    }
    const hash=Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',new TextEncoder().encode(JSON.stringify(manifest)))),x=>x.toString(16).padStart(2,'0')).join('');
    if(token!==selectionToken)return;
    files=kept;cacheKey=CACHE_PREFIX+hash;
    state={schema_version:'frame-annotation-v1',project_id:hash,created_at:new Date().toISOString(),manifest,scope:null,roi:null,labels:{},notes:{},index:0,keys:{present:'1',absent:'2',uncertain:'3'}};
    let restored=false;
    try {const saved=localStorage.getItem(cacheKey);if(saved){state=validateProject(JSON.parse(saved),manifest);restored=true;}} catch {tell('自動保存を復元できませんでした。保存済みJSONがあれば読み込んでください。');}
    drawing=false;points=[];syncKeys();$('dataset').textContent=`${files.length} 枚（ファイル名順）`;
    tell(restored?'前回の作業を復元しました。':'画像を読み込みました。ROIを描くか、全画面を選んでください。');
    save();show();
  } catch(e){tell('画像を読み込めませんでした：'+e.message);}
  finally{if(token===selectionToken){busy=false;update();}}
}
function annotate(label) {
  if($(label).disabled)return;
  const id=idOf(current()), note=$('note').value.trim();
  if(label==='uncertain' && !note){tell('判定不能の理由をメモへ入力してください。');$('note').focus();return;}
  state.notes[id]=note;
  state.labels[id]={label,updated_at:new Date().toISOString(),width:image.naturalWidth,height:image.naturalHeight};
  tell(`${current().path}：${LABELS[label]}を保存しました。`);
  if($('autoNext').checked && state.index<files.length-1){state.index++;save();show();}else{save();update();}
}
function move(delta){if(!state||drawing||busy)return;state.index=Math.max(0,Math.min(files.length-1,state.index+delta));save();show();}
$('folder').onchange=selectImages;$('files').onchange=selectImages;
for(const k of Object.keys(LABELS))$(k).onclick=()=>annotate(k);
$('prev').onclick=()=>move(-1);$('next').onclick=()=>move(1);
$('note').oninput=()=>{if(!state)return;const id=idOf(current());state.notes[id]=$('note').value;if(state.labels[id]?.label==='uncertain'&&!$('note').value.trim()){delete state.labels[id];tell('理由が空になったため判定不能ラベルを解除しました。');}save();update();};
$('roiStart').onclick=()=>{drawing=true;points=[];draw();update();tell('ROIの頂点を順番にクリックしてください。');};
canvas.onclick=e=>{if(!drawing)return;const rect=canvas.getBoundingClientRect();points.push([(e.clientX-rect.left)/rect.width,(e.clientY-rect.top)/rect.height]);draw();update();};
$('roiFinish').onclick=()=>{const roi={points:points.map(p=>p.slice()),width:image.naturalWidth,height:image.naturalHeight};if(!validPolygon(roi))return tell('ROIは交差しない、面積のある多角形にしてください。描画取消でやり直せます。');state.roi=roi;state.scope='roi';drawing=false;save();draw();update();tell('共通ROIを設定しました。1＝あり、2＝なしで入力できます。');};
$('roiCancel').onclick=()=>{drawing=false;points=[];draw();update();};
$('fullFrame').onclick=()=>{state.scope='full_frame';state.roi=null;save();draw();update();tell('全画面で判定します。');};
$('applyKeys').onclick=()=>{const keys={present:$('keyPresent').value.toLowerCase(),absent:$('keyAbsent').value.toLowerCase(),uncertain:$('keyUncertain').value.toLowerCase()};if(!validKeys(keys))return tell('キーは重複しない英数字1文字ずつにしてください。');if(!state)return tell('先に画像を選択してください。');state.keys=keys;syncKeys();save();tell('キー割り当てを保存しました。');};
document.addEventListener('keydown',e=>{if(e.repeat||e.isComposing||e.ctrlKey||e.metaKey||e.altKey||['INPUT','TEXTAREA','SELECT'].includes(e.target.tagName))return;if(e.key==='ArrowLeft'){e.preventDefault();move(-1);}else if(e.key==='ArrowRight'){e.preventDefault();move(1);}else{const k=Object.keys(LABELS).find(k=>state?.keys[k]===e.key.toLowerCase());if(k){e.preventDefault();annotate(k);}}});
function download(content,type,ext){const url=URL.createObjectURL(new Blob([content],{type}));const a=document.createElement('a');a.href=url;a.download=`annotation-${new Date().toISOString().replace(/[:.]/g,'-')}.${ext}`;a.click();setTimeout(()=>URL.revokeObjectURL(url),5000);}
$('exportJson').onclick=()=>{if(state)download(JSON.stringify(state,null,2),'application/json','json');};
const csv=v=>'"'+String(v??'').replaceAll('"','""')+'"';
$('exportCsv').onclick=()=>{if(!state)return;const rows=[['project_id','path','sha256','scope','label','note','updated_at']];for(const m of state.manifest){const id=idOf(m),a=state.labels[id];rows.push([state.project_id,m.path,m.sha256,state.scope,a?.label||'',state.notes[id]||'',a?.updated_at||'']);}download('\uFEFF'+rows.map(r=>r.map(csv).join(',')).join('\r\n'),'text/csv;charset=utf-8','csv');};
$('importJson').onchange=async e=>{const file=e.target.files[0];e.target.value='';if(!file)return;if(!state||busy)return tell('先に元と同じ画像一式を選択してください。');try{const imported=validateProject(JSON.parse(await file.text()),state.manifest);if(hasLabels()&&!confirm('現在のラベルを保存済みJSONで置き換えます。現在の作業は書き出し済みですか？'))return;state=imported;drawing=false;syncKeys();save();show();tell('保存した作業を復元しました。');}catch(err){tell('読み込めません：'+err.message);}};
update();
