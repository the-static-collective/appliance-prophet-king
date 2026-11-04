#!/usr/bin/env python3
"""Offline GUI smoke with Chromium/Playwright, optional (not required by generator)."""
import asyncio, json
from pathlib import Path
from playwright.async_api import async_playwright

HTML=Path(__file__).resolve().parents[1]/'tweak.html'

async def main():
    async with async_playwright() as p:
        browser=await p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
        page=await browser.new_page(accept_downloads=True,viewport={'width':425,'height':850})
        errors=[]
        page.on('pageerror',lambda err:errors.append(str(err)))
        await page.set_content(HTML.read_text('utf-8'))
        assert await page.locator('#num_mouth_inner_width').inner_text()=='140 mm'
        assert await page.locator('#status').inner_text()== 'Within the printable P0 template envelope (still not measured).'
        await page.locator('#burger').click()
        assert await page.locator('#num_mouth_inner_width').inner_text()=='150 mm'
        async with page.expect_download() as event:
            await page.locator('#downloadJSON').click()
        download=await event.value
        blob=Path(await download.path()).read_bytes()
        data=json.loads(blob)
        assert data['disposition']=='HYPOTHETICAL_UNMEASURED_HOLD'
        assert data['measurements']['mouth_inner_width']==150
        async with page.expect_download() as event:
            await page.locator('#downloadSvg').click()
        svg=Path(await (await event.value).path()).read_text()
        assert 'width="420mm" height="297mm"' in svg
        assert '100 mm CHECK' in svg
        await page.locator('#compact').click()
        assert await page.locator('#num_mouth_inner_width').inner_text()=='125 mm'
        assert not errors,errors
        await browser.close()
        print('PASS: phone-width offline GUI, 3 presets, 2 downloads, hypothetical label, zero JS errors')

if __name__=='__main__':asyncio.run(main())
