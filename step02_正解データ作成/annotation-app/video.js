'use strict';
const $=id=>document.getElementById(id), M=VideoAnnotations;
const LABELS={present:'介入あり',absent:'介入なし',uncertain:'判定不能'};
const video=$('video'), canvas=$('overlay'), ctx=canvas.getContext('2d');
let state=null,cacheKey='',blobUrl=null,ready=false,drawing=false,points=[],selected=null,drag=null,loading=0,raf=null;
function tell(text,error=false){$('message').textContent=text;$('message').classList.toggle('error',error);}
const duration=()=>state?.source.duration_s||0;
const timeString=t=>{const ms=Math.round(Math.max(0,t)*1000),h=Math.floor(ms/3600000),m=Math.floor(ms/60000)%60,s=Math.floor(ms/1000)%60;return [h,m,s].map(v=>String(v).padStart(2,'0')).join(':')+'.'+String(ms%1000).padStart(3,'0');};
function bounds(){const v=$('workWindow').value;if(!state||v==='all')return {start_s:0,end_s:duration()};return M.hourWindows(duration())[Number(v)]||{start_s:0,end_s:duration()};}
const viewLength=()=>Math.max(.001,bounds().end_s-bounds().start_s);
function setupWindows(){const list=$('workWindow');list.replaceChildren();const all=document.createElement('option');all.value='all';all.textContent='動画全体';list.append(all);for(const [i,w]of M.hourWindows(duration()).entries()){const opt=document.createElement('option');opt.value=i;opt.textContent=`${i+1}枠目：${timeString(w.start_s)}〜${timeString(w.end_s)}`;list.append(opt);}list.value=duration()>3600?String(Math.min(Math.floor(state.playhead_s/3600),M.hourWindows(duration()).length-1)):'all';$('fps').value=state.sampling?.fps||1;}
function frameTable(){const fps=state.sampling?.fps||1,w=bounds(),rows=$('frameRows');rows.replaceChildren();const ranges=$('workWindow').value==='all'?[['動画全体',0,duration()]]:[['この1時間枠',w.start_s,w.end_s],['動画全体',0,duration()]];const pct=n=>n===null?'—':(n*100).toFixed(1)+'%';for(const [name,start,end]of ranges){const st=M.frameStats(state.intervals,duration(),fps,start,end),tr=document.createElement('tr');const texts=[name,`${st.annotated.toLocaleString()} / ${st.total.toLocaleString()}枚（${pct(st.coverage)}完了）`,...['present','absent','uncertain'].map(k=>`${st[k].toLocaleString()}枚（${pct(st.shares[k])}）`),`${st.pending.toLocaleString()}枚`,`${pct(st.positive_ratio)}：${pct(st.negative_ratio)}`];for(const text of texts){const td=document.createElement('td');td.textContent=text;tr.append(td);}rows.append(tr);}}
function changeWindow(){if(!ready||drawing)return;video.pause();drag=null;const w=bounds();$('scrub').min=w.start_s;$('scrub').max=w.end_s;$('zoom').value='1';$('timeline').style.width='100%';$('timelineViewport').scrollLeft=0;seek(w.start_s);resetEditor();tell('作業範囲を切り替えました。ラベル区間はこれまでどおり自由な長さで指定できます。');}
const seconds=x=>x.toFixed(2)+'秒';
function save(){if(!state||!cacheKey)return;state.sampling=state.sampling||{fps:1,origin_s:0};state.playhead_s=Math.min(duration(),Math.max(0,video.currentTime||0));try{localStorage.setItem(cacheKey,JSON.stringify(state));$('saveStatus').textContent='ブラウザへ自動保存済み。終了前にJSONも保存してください。';}catch{$('saveStatus').textContent='自動保存できません。必ずJSONを保存してください。';}}
function fit(){if(!ready)return;const box=$('videoStage'),w=Math.min(box.clientWidth,box.clientHeight*state.source.width/state.source.height);$('videoShell').style.width=w+'px';$('videoShell').style.height=w*state.source.height/state.source.width+'px';drawRoi();}
new ResizeObserver(fit).observe($('videoStage'));
function drawRoi(){if(!ready)return;canvas.width=state.source.width;canvas.height=state.source.height;ctx.clearRect(0,0,canvas.width,canvas.height);const p=drawing?points:state.roi?.points;if(!p?.length)return;const scale=Math.max(1,canvas.width/700);ctx.strokeStyle='#63f4b2';ctx.fillStyle='#63f4b218';ctx.lineWidth=2*scale;ctx.beginPath();for(let i=0;i<p.length;i++)ctx[i?'lineTo':'moveTo'](p[i][0]*canvas.width,p[i][1]*canvas.height);if(!drawing)ctx.closePath();ctx.stroke();if(!drawing)ctx.fill();for(const a of p){ctx.fillStyle='#63f4b2';ctx.beginPath();ctx.arc(a[0]*canvas.width,a[1]*canvas.height,3*scale,0,Math.PI*2);ctx.fill();}}
function fields(){return {start_s:$('start').value===''?null:Number($('start').value),end_s:$('end').value===''?null:Number($('end').value)};}
function setTimes(start,end){$('start').value=start===null?'':start.toFixed(6);$('end').value=end===null?'':end.toFixed(6);drawDraft();}
function drawDraft(){const {start_s:a,end_s:b}=fields(),valid=ready&&a!==null&&b!==null&&a>=0&&b>a&&b<=duration()&&b>bounds().start_s&&a<bounds().end_s;$('draft').style.display=valid?'block':'none';if(valid){$('draft').style.left=((Math.max(a,bounds().start_s)-bounds().start_s)/viewLength()*100)+'%';$('draft').style.width=((Math.min(b,bounds().end_s)-Math.max(a,bounds().start_s))/viewLength()*100)+'%';}}
function updateClock(){if(!ready)return;$('clock').textContent=timeString(video.currentTime)+' / '+timeString(duration());$('scrub').value=video.currentTime;const w=bounds();$('playhead').style.left=(Math.max(0,Math.min(1,(video.currentTime-w.start_s)/viewLength()))*100)+'%';if(!video.paused&&video.currentTime>=w.end_s){video.pause();video.currentTime=w.end_s;}}
function update(){
 const enabled=ready&&!drawing;
 for(const id of ['play','scrub','markIn','markOut','toEnd','back','forward','start','end','speed','step','zoom','newInterval','workWindow','fps','applyFps'])$(id).disabled=!enabled;
 for(const k of Object.keys(LABELS))$(k).disabled=!enabled||!state?.scope;
 for(const id of ['exportJson','exportCsv'])$(id).disabled=!ready;
 $('roiStart').disabled=!ready||drawing||!!state?.intervals.length;$('fullFrame').disabled=$('roiStart').disabled;
 $('roiFinish').disabled=!drawing||points.length<3;$('roiCancel').disabled=!drawing;
 $('deleteInterval').disabled=!enabled||!selected;
 canvas.classList.toggle('drawing',drawing);
 $('scope').textContent=drawing?`頂点 ${points.length} 個。囲み終えたらROI確定` : state?.scope==='roi'?'共通ROI内を判定（緑の枠）':state?.scope==='full_frame'?'全画面を判定':'判定範囲を設定してください';
 $('editHeading').textContent=selected?'選択した区間を編集':'新しい区間';
 if(!state){$('frameRows').replaceChildren();return;}
 const w=bounds();$('windowLabel').textContent=`表示範囲：${timeString(w.start_s)}〜${timeString(w.end_s)}（元動画の時刻）`;$('prevWindow').disabled=!enabled||$('workWindow').value==='all'||Number($('workWindow').value)===0;$('nextWindow').disabled=!enabled||$('workWindow').value==='all'||Number($('workWindow').value)>=M.hourWindows(duration()).length-1;
 const stats=M.stats(state.intervals,duration());for(const k of Object.keys(LABELS))$('seconds'+k[0].toUpperCase()+k.slice(1)).textContent=seconds(stats[k]);
 $('secondsPending').textContent=seconds(stats.pending);$('ratio').textContent=stats.positive_ratio===null?'—':(100*stats.positive_ratio).toFixed(1)+'%';const visibleCount=state.intervals.filter(a=>a.end_s>w.start_s&&a.start_s<w.end_s).length;$('intervalCount').textContent=$('workWindow').value==='all'?state.intervals.length+'件':visibleCount+'件（動画全体 '+state.intervals.length+'件）';
 frameTable();drawDraft();updateClock();
}
function resetEditor(){selected=null;$('note').value='';setTimes(null,null);render();}
function selectInterval(a){video.pause();selected=a.id;$('note').value=a.note;setTimes(a.start_s,a.end_s);seek(a.start_s);render();}
function render(){
 $('segments').replaceChildren();$('rows').replaceChildren();
 if(state)for(const a of state.intervals){
  const w=bounds();if(a.end_s<=w.start_s||a.start_s>=w.end_s)continue;
  const el=document.createElement('div');el.className='segment '+a.label+(a.id===selected?' selected':'');el.style.left=(Math.max(a.start_s,w.start_s)-w.start_s)/viewLength()*100+'%';el.style.width=(Math.min(a.end_s,w.end_s)-Math.max(a.start_s,w.start_s))/viewLength()*100+'%';el.setAttribute('role','button');el.tabIndex=0;el.setAttribute('aria-label',`${LABELS[a.label]} ${timeString(a.start_s)}から${timeString(a.end_s)}`);
  const caption=document.createElement('span');caption.className='caption';caption.textContent=LABELS[a.label];el.append(caption);
  for(const side of ['left','right']){const grip=document.createElement('span');grip.className='handle '+side;grip.dataset.side=side;if((side==='left'&&a.start_s<w.start_s)||(side==='right'&&a.end_s>w.end_s))grip.style.display='none';el.append(grip);}
  el.onpointerdown=e=>{e.stopPropagation();if(!ready||drawing)return;if(e.target.dataset.side&&selected===a.id){video.pause();drag={type:e.target.dataset.side,old:a,start:a.start_s,end:a.end_s};el.setPointerCapture(e.pointerId);}else selectInterval(a);};
  el.onpointermove=e=>{if(drag?.old?.id===a.id){const t=timelineTime(e);if(drag.type==='left')drag.start=Math.min(t,drag.end-0.001);else drag.end=Math.max(t,drag.start+0.001);setTimes(Math.max(0,drag.start),Math.min(duration(),drag.end));}};
  el.onpointerup=e=>{if(drag?.old?.id!==a.id)return;const old=drag.old;drag=null;const f=fields();try{replace({...old,...f,updated_at:new Date().toISOString()},'resize');tell('区間の端を変更しました。');}catch(err){setTimes(old.start_s,old.end_s);tell(err.message,true);}render();};
  el.onpointercancel=()=>{drag=null;setTimes(a.start_s,a.end_s);};el.onkeydown=e=>{if(e.key==='Enter'){e.stopPropagation();selectInterval(a);}};$('segments').append(el);
  const tr=document.createElement('tr');if(selected===a.id)tr.className='selected';
  for(const v of [timeString(a.start_s),timeString(a.end_s),seconds(a.end_s-a.start_s),LABELS[a.label],a.note]){const td=document.createElement('td');td.textContent=v;tr.append(td);}const td=document.createElement('td'),button=document.createElement('button');button.textContent='選択';button.onclick=()=>selectInterval(a);td.append(button);tr.append(td);$('rows').append(tr);
 }
 update();
}
function replace(a,action){
 const next=M.upsert(state.intervals,a,duration());const old=state.intervals.find(x=>x.id===a.id)||null;
 state.history.push({action,at:new Date().toISOString(),before:old,after:a});state.intervals=next;save();
}
function label(k){if($(k).disabled)return;const f=fields();if(!selected&&f.start_s!==null&&f.end_s!==null&&(f.start_s<bounds().start_s||f.end_s>bounds().end_s))return tell('新しい区間は表示中の時間枠内にしてください。動画全体表示なら枠をまたいで指定できます。',true);if(f.start_s===null||f.end_s===null)return tell('Iで開始、Oで終了を指定するか、タイムラインをドラッグしてください。',true);
 try{const a={id:selected||crypto.randomUUID(),...f,label:k,note:$('note').value.trim(),updated_at:new Date().toISOString()};replace(a,selected?'edit':'add');selected=null;$('note').value='';setTimes(a.end_s,null);render();tell(`${timeString(a.start_s)}〜${timeString(a.end_s)}を「${LABELS[k]}」で保存しました。次の開始は直前の終了位置です。`);}catch(e){tell(e.message,true);}}
