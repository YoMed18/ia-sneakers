from dotenv import load_dotenv
from playwright.sync_api import sync_playwright
import time
import requests
import os
from zipfile import ZipFile

# Charger les variables d'environnement à partir du fichier .env
load_dotenv()

# Liste des chaussures
shoes_to_filter = [
    "chaussure-air-force-1",
    "chaussure-air-jordan-1",
    "chaussure-air-max-90",
    "chaussure-dunk",
    "chaussure-air-max-plus",
    "chaussure-air-max-95"
]


def download_images(image_urls, path='images-trier'):
    # Suivi du nombre d'images pour chaque catégorie
    name_count = {shoe: 0 for shoe in shoes_to_filter}

    if not os.path.exists(path):
        os.makedirs(path)

    for url in image_urls:
        category = "unknown"
        for shoe in shoes_to_filter:
            if shoe in url:
                category = shoe
                break

        if category != "unknown":
            # Incrémentation du compteur pour la catégorie
            name_count[category] += 1

            # Création d'un nom unique pour l'image
            name = f"{category}_{name_count[category]}.jpg"

            # Création du dossier de la chaussure
            folder_path = os.path.join(path, category)
            if not os.path.exists(folder_path):
                os.makedirs(folder_path)

            # Téléchargement de l'image dans le dossier de la chaussure
            with open(os.path.join(folder_path, name), 'wb') as f:
                response = requests.get(url)
                if response.status_code == 200:
                    f.write(response.content)


def create_zip(folder_path, zip_name='images.zip'):
    with ZipFile(zip_name, 'w') as zipf:
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                zipf.write(
                    os.path.join(root, file), os.path.relpath(
                        os.path.join(root, file), os.path.join(
                            folder_path, '..'
                            )
                        )
                    )


def run(playwright, url):
    browser = playwright.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto(url)

    # Démarre le défilement pendant 5 minutes
    end_time = time.time() + 5 * 60
    while time.time() < end_time:
        page.evaluate("window.scrollTo(0, document.body.scrollHeight);")
        page.wait_for_timeout(1000)

    images = page.query_selector_all(
        '.product-card__body img.product-card__hero-image'
        )
    image_urls = [img.get_attribute('src') for img in images]

    browser.close()
    return image_urls

# Exécutez le script


with sync_playwright() as playwright:

    nike_url = os.getenv("URL_NIKE")
    image_urls = run(playwright, nike_url)

download_images(image_urls)

# Créez un fichier ZIP pour chaque dossier d'images
for shoe in shoes_to_filter:
    create_zip(f'images-trier/{shoe}', f'{shoe}.zip')
