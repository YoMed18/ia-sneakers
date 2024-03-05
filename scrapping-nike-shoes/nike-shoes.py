import asyncio
import aiohttp
import os
from pathlib import Path
import shutil
from zipfile import ZipFile
from dotenv import load_dotenv
from playwright.async_api import async_playwright

load_dotenv()
async def scrape_timberland():
    URL_TIMBERLAND = os.getenv("URL_TIMBERLAND")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        await page.goto(URL_TIMBERLAND)

        consent_button = await page.query_selector('#onetrust-accept-btn-handler')
        if consent_button:
            await consent_button.click()

        while True:
            load_more_btn = await page.query_selector('.load-more-btn-js')

            if load_more_btn and await load_more_btn.is_visible():
                await load_more_btn.click(timeout=180000)
                await asyncio.sleep(1) 
            else:
                break

        images = await page.query_selector_all('.product-block-pdp-url.pdp-url-js .product-block-views-container.views-container-js .product-block-views-selected-view-main-image img')
        images_src = [await image.get_attribute('src') for image in images]

        await browser.close()
        return images_src

async def scrape_new_balance():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        URL_NEWBALANCE = os.getenv("URL_NEWBALANCE")
        await page.goto(URL_NEWBALANCE)
        
        consent_button = await page.query_selector('#consent_prompt_submit')
        if consent_button:
            await consent_button.click()
            await asyncio.sleep(1) 

        discount_button = await page.query_selector('#discountPopUpCloseBtn')
        if discount_button:
            await discount_button.click()
            await asyncio.sleep(1)

        while True:
            load_more_btn = await page.query_selector("#btn-loadMore")
            if load_more_btn:
                await load_more_btn.click(timeout=580000)
                await page.wait_for_timeout(1000)
            else:
                break

        images = await page.query_selector_all(".firstImage .tile-image img")
        images_src = [await image.get_attribute("src") for image in images]

        await browser.close()
        return images_src
 
async def scrape_vans():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False) 
        page = await browser.new_page()
        URL_VANS = os.getenv("URL_VANS")
        await page.goto(URL_VANS)
        
        consent_button = await page.query_selector('#onetrust-accept-btn-handler')
        if consent_button:
            await consent_button.click()

        while True:
            load_more_btn = await page.query_selector("#catalog-container .load-more-btn")
            if load_more_btn and await load_more_btn.is_visible():
                await load_more_btn.click()
                await asyncio.sleep(1)
            else:
                break 

        images = await page.query_selector_all(".cycle-sentinel .product-block-views-selected-view-main-image img")
        images_src = [await image.get_attribute("src") for image in images]

        await browser.close()
        return images_src
        
async def script_nike():
    URL_NIKE = os.getenv("URL_NIKE")

    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(headless=False)
        page = await browser.new_page()
        await page.goto(URL_NIKE)

        consent_button_selector = '[data-testid="dialog-accept-button"]'
        consent_button = await page.query_selector(consent_button_selector)
        if consent_button:
            await consent_button.click()
            await asyncio.sleep(1)

        end_time = time.time() + 5 * 60
        while time.time() < end_time:
            await page.evaluate("window.scrollTo(0, document.body.scrollHeight);")
            await page.wait_for_timeout(1000)

        images = await page.query_selector_all('.product-card__body img.product-card__hero-image')
        urls = [await img.get_attribute('src') for img in images]

        await browser.close()
        return urls
        
async def main():
    timberland_urls = await scrape_timberland()
    new_balance_urls = await scrape_new_balance()
    vans_urls = await scrape_vans()
    nike_urls = await script_nike()

    all_urls = {'timberland': timberland_urls, 'new_balance': new_balance_urls, 'vans': vans_urls, 'nike': nike_urls}

    base_dir = 'downloaded_images'
    Path(base_dir).mkdir(exist_ok=True)

    for brand, urls in all_urls.items():
        brand_dir = os.path.join(base_dir, brand)
        await download_images(urls, brand_dir)
        zip_directory(brand_dir, f"{brand_dir}.zip")

asyncio.run(main())