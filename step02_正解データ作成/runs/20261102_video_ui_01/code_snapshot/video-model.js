/* Local interval data model. Seconds refer to original media time. */
(function(root) {
'use strict';
const labels=['present','absent','uncertain'];
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

function validateInterval(a, duration) {
 if(!a || typeof a.id!=='string' || !a.id || !labels.includes(a.label) || typeof a.note!=='string') throw Error('区間の形式が不正です。');
 if(!Number.isFinite(a.start_s)||!Number.isFinite(a.end_s)||a.start_s<0||a.start_s>=a.end_s||a.end_s>duration) throw Error('区間は 0 ≤ 開始 < 終了 ≤ 動画長 にしてください。');
 if(a.label==='uncertain'&&!a.note.trim()) throw Error('判定不能には理由を入力してください。');
}
function validateIntervals(intervals,duration) {
 if(!Array.isArray(intervals)||!Number.isFinite(duration)||duration<=0)throw Error('動画または区間の形式が不正です。');
 const sorted=[...intervals].sort((a,b)=>a.start_s-b.start_s);
 const ids=new Set();let previous=0;
 for(const a of sorted){validateInterval(a,duration);if(ids.has(a.id))throw Error('区間IDが重複しています。');ids.add(a.id);if(a.start_s<previous)throw Error('既存の区間と重なっています。端を調整するか、既存区間を編集してください。');previous=a.end_s;}
 return sorted;
}
function upsert(intervals, candidate, duration) {
 return validateIntervals([...intervals.filter(a=>a.id!==candidate.id),candidate],duration);
}
function stats(intervals,duration) {
 const sums={present:0,absent:0,uncertain:0};
 for(const a of validateIntervals(intervals,duration))sums[a.label]+=a.end_s-a.start_s;
 const binary=sums.present+sums.absent;
 return {...sums,pending:Math.max(0,duration-binary-sums.uncertain),positive_ratio:binary?sums.present/binary:null};
}
function validateProject(s,source) {
 if(!s||s.schema_version!=='video-interval-v1'||!s.source||!Array.isArray(s.intervals)||!Array.isArray(s.history))throw Error('動画区間用の作業JSONを選択してください。');
 for(const k of ['name','size','sample_fingerprint','duration_s','width','height'])if(s.source[k]!==source[k])throw Error('保存データと選択した動画が一致しません。');
 if(![null,'roi','full_frame'].includes(s.scope))throw Error('判定範囲が不正です。');
 if(s.scope==='roi'?(!validPolygon(s.roi)||s.roi.width!==source.width||s.roi.height!==source.height):s.roi!==null)throw Error('ROIが不正です。');
 if(s.intervals.length&&!s.scope)throw Error('判定範囲がありません。');
 validateIntervals(s.intervals,source.duration_s);
 if(!Number.isFinite(s.playhead_s)||s.playhead_s<0||s.playhead_s>source.duration_s)throw Error('再生位置が不正です。');
 return s;
}
const api={validPolygon,validateInterval,validateIntervals,upsert,stats,validateProject};
root.VideoAnnotations=api;
if(typeof module!=='undefined')module.exports=api;
})(globalThis);
