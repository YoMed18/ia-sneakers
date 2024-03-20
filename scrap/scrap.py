import requests
from bs4 import BeautifulSoup
from urllib.parse import unquote, urljoin
import os
import re


# Fonction pour télécharger les images d'un site web
def telecharger_toutes_images(url_page, nom_dossier, callback=None):
    # Vérifiez et créez le dossier si nécessaire
    if not os.path.exists(nom_dossier):
        os.makedirs(nom_dossier)

    try:
        # Obtenez le contenu de la page
        reponse_page = requests.get(url_page)
        soup = BeautifulSoup(reponse_page.text, 'html.parser')

        # Trouvez toutes les images sur la page
        images = soup.find_all('img')
        if not images:
            print("Aucune image trouvée sur la page.")
            return

        for img in images:
            src = img.get('src')
            alt = img.get('alt', '').strip()
            if not src or not alt:
                print("Image sans source ou texte alternatif; ignorée.")
                continue

            nom_fichier = nettoyer_nom_fichier(alt) + "." + src.split('.')[-1].split('?')[0]
            chemin_complet = os.path.join(nom_dossier, nom_fichier)

            telecharger_image(urljoin(url_page, src), chemin_complet)

            # Appelez la callback avec le nom du fichier de l'image téléchargée
            if callback:
                callback(nom_fichier)

    except requests.HTTPError as erreur:
        print(f"Erreur lors du téléchargement des images : {erreur}")


# Fonction afin de netoyyer le nom du fichier
def nettoyer_nom_fichier(nom):
    nom = re.sub(r'[\\/:"*?<>|]+', "", nom) # Retirer les caractères non
    # autorisés
    return unquote(nom)[:200]  # Limite la longueur pour éviter les erreurs sur les
    # systèmes de fichiers


# Fonction afin de télécharger les images
def telecharger_image(url, chemin_complet):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        with open(chemin_complet, 'wb') as fichier:
            fichier.write(response.content)
        print(f"L'image a été téléchargée et sauvegardée sous : {chemin_complet}")
    except requests.exceptions.RequestException as erreur:
        print(f"Erreur lors du téléchargement de l'image {url}: {erreur}")
        # Note: Ici, vous pourriez choisir de ne pas relancer l'exception pour permettre au test de vérifier le mock de `print`



if __name__ == "__main__":
    url_page = input("Veuillez entrer l'URL de la page d'où télécharger les images : ")
    nom_dossier = input("Veuillez entrer le nom du dossier dans lequel sauvegarder les "
                        "images : ")
    telecharger_toutes_images(url_page, nom_dossier)
