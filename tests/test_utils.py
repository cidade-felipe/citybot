import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

root_path = Path(__file__).resolve().parents[1]
if str(root_path) not in sys.path:
    sys.path.append(str(root_path))

from src.utils.file_writer import salvar_texto
from src.utils.pdf_reader import carrega_pdf
from src.utils.scrapers import (
    ExtractedContent,
    REQUEST_TIMEOUT_SECONDS,
    VIDEO_LANGUAGES,
    YOUTUBE_AUDIO_DOWNLOAD_HINT,
    YOUTUBE_COOKIES_BROWSER_ENV,
    YOUTUBE_COOKIES_FILE_ENV,
    YOUTUBE_COOKIES_PROFILE_ENV,
    _extrai_video_id,
    _yt_dlp_options,
    _valida_duracao_audio,
    carrega_site,
    carrega_video,
)


class ScrapersTest(unittest.TestCase):
    @patch('src.utils.scrapers.requests.get')
    def test_carrega_site_remove_scripts_e_usa_timeout(self, mock_get):
        response = Mock()
        response.text = '<html><script>ignorar()</script><body>Conteúdo útil</body></html>'
        mock_get.return_value = response

        texto = carrega_site('https://example.com')

        self.assertEqual(texto, 'Conteúdo útil')
        mock_get.assert_called_once_with(
            'https://example.com',
            headers={'User-Agent': 'Mozilla/5.0'},
            timeout=REQUEST_TIMEOUT_SECONDS,
        )
        response.raise_for_status.assert_called_once()

    def test_extrai_ids_de_urls_suportadas(self):
        urls = {
            'https://www.youtube.com/watch?v=abc123&list=lista': 'abc123',
            'https://youtu.be/abc123?si=share': 'abc123',
            'https://www.youtube.com/shorts/abc123': 'abc123',
            'https://www.youtube.com/embed/abc123': 'abc123',
        }

        for url, expected in urls.items():
            with self.subTest(url=url):
                self.assertEqual(_extrai_video_id(url), expected)

    @patch('src.utils.scrapers.YouTubeTranscriptApi')
    def test_carrega_video_usa_api_compativel_com_dependencia(self, mock_api):
        mock_api.return_value.fetch.return_value = [
            Mock(text='Primeira parte'),
            Mock(text='segunda parte'),
        ]

        texto = carrega_video('https://youtu.be/abc123')

        self.assertEqual(texto, 'Primeira parte segunda parte')
        mock_api.return_value.fetch.assert_called_once_with(
            'abc123',
            languages=VIDEO_LANGUAGES,
        )

    @patch('src.utils.scrapers.YoutubeDL')
    @patch('src.utils.scrapers.YouTubeTranscriptApi')
    def test_carrega_video_usa_ytdlp_como_fallback(self, mock_api, mock_youtube_dl):
        mock_api.return_value.fetch.side_effect = RuntimeError('sem transcrição')

        ydl = mock_youtube_dl.return_value.__enter__.return_value
        ydl.extract_info.return_value = {
            'subtitles': {
                'en': [
                    {
                        'ext': 'json3',
                        'url': 'https://captions.example/en-json3',
                    },
                ],
            },
            'automatic_captions': {
                'pt': [
                    {
                        'ext': 'json3',
                        'url': 'https://captions.example/json3',
                    },
                ],
            },
        }

        response = Mock()
        response.read.return_value = (
            '{"events": ['
            '{"segs": [{"utf8": "Primeira "}, {"utf8": "parte"}]},'
            '{"segs": [{"utf8": "segunda parte"}]}'
            ']}'
        ).encode('utf-8')
        ydl.urlopen.return_value = response

        with self.assertLogs('src.utils.scrapers', level='WARNING'):
            texto = carrega_video('https://youtu.be/abc123')

        self.assertEqual(texto, 'Primeira parte segunda parte')
        ydl.extract_info.assert_called_once_with('https://youtu.be/abc123', download=False)
        ydl.urlopen.assert_called_once_with('https://captions.example/json3')

    @patch('src.utils.scrapers._baixa_audio_yt_dlp')
    @patch('src.utils.scrapers.WhisperModel')
    @patch('src.utils.scrapers.YoutubeDL')
    @patch('src.utils.scrapers.YouTubeTranscriptApi')
    def test_carrega_video_usa_faster_whisper_como_fallback(self, mock_api, mock_youtube_dl, mock_whisper, mock_download_audio):
        mock_api.return_value.fetch.side_effect = RuntimeError('sem transcrição')

        ydl = mock_youtube_dl.return_value.__enter__.return_value
        ydl.extract_info.return_value = {
            'subtitles': {},
            'automatic_captions': {},
        }
        mock_download_audio.return_value = Path('audio.webm')
        model = mock_whisper.return_value
        model.transcribe.return_value = (
            [
                Mock(text='Texto do áudio'),
                Mock(text='segunda parte'),
            ],
            Mock(),
        )

        with self.assertLogs('src.utils.scrapers', level='WARNING'):
            texto = carrega_video('https://youtu.be/abc123')

        self.assertEqual(texto, 'Texto do áudio segunda parte')
        mock_download_audio.assert_called_once()
        self.assertEqual(mock_download_audio.call_args.args[0], 'https://youtu.be/abc123')
        model.transcribe.assert_called_once_with(
            'audio.webm',
            language=None,
            beam_size=5,
            vad_filter=True,
        )

    @patch('src.utils.scrapers.YoutubeDL')
    @patch('src.utils.scrapers.YouTubeTranscriptApi')
    def test_carrega_video_retorna_erro_contextual_em_rate_limit(self, mock_api, mock_youtube_dl):
        mock_api.return_value.fetch.side_effect = RuntimeError('Too Many Requests')
        ydl = mock_youtube_dl.return_value.__enter__.return_value
        ydl.extract_info.side_effect = RuntimeError('HTTP Error 429: Too Many Requests')

        with self.assertLogs('src.utils.scrapers', level='WARNING'):
            texto = carrega_video('https://youtu.be/abc123')

        self.assertIsInstance(texto, ExtractedContent)
        self.assertEqual(texto, '')
        self.assertIn('HTTP 429 Too Many Requests', texto.error_message)
        self.assertIn(YOUTUBE_COOKIES_BROWSER_ENV, texto.error_message)
        self.assertIn(YOUTUBE_AUDIO_DOWNLOAD_HINT, texto.error_message)

    @patch('src.utils.scrapers.YoutubeDL')
    @patch('src.utils.scrapers.YouTubeTranscriptApi')
    def test_carrega_video_retorna_erro_contextual_em_banco_de_cookies_bloqueado(self, mock_api, mock_youtube_dl):
        mock_api.return_value.fetch.side_effect = RuntimeError('Too Many Requests')
        mock_youtube_dl.side_effect = RuntimeError('Could not copy Chrome cookie database.')

        with self.assertLogs('src.utils.scrapers', level='WARNING'):
            texto = carrega_video('https://youtu.be/abc123')

        self.assertIsInstance(texto, ExtractedContent)
        self.assertEqual(texto, '')
        self.assertIn('não conseguiu copiar o banco de cookies', texto.error_message)
        self.assertIn(YOUTUBE_COOKIES_FILE_ENV, texto.error_message)

    @patch('src.utils.scrapers.YoutubeDL')
    @patch('src.utils.scrapers.YouTubeTranscriptApi')
    def test_carrega_video_retorna_erro_contextual_em_arquivo_de_cookies_invalido(self, mock_api, mock_youtube_dl):
        mock_api.return_value.fetch.side_effect = RuntimeError('Too Many Requests')
        mock_youtube_dl.side_effect = RuntimeError(
            "'C:\\tmp\\youtube_cookies.txt' does not look like a Netscape format cookies file"
        )

        with self.assertLogs('src.utils.scrapers', level='WARNING'):
            texto = carrega_video('https://youtu.be/abc123')

        self.assertIsInstance(texto, ExtractedContent)
        self.assertEqual(texto, '')
        self.assertIn('formato Netscape cookies.txt', texto.error_message)
        self.assertIn('arquivos JSON, HTML ou SQLite', texto.error_message)

    @patch.dict(
        os.environ,
        {
            YOUTUBE_COOKIES_BROWSER_ENV: 'chrome',
            YOUTUBE_COOKIES_PROFILE_ENV: 'Default',
            YOUTUBE_COOKIES_FILE_ENV: '',
        },
    )
    def test_ytdlp_options_usa_cookies_do_navegador_quando_configurado(self):
        options = _yt_dlp_options()

        self.assertEqual(options['cookiesfrombrowser'], ('chrome', 'Default'))

    @patch.dict(
        os.environ,
        {
            YOUTUBE_COOKIES_BROWSER_ENV: 'chrome',
            YOUTUBE_COOKIES_FILE_ENV: 'C:\\tmp\\youtube_cookies.txt',
        },
    )
    def test_ytdlp_options_prioriza_arquivo_de_cookies(self):
        options = _yt_dlp_options()

        self.assertEqual(options['cookiefile'], 'C:\\tmp\\youtube_cookies.txt')
        self.assertNotIn('cookiesfrombrowser', options)

    @patch.dict(os.environ, {'CITYBOT_WHISPER_MAX_AUDIO_SECONDS': '60'})
    def test_valida_duracao_audio_bloqueia_video_longo(self):
        with self.assertRaisesRegex(RuntimeError, 'excede o limite de 60 segundos'):
            _valida_duracao_audio({'duration': 120})


