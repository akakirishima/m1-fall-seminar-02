const assert=require('node:assert/strict');
const M=require('../video-model.js');
const a=(id,start_s,end_s,label='present',note='')=>({id,start_s,end_s,label,note});
let passed=0;
function test(name,fn){fn();passed++;console.log('PASS',name);}
test('Adjacent half-open intervals are allowed',()=>assert.equal(M.validateIntervals([a('a',0,2),a('b',2,4)],10).length,2));
test('No overlap across labels',()=>assert.throws(()=>M.upsert([a('a',0,2)],a('b',1,4,'absent'),10),/重な/));
test('Resize collision leaves original unchanged',()=>{const x=[a('a',0,2),a('b',3,4)];assert.throws(()=>M.upsert(x,a('b',1,4),10));assert.equal(x[1].start_s,3);});
test('Editing replaces one interval',()=>assert.equal(M.upsert([a('a',0,2)],a('a',1,3,'absent'),10).length,1));
test('Untouched gaps remain unannotated',()=>assert.equal(M.stats([a('a',2,4)],10).pending,8));
test('Ratio uses seconds, excludes uncertain and gaps',()=>{const s=M.stats([a('a',0,2),a('b',2,8,'absent'),a('c',8,9,'uncertain','blur')],10);assert.equal(s.positive_ratio,0.25);assert.equal(s.pending,1);});
test('No binary labels yields null ratio',()=>assert.equal(M.stats([],10).positive_ratio,null));
test('Zero, reversed, negative, beyond duration and NaN rejected',()=>{for(const [x,y]of [[2,2],[3,2],[-1,2],[0,11],[NaN,2]])assert.throws(()=>M.validateInterval(a('a',x,y),10));});
test('Uncertain requires reason',()=>assert.throws(()=>M.validateInterval(a('a',0,2,'uncertain'),10),/理由/));
test('Unknown label rejected',()=>assert.throws(()=>M.validateInterval(a('a',0,2,'other'),10)));
test('Duplicate IDs rejected',()=>assert.throws(()=>M.validateIntervals([a('a',0,2),a('a',3,4)],10)));
test('Self-intersecting ROI rejected',()=>assert.equal(M.validPolygon({width:640,height:480,points:[[0,0],[1,1],[1,0],[0,1]]}),false));
test('Different source rejected on restore',()=>assert.throws(()=>M.validateProject({schema_version:'video-interval-v1',source:{name:'x'},intervals:[],history:[]},{name:'y'}),/一致/));
console.log(`${passed} tests passed`);
