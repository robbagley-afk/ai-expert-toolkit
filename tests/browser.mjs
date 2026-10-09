import {chromium} from 'playwright';
import assert from 'node:assert/strict';
const base=process.env.TOOLKIT_BASE||'http://127.0.0.1:8767/';
const browser=await chromium.launch({headless:true});
try {
 const ctx=await browser.newContext();const page=await ctx.newPage();const errors=[];page.on('pageerror',e=>errors.push(String(e)));
 for(const width of [375,1440]){await page.setViewportSize({width,height:950});for(const path of ['','chatgpt-quick-start-guide/']){
  await page.goto(base+path);assert.equal(await page.locator('h1').count(),1);
  assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));
  await page.screenshot({path:`./toolkit-qa-${path?'guide':'home'}-${width}.png`,fullPage:true});
 }}
 const boxes=page.locator('input[data-check]');assert.equal(await boxes.count(),8);await boxes.first().focus();await page.keyboard.press('Space');assert.equal(await page.locator('[data-progress]').textContent(),'1 of 8 complete');await page.reload();assert.equal(await boxes.first().isChecked(),true);
 for(const bad of ['{bad','[]','{"unknown":true,"controls":"yes","work":true}']){await page.evaluate(v=>localStorage.setItem('toolkit-guide-checklist-v1',v),bad);await page.reload();assert.equal(await boxes.first().isChecked(),false);assert.equal(await page.locator('[data-progress]').textContent(),bad.includes('work')?'1 of 8 complete':'0 of 8 complete');}
 await ctx.close();const denied=await browser.newContext();await denied.addInitScript(()=>Object.defineProperty(window,'localStorage',{get(){throw Error('denied')}}));const p=await denied.newPage();await p.goto(base+'chatgpt-quick-start-guide/');await p.locator('input[data-check]').first().check();assert.equal(await p.locator('[data-progress]').textContent(),'1 of 8 complete');await denied.close();assert.deepEqual(errors,[]);console.log('PASS: mobile/desktop, persistence, corrupt/unknown storage, keyboard, denied storage, no page errors');
} finally { await browser.close(); }
