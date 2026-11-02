const assert=require('node:assert/strict');const M=require('../video-model.js');
const a=(id,start_s,end_s,label='present')=>({id,start_s,end_s,label,note:label==='uncertain'?'test':''});
let n=0;function test(name,fn){fn();n++;console.log('PASS',name);}
test('One hour at 1fps is 3600 samples',()=>assert.equal(M.frameCount(0,3600),3600));
test('Adjacent hour windows do not double-count boundary',()=>{assert.equal(M.frameCount(0,3600)+M.frameCount(3600,7200),7200);assert.equal(M.frameStats([a('a',3599,3601)],7200,1,3600,7200).present,1);});
test('Fractional boundaries count grid points, not rounded duration',()=>{assert.equal(M.frameCount(.2,1.2),1);assert.equal(M.frameCount(.1,.9),0);assert.equal(M.frameCount(0,.1),1);});
test('End is excluded, zero is included',()=>assert.equal(M.frameCount(0,6),6));
test('FPS scales the sampling grid',()=>{assert.equal(M.frameCount(0,3600,2),7200);assert.equal(M.frameCount(0,3600,.5),1800);});
test('Annotated includes uncertain, binary shares exclude it',()=>{const s=M.frameStats([a('a',0,2),a('b',2,5,'absent'),a('c',5,6,'uncertain')],10);assert.equal(s.annotated,6);assert.equal(s.pending,4);assert.equal(s.positive_ratio,.4);assert.equal(s.negative_ratio,.6);assert.equal(s.shares.uncertain,1/6);});
test('Unsampled labelled interval does not fabricate a frame',()=>{const s=M.frameStats([a('a',.1,.9)],1);assert.equal(s.annotated,0);assert.equal(s.pending,1);assert.equal(s.positive_ratio,null);});
test('Cross-hour intervals contribute to both views with no duplication',()=>{const x=[a('a',3500.5,3700.5)];assert.equal(M.frameStats(x,7200,1,0,3600).present+M.frameStats(x,7200,1,3600,7200).present,M.frameStats(x,7200).present);});
test('Last hour may be partial',()=>assert.deepEqual(M.hourWindows(7300),[{start_s:0,end_s:3600},{start_s:3600,end_s:7200},{start_s:7200,end_s:7300}]));
test('Exact hour has no empty final page',()=>assert.equal(M.hourWindows(7200).length,2));
test('Invalid rate rejected',()=>{for(const f of [0,-1,NaN,Infinity])assert.throws(()=>M.frameCount(0,1,f));});
test('Formula matches enumerated samples on fractional windows',()=>{for(let i=0;i<150;i++){const start=i*.031,end=start+.48,fps=[.5,1,2,3][i%4];let count=0;for(let k=0;k<40;k++)if(start<=k/fps&&k/fps<end)count++;assert.equal(M.frameCount(start,end,fps),count);}});
console.log(n+' frame-count tests passed');
