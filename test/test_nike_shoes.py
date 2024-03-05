import os
import pytest
from test_nike_shoes import download_images, create_zip, run

# Marquer le test pour s'assurer que ce test nécessite une connexion Internet pour récupérer les images
@pytest.mark.internet_access
def test_run_and_download():
    # Exécuter le script
    with sync_playwright() as playwright:
        all_images = run(playwright)

    # Télécharger les images
    download_images(all_images)

    # Vérifier que le dossier d'images et le fichier zip sont créés
    assert os.path.exists('images')
    assert os.path.exists('images.zip')

    # Supprimer les fichiers après le test
    os.remove('images.zip')
    os.rmdir('images')
