"""Create a synthetic browser-recorded WebM and add its test duration to EBML Info."""
import json
import struct
import subprocess
from pathlib import Path

root=Path(__file__).resolve().parents[3]
folder=root/'data/local/video-smoke'
folder.mkdir(parents=True, exist_ok=True)
code='''async page=>{
 const pending=page.waitForEvent('download');
 await page.evaluate(async()=>{
  const canvas=document.createElement('canvas');canvas.width=640;canvas.height=480;
  const ctx=canvas.getContext('2d'), stream=canvas.captureStream(10), chunks=[];
  const recorder=new MediaRecorder(stream,{mimeType:'video/webm;codecs=vp8'});
  recorder.ondataavailable=e=>chunks.push(e.data);
  const finished=new Promise(resolve=>recorder.onstop=resolve);recorder.start();
  const timer=setInterval(()=>{ctx.fillStyle='#d7ddd5';ctx.fillRect(0,0,640,480);ctx.strokeStyle='#315a49';ctx.lineWidth=5;ctx.strokeRect(90,60,460,360);ctx.fillStyle='#a95438';ctx.fillRect(120+(Date.now()%200),170,90,60);},100);
  await new Promise(r=>setTimeout(r,6200));recorder.stop();await finished;clearInterval(timer);stream.getTracks().forEach(t=>t.stop());
  const url=URL.createObjectURL(new Blob(chunks,{type:'video/webm'})),a=document.createElement('a');a.href=url;a.download='synthetic.webm';a.click();
 });
 await(await pending).saveAs(OUTPUT_PATH);
}'''.replace('OUTPUT_PATH',json.dumps(str(folder/'recorded.webm')))
result=subprocess.run([str(Path.home()/'.codex/skills/playwright/scripts/playwright_cli.sh'),'-s=videoannotation','run-code',code],cwd=root,capture_output=True,text=True)
if result.returncode:raise RuntimeError(result.stdout+result.stderr)
data=(folder/'recorded.webm').read_bytes()
def vint(data,pos,identifier=False):
    n=1
    while n<=8 and not data[pos] & (1 << (8-n)):n+=1
    if n>8:raise ValueError('Invalid EBML')
    raw=int.from_bytes(data[pos:pos+n],'big')
    return (raw if identifier else raw & ((1 << (7*n))-1)),n
pos=data.index(bytes.fromhex('1549a966'))
size,n=vint(data,pos+4)
end=pos+4+n+size
# TimecodeScale is 1,000,000 ns in MediaRecorder output; duration is milliseconds.
info=data[pos+4+n:end]
scale_pos=info.find(bytes.fromhex('2ad7b1'))
scale=1000000
if scale_pos>=0:
    value_len,k=vint(info,scale_pos+3)
    scale=int.from_bytes(info[scale_pos+3+k:scale_pos+3+k+value_len],'big')
addition=bytes.fromhex('448988')+struct.pack('>d',6_000_000_000/scale)
new_size=size+len(addition)
if new_size >= (1 << (7*n))-1:raise ValueError('Info header too small')
encoded=((1 << (7*n))|new_size).to_bytes(n,'big')
# Chromium records an unknown-length Segment, so no parent length needs adjustment.
seg=data.index(bytes.fromhex('18538067')); seg_size,seg_n=vint(data,seg+4)
finite_segment = seg_size != (1 << (7*seg_n))-1
output=data[:pos+4]+encoded+info+addition+data[end:]
if finite_segment:
    output=output[:seg+4]+((1 << (7*seg_n))| (seg_size+len(addition))).to_bytes(seg_n,'big')+output[seg+4+seg_n:]
(folder/'synthetic.webm').write_bytes(output)
print('Synthetic WebM ready:',len(output),'bytes; declared duration 6 seconds')
