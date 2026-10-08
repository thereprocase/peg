// node shots.cjs <iteration dir> : workbench-shaded review renders of installed/loaded/print GLBs.
const {chromium} = require('playwright-core');
const fs = require('node:fs/promises');
const path = require('node:path');
const DOCS = path.resolve(__dirname, '../../../../docs');
const dir = path.resolve(process.argv[2]);
const CHROME = process.env.LOCALAPPDATA + '/ms-playwright/chromium-1208/chrome-win64/chrome.exe';
const views = process.env.VIEWS ? JSON.parse(process.env.VIEWS) : [
  ['loaded', 'hero', '25deg 65deg auto'],
  ['installed', 'empty-hero', '25deg 65deg auto'],
  ['loaded', 'front', '0deg 80deg auto'],
  ['installed', 'front-low', '-20deg 100deg auto'],
  ['installed', 'left-end', '80deg 75deg auto'],
  ['installed', 'right-below', '-60deg 115deg auto'],
  ['installed', 'top-mouths', '10deg 25deg 60%'],
  ['print', 'print', '35deg 60deg auto'],
  ['print', 'print-bed', '200deg 120deg auto'],
];
(async () => {
  const browser = await chromium.launch({executablePath: CHROME, headless: true});
  const page = await browser.newPage({viewport: {width: 1000, height: 800}, deviceScaleFactor: 1});
  const errors = [];
  page.on('pageerror', e => errors.push(e.message));
  await page.route('http://hx.test/**', async route => {
    const u = new URL(route.request().url());
    if (u.pathname === '/index.html') return route.fulfill({contentType: 'text/html', body: `<html><head><script type="module" src="/gallery/vendor/model-viewer.min.js"></script>${process.env.NOWB ? "" : "<script defer src=\"/viewer/workbench.js\"></script>"}</head><body style="margin:0"><model-viewer id="m" style="width:1000px;height:800px" camera-controls></model-viewer></body></html>`});
    const file = u.pathname.startsWith('/models/') ? path.join(dir, u.pathname.slice(8)) : path.join(DOCS, u.pathname);
    const type = file.endsWith('.js') ? 'text/javascript' : file.endsWith('.glb') ? 'model/gltf-binary' : 'application/octet-stream';
    route.fulfill({body: await fs.readFile(file), contentType: type});
  });
  await page.goto('http://hx.test/index.html');
  await page.evaluate(() => customElements.whenDefined('model-viewer'));
  const out = path.join(dir, process.env.OUTDIR || 'shots'); await fs.mkdir(out, {recursive: true});
  for (const [model, name, orbit, target] of views) {
    await page.evaluate(({model, orbit, target}) => new Promise((resolve, reject) => {
      const v = document.getElementById('m');
      const t = setTimeout(() => reject(Error('timeout')), 30000);
      const go = () => { v.cameraOrbit = orbit; v.cameraTarget = (typeof target !== 'undefined' && target) || 'auto auto auto'; v.jumpCameraToGoal(); clearTimeout(t); resolve(); };
      if (v.dataset.current === model) return go();
      v.addEventListener('load', () => { v.dataset.current = model; go(); }, {once: true});
      v.src = '/models/' + model + '.glb?' + Date.now();
    }), {model, orbit, target});
    if (!process.env.NOWB) await page.waitForFunction(() => Number(document.getElementById('m').dataset.workbenchMaterials) > 0); else await page.waitForTimeout(1500);
    await page.waitForTimeout(400);
    await page.locator('model-viewer').screenshot({path: path.join(out, name + '.png')});
    console.log(name);
  }
  await browser.close();
  if (errors.length) { console.error(errors.join('\n')); process.exitCode = 1; }
})();