function seek(t){if(ready)video.currentTime=Math.min(bounds().end_s,Math.max(bounds().start_s,t));}
function timelineTime(e){const r=$('timeline').getBoundingClientRect();return bounds().start_s+Math.max(0,Math.min(viewLength(),(e.clientX-r.left)/r.width*viewLength()));}
$('timeline').onpointerdown=e=>{if(!ready||drawing)return;video.pause();selected=null;$('note').value='';const t=timelineTime(e);drag={type:'new',start:t};$('timeline').setPointerCapture(e.pointerId);setTimes(t,t);update();};
$('timeline').onpointermove=e=>{if(drag?.type==='new'){const t=timelineTime(e);setTimes(Math.min(t,drag.start),Math.max(t,drag.start));}};
$('timeline').onpointerup=e=>{if(drag?.type!=='new')return;const t=timelineTime(e),a=drag.start;drag=null;if(Math.abs(t-a)<0.03){seek(t);setTimes(null,null);}else setTimes(Math.min(t,a),Math.max(t,a));render();};
$('timeline').onpointercancel=()=>{drag=null;setTimes(null,null);};
async function toggle(){if(!ready||drawing)return;if(video.paused){try{await video.play();}catch{tell('動画を再生できません。別のブラウザ対応形式を試してください。',true);}}else video.pause();}
$('play').onclick=toggle;video.onclick=toggle;
video.onplay=()=>{$('play').textContent='Ⅱ 停止';const tick=()=>{updateClock();if(!video.paused)raf=requestAnimationFrame(tick);};cancelAnimationFrame(raf);raf=requestAnimationFrame(tick);};
video.onpause=()=>{$('play').textContent='▶ 再生';cancelAnimationFrame(raf);save();};
video.ontimeupdate=updateClock;video.onseeked=()=>{updateClock();save();};
video.onerror=()=>{ready=false;update();tell('この動画を再生できません。MP4（H.264）やWebMなど、ブラウザ対応形式を選んでください。',true);};
$('scrub').oninput=()=>seek(Number($('scrub').value));$('speed').onchange=()=>{video.playbackRate=Number($('speed').value);};
$('back').onclick=()=>seek(video.currentTime-Number($('step').value));$('forward').onclick=()=>seek(video.currentTime+Number($('step').value));
$('markIn').onclick=()=>{if(ready&&!drawing){$('start').value=video.currentTime.toFixed(6);drawDraft();}};
$('markOut').onclick=()=>{if(ready&&!drawing){$('end').value=video.currentTime.toFixed(6);drawDraft();}};
$('toEnd').onclick=()=>{if(ready){$('end').value=bounds().end_s;drawDraft();}};
$('start').oninput=drawDraft;$('end').oninput=drawDraft;$('newInterval').onclick=resetEditor;
for(const k of Object.keys(LABELS))$(k).onclick=()=>label(k);
$('deleteInterval').onclick=()=>{if(!selected)return;const old=state.intervals.find(a=>a.id===selected);state.history.push({action:'delete',at:new Date().toISOString(),before:old,after:null});state.intervals=state.intervals.filter(a=>a.id!==selected);save();resetEditor();tell('区間を削除しました。作業JSONに変更履歴を残しています。');};
$('zoom').onchange=()=>{$('timeline').style.width=Number($('zoom').value)*100+'%';const view=$('timelineViewport');view.scrollLeft=(video.currentTime-bounds().start_s)/viewLength()*$('timeline').clientWidth-view.clientWidth/2;};
$('roiStart').onclick=()=>{video.pause();drawing=true;points=[];drawRoi();update();};
canvas.onclick=e=>{if(!drawing)return;const r=canvas.getBoundingClientRect();points.push([(e.clientX-r.left)/r.width,(e.clientY-r.top)/r.height]);drawRoi();update();};
$('roiFinish').onclick=()=>{const roi={points:points.map(p=>p.slice()),width:state.source.width,height:state.source.height};if(!M.validPolygon(roi))return tell('交差しない、面積のあるROIを指定してください。',true);state.scope='roi';state.roi=roi;drawing=false;save();drawRoi();update();tell('ROIを動画全体へ適用しました。区間の開始と終了を指定してください。');};
$('roiCancel').onclick=()=>{drawing=false;points=[];drawRoi();update();};$('fullFrame').onclick=()=>{state.scope='full_frame';state.roi=null;save();drawRoi();update();};
document.onkeydown=e=>{if(e.repeat||e.isComposing||e.ctrlKey||e.metaKey||e.altKey||['INPUT','TEXTAREA','SELECT'].includes(e.target.tagName)||!ready||drawing)return;const key=e.key.toLowerCase();const actions={' ':toggle,'i':()=>$('markIn').click(),'o':()=>$('markOut').click(),'1':()=>label('present'),'2':()=>label('absent'),'3':()=>label('uncertain'),'arrowleft':()=>$('back').click(),'arrowright':()=>$('forward').click(),'escape':resetEditor};if(actions[key]){e.preventDefault();actions[key]();}};
async function hash(buffer){return Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',buffer)),b=>b.toString(16).padStart(2,'0')).join('');}
$('videoFile').onchange=async e=>{
 const file=e.target.files[0];e.target.value='';if(!file)return;
 video.pause();save();ready=false;state=null;cacheKey='';selected=null;drawing=false;points=[];drag=null;render();const ticket=++loading;
 tell('動画を読み込み中…');$('videoName').textContent=file.name;
 try{
  const sample=await new Blob([String(file.size),await file.slice(0,65536).arrayBuffer(),await file.slice(Math.max(0,file.size-65536)).arrayBuffer()]).arrayBuffer();const fingerprint=await hash(sample);if(ticket!==loading)return;
  if(blobUrl)URL.revokeObjectURL(blobUrl);blobUrl=URL.createObjectURL(file);
  const metadata=new Promise((resolve,reject)=>{video.onloadedmetadata=resolve;video.addEventListener('error',()=>reject(Error('ブラウザで再生できる形式か確認してください。')),{once:true});});
  video.src=blobUrl;video.load();await metadata;if(ticket!==loading)return;
  if(!Number.isFinite(video.duration)||video.duration<=0||!video.videoWidth)throw Error('有限の長さを持つ動画を選択してください。');
  const source={name:file.name,size:file.size,sample_fingerprint:fingerprint,duration_s:video.duration,width:video.videoWidth,height:video.videoHeight};
  cacheKey='infant-video-interval-v1:'+await hash(new TextEncoder().encode(JSON.stringify(source)));if(ticket!==loading)return;
  state={schema_version:'video-interval-v1',created_at:new Date().toISOString(),source,scope:null,roi:null,intervals:[],history:[],playhead_s:0};
  let restored=false,corrupt=false;try{const saved=localStorage.getItem(cacheKey);if(saved){state=M.validateProject(JSON.parse(saved),source);restored=true;}}catch{corrupt=true;cacheKey+=':recovered-'+Date.now();}
  ready=true;$('videoEmpty').hidden=true;$('videoShell').hidden=false;$('scrub').max=duration();video.currentTime=state.playhead_s;video.playbackRate=Number($('speed').value);$('zoom').value='1';$('timeline').style.width='100%';setupWindows();$('scrub').min=bounds().start_s;$('scrub').max=bounds().end_s;fit();resetEditor();save();tell(corrupt?'自動保存を復元できませんでした。保存済みJSONがあれば読み込んでください。元の自動保存は保持しています。':restored?'前回の区間とROIを復元しました。':'動画を読み込みました。ROIまたは全画面を設定してください。');
 }catch(err){if(ticket===loading){ready=false;tell(err.message,true);update();}}
};
function download(content,type,ext){const url=URL.createObjectURL(new Blob([content],{type})),a=document.createElement('a');a.href=url;a.download='video-annotation-'+new Date().toISOString().replace(/[:.]/g,'-')+'.'+ext;a.click();setTimeout(()=>URL.revokeObjectURL(url),5000);}
$('exportJson').onclick=()=>{if(state){save();download(JSON.stringify(state,null,2),'application/json','json');}};
const csv=v=>'"'+String(v??'').replaceAll('"','""')+'"';
$('exportCsv').onclick=()=>{if(!state)return;const rows=[['video_name','sample_fingerprint','scope','start_s','end_s','label','note','updated_at','sampling_fps','sample_origin_s','sample_count']];for(const a of state.intervals)rows.push([state.source.name,state.source.sample_fingerprint,state.scope,a.start_s,a.end_s,a.label,a.note,a.updated_at,state.sampling?.fps||1,0,M.frameCount(a.start_s,a.end_s,state.sampling?.fps||1)]);download('\uFEFF'+rows.map(r=>r.map(csv).join(',')).join('\r\n'),'text/csv;charset=utf-8','csv');};
$('importJson').onchange=async e=>{const file=e.target.files[0];e.target.value='';if(!file)return;if(!ready)return tell('先に元の動画を選択してください。',true);const current=state;try{const imported=M.validateProject(JSON.parse(await file.text()),current.source);if(state!==current)throw Error('動画が切り替わりました。読み込み直してください。');if(current.intervals.length&&!confirm('現在の区間をJSONの内容で置き換えます。現在の作業は書き出し済みですか？'))return;video.pause();state=imported;drawing=false;selected=null;setupWindows();$('scrub').min=bounds().start_s;$('scrub').max=bounds().end_s;seek(state.playhead_s);save();drawRoi();resetEditor();tell('区間とROIを復元しました。');}catch(err){tell('読み込めません：'+err.message,true);}};
$('workWindow').onchange=changeWindow;
$('prevWindow').onclick=()=>{if(!$('prevWindow').disabled){$('workWindow').value=Number($('workWindow').value)-1;changeWindow();}};
$('nextWindow').onclick=()=>{if(!$('nextWindow').disabled){$('workWindow').value=Number($('workWindow').value)+1;changeWindow();}};
$('applyFps').onclick=()=>{if(!ready)return;const fps=Number($('fps').value);if(!Number.isFinite(fps)||fps<=0||fps>120)return tell('fpsは0より大きく120以下の値にしてください。',true);state.history.push({action:'sampling',at:new Date().toISOString(),before:state.sampling||{fps:1,origin_s:0},after:{fps,origin_s:0}});state.sampling={fps,origin_s:0};save();update();tell('想定抽出枚数を再計算しました。区間ラベルは変更していません。');};
$('prevWindow').disabled=true;$('nextWindow').disabled=true;
window.addEventListener('pagehide',save);update();
