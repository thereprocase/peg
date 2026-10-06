// Serve docs locally, then run with Playwright available via PLAYWRIGHT_MODULE.
// Rebuild the current collection's PNG previews with the shared viewer shader.
const {chromium} = require(process.env.PLAYWRIGHT_MODULE || 'playwright');
const fs = require('node:fs/promises');
const path = require('node:path');
(async () => {
  const root = path.resolve(__dirname, '..');
  const base = process.env.PEG_PREVIEW_URL || 'http://localhost:39879/';
  const catalog = JSON.parse(await fs.readFile(path.join(root, 'docs/gallery/current-pegs/catalog.json')));
  const browser = await chromium.launch({headless: true, executablePath: process.env.CHROMIUM_PATH || '/usr/bin/chromium', args: ['--no-sandbox']});
  try {
    const page = await browser.newPage({viewport: {width: 800, height: 640}, deviceScaleFactor: 1});
    const errors = [];
    page.on('pageerror', error => errors.push(error.message));
    page.on('console', message => { if (message.type() === 'error') errors.push(message.text()); });
    await page.route('**/workbench-preview.html', route => route.fulfill({contentType: 'text/html', body: `<html><head><script type="module" src="${base}gallery/vendor/model-viewer.min.js"></script><script defer src="${base}viewer/workbench.js"></script></head><body style="margin:0"><model-viewer id="model" style="width:800px;height:640px" camera-controls></model-viewer></body></html>`}));
    await page.goto(new URL('workbench-preview.html', base).href);
    await page.evaluate(() => customElements.whenDefined('model-viewer'));
    for (const part of catalog.parts) {
      for (const pose of ['installed', 'print']) {
        await page.evaluate(({part, pose}) => new Promise((resolve, reject) => {
          const viewer = document.getElementById('model');
          const timer = setTimeout(() => reject(Error('Model load timed out: ' + part.id)), 30000);
          viewer.addEventListener('load', () => { clearTimeout(timer); resolve(); }, {once: true});
          viewer.cameraOrbit = pose === 'print' ? '35deg 60deg auto' : '145deg 70deg auto';
          viewer.src = new URL('gallery/current-pegs/' + part.assets[pose + '_glb'], location.href).href;
        }), {part, pose});
        await page.waitForFunction(() => Number(document.getElementById('model').dataset.workbenchMaterials) > 0);
        await page.waitForTimeout(180);
        await page.evaluate(() => document.getElementById('model').jumpCameraToGoal());
        await page.waitForTimeout(60);
        const png = await page.locator('model-viewer').screenshot();
        const target = path.join(root, 'docs/gallery/current-pegs', part.assets[pose + '_png']);
        await fs.writeFile(target, png);
        if (pose === 'installed') await fs.writeFile(path.join(root, 'docs/gallery/current-pegs', part.assets.preview_png), png);
      }
      console.log(part.id);
    }
    if (errors.length) throw Error(errors.join('\n'));
  } finally { await browser.close(); }
})().catch(error => {console.error(error); process.exitCode = 1;});
