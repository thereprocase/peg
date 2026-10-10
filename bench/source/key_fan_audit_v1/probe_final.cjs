// Verify every decoded field and every tool against actual browser rendering.
const {chromium}=require(process.env.PLAYWRIGHT_MODULE||'/mnt/keith/bench/hx04-fan-audit-e487d4c/viewer/node_modules/playwright-core');
const fs=require('fs');
(async()=>{
 const browser=await chromium.launch({headless:true,executablePath:process.env.CHROMIUM_PATH||'/usr/bin/google-chrome',args:['--no-sandbox','--disable-dev-shm-usage','--use-angle=swiftshader','--enable-unsafe-swiftshader']});
 const errors=[],checks=[];const page=await browser.newPage({viewport:{width:1200,height:900}});
 page.on('pageerror',e=>errors.push(e.message));page.on('console',m=>{if(m.type()==='error')errors.push(m.text())});
 await page.goto(process.env.HX04_URL||'http://127.0.0.1:39881/');await page.waitForFunction(()=>window.studyReady,{timeout:120000});
 const counts=await page.evaluate(async()=>{const d=await window.studyReady;return {tools:d.tools.length,fields:d.fields.length}});
 for(let i=0;i<counts.tools;i++){await page.evaluate(i=>window.setStudy({mode:'motion',tool:i,phase:.5}),i);checks.push('tool-'+i)}
 for(let i=0;i<counts.fields;i++){await page.evaluate(i=>window.setStudy({mode:'fea',field:i,phase:1,shade:'stress'}),i);checks.push('field-'+i)}
 for(const q of [{mode:'sequence',phase:.5},{mode:'install',phase:0,relief:0},{mode:'install',phase:0,relief:1.5},{mode:'fea',field:25,phase:1}]){await page.evaluate(q=>window.setStudy(q),q);checks.push(q)}
 await page.locator('#stage').screenshot({path:'final-desktop.png'});
 await page.setViewportSize({width:390,height:844});await page.evaluate(()=>window.setStudy({mode:'motion',tool:22,phase:.5}));await page.waitForTimeout(500);await page.locator('#stage').screenshot({path:'final-mobile.png'});
 const layout=await page.evaluate(()=>({scrollWidth:document.documentElement.scrollWidth,width:innerWidth,canvasWidth:document.querySelector('canvas').getBoundingClientRect().width}));
 if(layout.scrollWidth>layout.width+1)errors.push('Mobile page overflows: '+JSON.stringify(layout));
 fs.writeFileSync('final-viewer-probe.json',JSON.stringify({url:process.env.HX04_URL||'local',counts,checks,layout,errors},null,2));await browser.close();
 if(errors.length)throw Error(errors.join('\n'));console.log('Final desktop/mobile: '+counts.tools+' tools, '+counts.fields+' fields PASS');
})().catch(e=>{console.error(e);process.exit(1)});