class PdfReaderTest(unittest.TestCase):
    @patch('src.utils.pdf_reader.PdfReader')
    def test_ignora_paginas_sem_texto(self, mock_reader):
        first_page = Mock()
        first_page.extract_text.return_value = None
        second_page = Mock()
        second_page.extract_text.return_value = 'Página com texto'
        mock_reader.return_value.pages = [first_page, second_page]

        with tempfile.NamedTemporaryFile(suffix='.pdf') as pdf:
            texto = carrega_pdf(pdf.name)

        self.assertEqual(texto, '\nPágina com texto')


class FileWriterTest(unittest.TestCase):
    def test_nome_com_diretorios_nao_escapa_da_pasta_textos(self):
        original_directory = os.getcwd()

        with tempfile.TemporaryDirectory() as temporary_directory:
            raiz_dados = Path(temporary_directory)
            diretorio_execucao = raiz_dados / 'execucao'
            diretorio_execucao.mkdir()
            os.chdir(diretorio_execucao)
            try:
                with patch('src.utils.file_writer.TEXTOS_DIR', raiz_dados / 'textos'):
                    resultado = salvar_texto('Conteúdo', '../arquivo')

                self.assertEqual(resultado, 'Conteúdo')
                self.assertTrue((raiz_dados / 'textos/arquivo.docx').exists())
                self.assertTrue((raiz_dados / 'textos/arquivo.txt').exists())
                self.assertFalse((diretorio_execucao / 'textos/arquivo.txt').exists())
                self.assertFalse((raiz_dados / 'arquivo.txt').exists())
            finally:
                os.chdir(original_directory)


if __name__ == '__main__':
    unittest.main()
