# Fichier: test_ad_functions.py
# Contient les tests unitaires

import unittest
from unittest.mock import patch, MagicMock
from ldap3 import ALL  # Ajout de l'import manquant
import ad_functions

class TestADFunctions(unittest.TestCase):
    
    @patch('ad_functions.Server')
    @patch('ad_functions.Connection')
    def test_connect_to_ad(self, mock_connection, mock_server):
        # Configuration du mock
        mock_conn = MagicMock()
        mock_conn.bind.return_value = True
        mock_connection.return_value = mock_conn
        
        # Test de la fonction
        result = ad_functions.connect_to_ad()
        
        # Vérifications
        mock_server.assert_called_once_with('localhost', get_info=ALL)
        mock_connection.assert_called_once()
        mock_conn.bind.assert_called_once()
        self.assertEqual(result, mock_conn)
    
    def test_check_create_ou_existing(self):
        # Mock connection pour simuler une OU existante
        mock_conn = MagicMock()
        mock_conn.search.return_value = True
        
        result = ad_functions.check_create_ou(mock_conn, "OU=Test,DC=ynov,DC=local", "Test")
        
        mock_conn.search.assert_called_once()
        self.assertTrue(result)
        mock_conn.add.assert_not_called()
    
    def test_check_create_ou_new(self):
        # Mock connection pour simuler une OU non existante
        mock_conn = MagicMock()
        mock_conn.search.return_value = False
        mock_conn.add.return_value = True
        
        result = ad_functions.check_create_ou(mock_conn, "OU=Test,DC=ynov,DC=local", "Test")
        
        mock_conn.search.assert_called_once()
        mock_conn.add.assert_called_once()
        self.assertTrue(result)
    
    def test_create_user_success(self):
        # Mock connection pour simuler une création réussie
        mock_conn = MagicMock()
        mock_conn.add.return_value = True
        mock_conn.extend.microsoft.modify_password.return_value = True
        
        user_info = {
            'nom': 'Test',
            'prenom': 'Unitaire',
            'motdepasse': 'P@ssw0rd'
        }
        
        result = ad_functions.create_user(
            mock_conn, 
            user_info, 
            "OU=Test,DC=ynov,DC=local", 
            "DC=ynov,DC=local"
        )
        
        mock_conn.add.assert_called_once()
        mock_conn.extend.microsoft.modify_password.assert_called_once()
        self.assertTrue(result)
    
    def test_create_user_failure(self):
        # Mock connection pour simuler un échec
        mock_conn = MagicMock()
        mock_conn.add.return_value = False
        
        user_info = {
            'nom': 'Test',
            'prenom': 'Unitaire',
            'motdepasse': 'P@wd123!'
        }
        
        result = ad_functions.create_user(
            mock_conn, 
            user_info, 
            "OU=Test,DC=ynov,DC=local", 
            "DC=ynov,DC=local"
        )
        
        mock_conn.add.assert_called_once()
        mock_conn.extend.microsoft.modify_password.assert_not_called()
        self.assertFalse(result)

if __name__ == '__main__':
    unittest.main()