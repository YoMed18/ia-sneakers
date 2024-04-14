import unittest
from unittest.mock import patch, MagicMock
import scrap.scrap as sp
import requests


class TestScrapImages(unittest.TestCase):

    @patch('scrap.scrap.os.path.exists')
    @patch('scrap.scrap.os.makedirs')
    def test_creation_dossier(self, mock_makedirs, mock_exists):
        mock_exists.return_value = False
        sp.telecharger_toutes_images("http://exemple.com",
                                     "dossier_test"
                                     )
        mock_makedirs.assert_called_with("dossier_test")

    @patch('scrap.scrap.requests.get')
    @patch('scrap.scrap.print')
    def test_erreur_telechargement_image(self, mock_print, mock_get):
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = \
            requests.exceptions.HTTPError("Error message for testing")

        mock_get.return_value = mock_response

        # Appeler la fonction sans essayer de catcher l'exception ici
        sp.telecharger_image("https://exemple.com/image_invalide.jpg",
                             "chemin/fichier.jpg")

        # Vérifier si `print` a été appelé avec le bon message
        mock_print.assert_any_call(
            "Erreur lors du téléchargement de l'image "
            "https://exemple.com/image_invalide.jpg: Error message for testing"
            )
        
    def test_elimination_caracteres_interdits(self):
        nom = "nom\\/:*?\"<>|de/fichier"
        attendu = "nomdefichier"
        self.assertEqual(sp.nettoyer_nom_fichier(nom), attendu)

    def test_troncature_nom_long(self):
        nom = "a" * 201
        attendu = "a" * 200
        self.assertEqual(sp.nettoyer_nom_fichier(nom), attendu)

    def test_decodage_pourcentage(self):
        nom = "fichier%20avec%20espaces"
        attendu = "fichier avec espaces"
        self.assertEqual(sp.nettoyer_nom_fichier(nom), attendu)

    def test_nom_sans_modification(self):
        nom = "nom_de_fichier_valide"
        self.assertEqual(sp.nettoyer_nom_fichier(nom), nom)
        
    def test_nom_vide(self):
        nom = ""
        attendu = ""
        self.assertEqual(sp.nettoyer_nom_fichier(nom), attendu)
