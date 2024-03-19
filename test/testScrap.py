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
    def test_telechargement_image(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = b'contenu_image_fictive'
        mock_get.return_value = mock_response

        with patch('scrap.scrap.open',
                   new_callable=unittest.mock.mock_open()) as mock_open:
            sp.telecharger_image("https://exemple.com/image.jpg",
                                 "chemin/fichier.jpg"
                                 )
            mock_open.assert_called_with("chemin/fichier.jpg", 'wb')
            mock_file_handle = mock_open.return_value.__enter__.return_value
            mock_file_handle.write.assert_called_with(b'contenu_image_fictive')

    @patch('scrap.scrap.requests.get')
    @patch('scrap.scrap.print')
    def test_erreur_telechargement_image(self, mock_print, mock_get):
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError(
            "Error message for testing")
        mock_get.return_value = mock_response

        sp.telecharger_image("https://exemple.com/image_invalide.jpg",
                             "chemin/fichier.jpg")

        mock_print.assert_any_call(
            "Erreur lors du téléchargement de l'image "
            "https://exemple.com/image_invalide.jpg: Error message for testing")


if __name__ == '__main__':
    unittest.main()
