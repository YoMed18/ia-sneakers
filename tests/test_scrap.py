import unittest
from unittest.mock import patch, MagicMock, mock_open
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
    def test_telechargement_image(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = b'contenu_image_fictive'
        mock_get.return_value = mock_response

        with patch('scrap.scrap.open',
                   new_callable=unittest.mock.mock_open()) as mock_open:
            sp.telecharger_image(
                "https://exemple.com/image.jpg",
                "chemin/fichier.jpg"
            )

            open_call = mock_open.mock_calls[0]
            called_with_path = open_call[1][0]
            # Vérifie que le chemin appelé commence par le chemin attendu
            assert called_with_path.startswith(
                "chemin/fichier.jpg"
            ), "Le chemin du fichier ouvert ne commence pas comme attendu"

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

    @patch('scrap.scrap.requests.get')
    @patch('scrap.scrap.telecharger_image')
    @patch('scrap.scrap.os.path.exists')
    @patch('scrap.scrap.os.makedirs')
    @patch('scrap.scrap.nettoyer_nom_fichier', side_effect=lambda x: x)
    @patch('scrap.scrap.time.time',
           return_value=1234567890)
    def test_telecharger_toutes_images(self, mock_time, mock_nettoyer,
                                       mock_makedirs, mock_exists,
                                       mock_telecharger_image, mock_get):
        html_content = """
            <html>
                <body>
                    <img src="http://exemple.com/image1.jpg" alt="Image 1">
                    <img src="http://exemple.com/image2.jpg">
                    <img alt="Image sans source">
                </body>
            </html>
            """
        mock_exists.return_value = False
        mock_response = MagicMock()
        mock_response.text = html_content
        mock_get.return_value = mock_response

        sp.telecharger_toutes_images("http://exemple.com", "dossier_test")

        expected_calls = [
            (("http://exemple.com/image1.jpg", "dossier_test/Image 1",
              "http://exemple.com"),),
            (("http://exemple.com/image2.jpg", "dossier_test/1234567890",
              "http://exemple.com"),)
        ]
        mock_telecharger_image.assert_has_calls(expected_calls, any_order=True)

        mock_makedirs.assert_called_once_with("dossier_test")

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

    @patch('scrap.scrap.Image.open')
    @patch('scrap.scrap.os.remove')
    @patch('scrap.scrap.Image.new')
    @patch('scrap.scrap.print')
    def test_conversion_avec_alpha(self, mock_print, mock_new,
                                   mock_remove, mock_open):
        img_mock = MagicMock()
        img_mock.mode = 'RGBA'
        img_mock.convert.return_value = img_mock
        mock_open.return_value = img_mock

        fond_blanc_mock = MagicMock()
        mock_new.return_value = fond_blanc_mock

        sp.convertir_en_jpg("chemin/fake_image.gif")

        mock_new.assert_called_once