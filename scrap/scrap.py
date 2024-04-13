import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin, unquote
import os
import time
import base64
import binascii
from PIL import Image


def telecharger_toutes_images(url_page, nom_dossier, callback=None):
    if not os.path.exists(nom_dossier):
        os.makedirs(nom_dossier)

    reponse_page = requests.get(url_page)
    soup = BeautifulSoup(reponse_page.text, 'html.parser')

    images = soup.find_all('img')
    if not images:
        print("Aucune image trouvée sur la page.")
        return

    for img in images:
        src = img.get('src')
        alt = img.get('alt', '').strip()
        print(alt)
        if not src:
            print("Image sans source; ignorée.")
            continue

        nom_fichier = nettoyer_nom_fichier(alt if alt else str(
            time.time())) 
        # Utilise le temps comme nom de fichier si alt est vide
        chemin_complet = os.path.join(nom_dossier, nom_fichier)

        telecharger_image(src, chemin_complet, url_page)

        if callback:
            callback(nom_fichier)


def nettoyer_nom_fichier(nom):
    nom = re.sub(r'[\\/:"*?<>|]+', "", nom)
    return unquote(nom)[:200]


def convertir_en_jpg(chemin_image):
    try:
        with Image.open(chemin_image) as img:
            # Si l'image est en mode RGBA (avec canal alpha),
            # on crée un fond blanc
            if img.mode == 'RGBA':
                fond_blanc = Image.new('RGB', img.size, 'WHITE')  # Fond blanc
                fond_blanc.paste(img, (0, 0),
                                 img)  
                # Utiliser img comme masque pour garder la
                # transparence
                img = fond_blanc
            elif (img.mode == 'LA' or
                  (img.mode == 'P' and 'transparency' in img.info)):
                img = img.convert('RGB')

            chemin_sans_ext = os.path.splitext(chemin_image)[0]
            nouveau_chemin = f"{chemin_sans_ext}.jpg"
            img.save(nouveau_chemin, "JPEG")
            os.remove(chemin_image)  # Supprime l'ancien fichier
            print(f"Converti et sauvegardé en JPG : {nouveau_chemin}")
    except Exception as e:
        print(f"Erreur lors de la conversion en JPG : {e}")


def telecharger_image(url, chemin_complet, base_url=None):
    if url.startswith('data:image'):
        # Séparation du format et des données encodées en base64
        format, imgstr = url.split(';base64,')
        ext = format.split('/')[-1]

        # Correction des problèmes de formatage base64
        imgstr = imgstr.replace(' ', '+')
        imgstr += '=' * (-len(imgstr) % 4)

        try:
            # Décodage de la chaîne base64 en données binaires
            imgdata = base64.b64decode(imgstr)

            # Construction du chemin complet du fichier
            nom_fichier_complet = f"{chemin_complet}.{ext}"

            # Sauvegarde des données binaires en tant qu'image
            with open(nom_fichier_complet, 'wb') as fichier:
                fichier.write(imgdata)
            print(
                "L'image encodée a été téléchargée et sauvegardée sous : "
                f"{nom_fichier_complet}"
            )

            # Conversion en JPG si nécessaire
            if ext not in ['png', 'jpg', 'jpeg', 'svg']:
                convertir_en_jpg(nom_fichier_complet)

        except binascii.Error as e:
            print(
                f"Erreur lors du décodage de l'image encodée en base64 : {e}")

    else:
        if not url.startswith('http'):
            url = urljoin(base_url, url)  
            # Conversion des URLs relatifs en absolus
        ext = os.path.splitext(urlparse(url).path)[1][1:]

        # Générer un chemin complet avec un timestamp pour éviter les doublons
        nom_fichier_complet = f"{chemin_complet}_{int(time.time())}."
        extension = ext if ext in ['png', 'jpg', 'jpeg', 'svg'] else 'jpg'
        nom_fichier_complet += f"{extension}"

        try:
            # Téléchargement de l'image
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            with open(nom_fichier_complet, 'wb') as fichier:
                fichier.write(response.content)
            print(
                "L'image a été téléchargée et sauvegardée sous : "
                f"{nom_fichier_complet}"
            )

            # Conversion en JPG si nécessaire
            if ext not in ['png', 'jpg', 'jpeg', 'svg']:
                convertir_en_jpg(nom_fichier_complet)

        except requests.exceptions.RequestException as erreur:
            print(f"Erreur lors du téléchargement de l'image {url}: {erreur}")


if __name__ == "__main__":
    url_page = input(
     "Veuillez entrer l'URL de la page d'où télécharger les images : ")
    nom_dossier = input(
     "Veuillez entrer le nom du dossier dans lequel sauvegarder les images :"
                        )
    telecharger_toutes_images(url_page, nom_dossier)
