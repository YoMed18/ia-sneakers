from playwright.sync_api import sync_playwright  # pip install playwright puis playwright install
import time
import requests
import os
from zipfile import ZipFile

def download_images(urls, path='images'):
    if not os.path.exists(path):
        os.makedirs(path)
    for i, url in enumerate(urls):
        response = requests.get(url)
        if response.status_code == 200:
            with open(f"{path}/image_{i}.jpg", 'wb') as f:
                f.write(response.content)

def create_zip(folder_path, zip_name='images.zip'):
    with ZipFile(zip_name, 'w') as zipf:
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                zipf.write(os.path.join(root, file), os.path.relpath(os.path.join(root, file), os.path.join(folder_path, '..')))

def run(playwright):
    browser = playwright.chromium.launch(headless=True)  # Ou .firefox, .webkit
    page = browser.new_page()
    page.goto("https://www.nike.com/fr/w/chaussures-y7ok")

    # Démarre le défilement pendant 5 minutes
    end_time = time.time() + 3 * 60
    while time.time() < end_time:
        page.evaluate("window.scrollTo(0, document.body.scrollHeight);")
        page.wait_for_timeout(1000)  # Attente d'1 seconde entre les scrolls

    # Récupère les URLs des images après le défilement
    images = page.query_selector_all('.product-card__body img.product-card__hero-image')
    urls = [img.get_attribute('src') for img in images]

    browser.close()
    return urls

with sync_playwright() as playwright:
    urls = run(playwright)

# Utilisez les fonctions définies pour télécharger les images et créer un fichier ZIP
download_images(urls)
create_zip('images')

# python nike-shoes.py