async page=>{
 const root=PROJECT_ROOT,errors=[];page.on('pageerror',e=>errors.push(e.message));
 await page.goto('about:blank');await page.goto('http://127.0.0.1:8765/video.html');
 await page.evaluate(()=>{for(const k of Object.keys(localStorage))if(k.startsWith('infant-video-interval-v1:'))localStorage.removeItem(k);});
 const file=root+'/data/local/video-smoke/synthetic.webm';
 await page.getByLabel('動画ファイルを選択',{exact:true}).setInputFiles(file);
 await page.waitForFunction(()=>!document.getElementById('fullFrame').disabled);
 await page.getByRole('button',{name:'全画面を使う',exact:true}).click();
 const add=async(start,end,button,note='')=>{await page.getByRole('spinbutton',{name:'開始（秒）'}).fill(String(start));await page.getByRole('spinbutton',{name:'終了（秒）'}).fill(String(end));await page.getByRole('textbox',{name:'区間のメモ（判定不能では必須）'}).fill(note);await page.getByRole('button',{name:button,exact:true}).click();};
 await add(0,2,'介入あり 1');await add(2,5,'介入なし 2');await add(5,await page.locator('#video').evaluate(v=>v.duration),'判定不能 3','test');
 let text=await page.locator('#frameRows').innerText();
 for(const s of ['6 / 6枚','2枚（33.3%）','3枚（50.0%）','1枚（16.7%）','40.0%：60.0%'])if(!text.includes(s))throw Error('Wrong frame counts: '+text);
 await page.getByRole('spinbutton',{name:'抽出レート'}).fill('2');await page.getByRole('button',{name:'反映',exact:true}).click();
 text=await page.locator('#frameRows').innerText();if(!text.includes('12 / 12枚')||!text.includes('4枚（33.3%）'))throw Error('FPS change failed');
 const jp=page.waitForEvent('download');await page.getByRole('button',{name:'作業を保存（JSON）'}).click();await(await jp).saveAs(root+'/data/local/video-smoke/counts.json');
 const cp=page.waitForEvent('download');await page.getByRole('button',{name:'区間を書き出す（CSV）'}).click();await(await cp).saveAs(root+'/data/local/video-smoke/counts.csv');
 await page.reload();await page.getByLabel('動画ファイルを選択',{exact:true}).setInputFiles(file);await page.waitForFunction(()=>document.getElementById('frameRows').innerText.includes('12 / 12枚'));
 // Inject a 7300-second data fixture to test long-duration layout/navigation only.
 // This is not a test of decoding or playback of a two-hour video.
 await page.evaluate(()=>{video.pause();state.source={...state.source,duration_s:7300};state.sampling={fps:1,origin_s:0};state.playhead_s=0;state.intervals=[{id:'a',start_s:0,end_s:1,label:'absent',note:''},{id:'b',start_s:3599,end_s:3601,label:'present',note:''},{id:'c',start_s:7200,end_s:7201,label:'uncertain',note:'test'}];setupWindows();$('scrub').min=bounds().start_s;$('scrub').max=bounds().end_s;render();});
 if(await page.getByRole('combobox',{name:'作業する範囲'}).inputValue()!=='0')throw Error('First hour not selected');
 text=await page.locator('#frameRows').innerText();if(!text.includes('2 / 3,600枚')||!text.includes('4 / 7,300枚'))throw Error('First-hour summary failed: '+text);
 await page.getByRole('button',{name:'次の1時間 →',exact:true}).click();
 text=await page.locator('#frameRows').innerText();if(!text.includes('1 / 3,600枚'))throw Error('Second-hour summary failed');
 if(await page.getByRole('slider',{name:'再生位置'}).getAttribute('min')!=='3600')throw Error('Second-hour seek bounds failed');
 await page.getByRole('button',{name:'次の1時間 →',exact:true}).click();text=await page.locator('#frameRows').innerText();if(!text.includes('1 / 100枚'))throw Error('Partial final hour failed');
 await page.getByRole('combobox',{name:'作業する範囲'}).selectOption('all');text=await page.locator('#frameRows').innerText();if((await page.locator('#frameRows tr').count())!==1||!text.includes('4 / 7,300枚'))throw Error('All-video summary failed');
 await page.getByRole('combobox',{name:'作業する範囲'}).selectOption('0');
 await page.screenshot({path:root+'/output/playwright/hour-count-smoke.png',fullPage:true});
 if(errors.length)throw Error(errors.join(';'));
 console.log('PASS: 1fps counts/shares, FPS change and restore, JSON/CSV, synthetic hour windows and partial final window; long-video decoding not tested');
 await page.goto('about:blank');await page.goto('http://127.0.0.1:8765/video.html');await page.evaluate(()=>{for(const k of Object.keys(localStorage))if(k.startsWith('infant-video-interval-v1:'))localStorage.removeItem(k);});
}
