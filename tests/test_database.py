import unittest

from src.core.database import DEFAULT_DB_PATH, CityBotDatabase
from src.utils.paths import PROJECT_ROOT


class CityBotDatabaseTest(unittest.TestCase):
    def setUp(self):
        self.database = CityBotDatabase(':memory:')

    def tearDown(self):
        self.database.conexao.close()

    def test_salva_e_carrega_conversa(self):
        self.database.save_conversation('Pergunta', 'Resposta')

        self.assertEqual(
            self.database.load_conversations(),
            [('Pergunta', 'Resposta')],
        )

    def test_caminho_padrao_do_banco_fica_na_raiz_do_projeto(self):
        self.assertEqual(DEFAULT_DB_PATH, PROJECT_ROOT / 'citybot.db')

    def test_limpar_conversas_preserva_usuario_e_aceita_novos_registros(self):
        self.database.save_user('Pessoa', 'Preferências')
        self.database.save_conversation('Pergunta', 'Resposta')

        self.database.limpar_conversas()
        self.database.save_conversation('Nova pergunta', 'Nova resposta')

        self.assertIsNotNone(self.database.load_user('Pessoa'))
        self.assertEqual(
            self.database.load_conversations(),
            [('Nova pergunta', 'Nova resposta')],
        )

    def test_limpar_banco_remove_conversas_e_usuarios(self):
        self.database.save_user('Pessoa', 'Preferências')
        self.database.save_conversation('Pergunta', 'Resposta')

        self.database.limpar_banco()

        self.assertIsNone(self.database.load_user('Pessoa'))
        self.assertEqual(self.database.load_conversations(), [])


if __name__ == '__main__':
    unittest.main()
