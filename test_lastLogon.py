import unittest
from unittest.mock import patch, MagicMock
import datetime
import lastLogon

class DummyEntry:
    def __init__(self, cn, lastLogon):
        self.cn = MagicMock(value=cn)
        self.lastLogonTimestamp = MagicMock(value=lastLogon)
        self.entry_dn = f"CN={cn},OU=Test,DC=ynov,DC=local"

class TestLastLogonScript(unittest.TestCase):
    def setUp(self):
        # Sauvegarde de la vraie classe datetime
        self.real_datetime_cls = lastLogon.datetime.datetime
        # Date fixe pour les tests (28 avril 2025 UTC)
        self.fixed_now = datetime.datetime(2025, 4, 28, tzinfo=datetime.timezone.utc)

        # Sous-classe qui surcharge only now()
        real_cls = self.real_datetime_cls
        fixed_now = self.fixed_now
        class FixedDateTime(real_cls):
            @classmethod
            def now(cls, tz=None):
                # Retourne une instance FixedDateTime fixée
                if tz:
                    return cls(fixed_now.year, fixed_now.month, fixed_now.day,
                               fixed_now.hour, fixed_now.minute, fixed_now.second,
                               tzinfo=tz)
                return cls(fixed_now.year, fixed_now.month, fixed_now.day,
                           fixed_now.hour, fixed_now.minute, fixed_now.second)
        # Injection dans le module lastLogon
        lastLogon.datetime.datetime = FixedDateTime

    def tearDown(self):
        # Restauration de datetime original
        lastLogon.datetime.datetime = self.real_datetime_cls

    @patch('lastLogon.load_dotenv')
    @patch('lastLogon.os.getenv', side_effect=lambda k: {
        'OU_PATH': 'OU=Test,DC=ynov,DC=local',
        'AD_USER': 'test_user',
        'AD_PASSWORD': 'test_pass'
    }[k])
    @patch('lastLogon.Connection')
    @patch('lastLogon.Server')
    def test_disable_inactive_users(self,
                                    mock_server,
                                    mock_conn_cls,
                                    mock_getenv,
                                    mock_loadenv):
        # Connexion simulée avec bind() réussi
        mock_conn = MagicMock()
        mock_conn.bind.return_value = True

        # Création de raw timestamps (100ns units) pour >7j et <=7j
        epoch = lastLogon.datetime.datetime(1601, 1, 1, tzinfo=datetime.timezone.utc)
        now = lastLogon.datetime.datetime.now(datetime.timezone.utc)
        old_date = now - datetime.timedelta(days=10)
        recent_date = now - datetime.timedelta(days=3)
        old_raw = int((old_date - epoch).total_seconds() * 1e7)
        recent_raw = int((recent_date - epoch).total_seconds() * 1e7)

        # Préparation des entrées
        entries = [
            DummyEntry('UserOld', old_raw),
            DummyEntry('UserRecent', recent_raw),
            DummyEntry('UserNoTS', None)
        ]
        mock_conn.entries = entries
        mock_conn_cls.return_value = mock_conn

        # Exécution du script
        lastLogon.main()

        # Vérification de la recherche d'utilisateurs
        mock_conn.search.assert_called_once_with(
            search_base='OU=Test,DC=ynov,DC=local',
            search_filter='(objectClass=user)',
            search_scope=lastLogon.SUBTREE,
            attributes=['cn', 'lastLogonTimestamp']
        )
        # Seul UserOld doit être désactivé
        mock_conn.modify.assert_called_once_with(
            entries[0].entry_dn,
            {'userAccountControl': [(lastLogon.MODIFY_REPLACE, [514])]}
        )

    @patch('lastLogon.load_dotenv')
    @patch('lastLogon.os.getenv', side_effect=lambda k: {
        'OU_PATH': 'OU=Test,DC=ynov,DC=local',
        'AD_USER': 'test_user',
        'AD_PASSWORD': 'test_pass'
    }[k])
    @patch('lastLogon.Connection')
    @patch('lastLogon.Server')
    def test_no_modify_when_bind_fails(self,
                                       mock_server,
                                       mock_conn_cls,
                                       mock_getenv,
                                       mock_loadenv):
        # bind() échoue => sortie
        mock_conn = MagicMock()
        mock_conn.bind.return_value = False
        mock_conn_cls.return_value = mock_conn

        with self.assertRaises(SystemExit) as cm:
            lastLogon.main()
        self.assertEqual(cm.exception.code, 1)

        mock_conn.search.assert_not_called()
        mock_conn.modify.assert_not_called()

if __name__ == '__main__':
    unittest.main()

