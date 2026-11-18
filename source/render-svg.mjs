// Rend un SVG en PNG, fond transparent, à l'échelle demandée. Usage : node render-svg.mjs <svg> <png> [échelle] [instant en ms]
// L'instant fige les animations CSS à ce moment-là : utile pour regarder une image précise d'une animation.
import { chromium } from 'playwright-core';
import fs from 'node:fs';

const [source, target, scale = '1', at = ''] = process.argv.slice(2);
const svg = fs.readFileSync(source, 'utf8');
const size = /viewBox="0 0 ([\d.]+) ([\d.]+)"/.exec(svg);
const [width, height] = [Number(size[1]), Number(size[2])];
const browser = await chromium.launch({ executablePath: process.env.CHROMIUM || '/usr/bin/chromium', headless: true, args: ['--no-sandbox', '--disable-dev-shm-usage'] });
const page = await browser.newPage({ viewport: { width: Math.ceil(width), height: Math.ceil(height) }, deviceScaleFactor: Number(scale) });
await page.setContent(`<!doctype html><html><body style="margin:0;background:transparent">${svg}</body></html>`);
if (at !== '') {
  await page.evaluate((ms) => { for (const animation of document.getAnimations()) { animation.pause(); animation.currentTime = ms; } }, Number(at));
}
await page.waitForTimeout(150);
await page.screenshot({ path: target, omitBackground: true, clip: { x: 0, y: 0, width, height } });
await browser.close();
console.log(`${target} : ${width}×${height} à l'échelle ${scale}`);
