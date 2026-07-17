import os
import unittest
from unittest.mock import patch

from src.core.bot_gemini import CityBotGemini


class ProviderConfigTest(unittest.TestCase):
    def test_gemini_retorna_erro_claro_sem_configuracao(self):
        with (
            patch.dict(os.environ, {}, clear=True),
            patch('src.core.bot_gemini.load_dotenv'),
            patch('src.core.bot_gemini.genai.Client') as mock_client,
            patch('src.core.bot_gemini.CityBotDatabase'),
        ):
            bot = CityBotGemini()

        self.assertIn('GEMINI_API_KEY', bot.config_error)
        self.assertIn('GEMINI_MODEL', bot.config_error)
        self.assertIsNone(bot.client)
        mock_client.assert_not_called()
        self.assertIn(
            'Erro de configuracao Gemini',
            bot.resposta_bot([('user', 'Oi')]),
        )


if __name__ == '__main__':
    unittest.main()
