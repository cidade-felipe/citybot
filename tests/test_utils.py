import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

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
    _audio_yt_dlp_options,
    _baixa_audio_yt_dlp,
    _carrega_legendas_yt_dlp,
    _extrai_video_id,
    _filtro_duracao_audio,
    _normaliza_progresso_yt_dlp,
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

    @patch('src.utils.scrapers._extract_video_title', return_value='Título do vídeo')
    @patch('src.utils.scrapers.YouTubeTranscriptApi')
    def test_carrega_video_usa_api_compativel_com_dependencia(self, mock_api, mock_title):
        mock_api.return_value.fetch.return_value = [
            Mock(text='Primeira parte'),
            Mock(text='segunda parte'),
        ]

        texto = carrega_video('https://youtu.be/abc123')

        self.assertEqual(texto, 'Primeira parte segunda parte')
        self.assertEqual(texto.source_title, 'Título do vídeo')
        mock_title.assert_called_once_with('https://youtu.be/abc123')
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
            'title': 'Título do vídeo',
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
        self.assertEqual(texto.source_title, 'Título do vídeo')
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
            'title': 'Título do vídeo',
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
        self.assertEqual(texto.source_title, 'Título do vídeo')
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
        self.assertIn('não conseguiu acessar ou descriptografar os cookies', texto.error_message)
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

    @patch.dict(
        os.environ,
        {
            YOUTUBE_COOKIES_BROWSER_ENV: 'chrome',
            YOUTUBE_COOKIES_PROFILE_ENV: '',
            YOUTUBE_COOKIES_FILE_ENV: '',
        },
    )
    def test_ytdlp_options_pode_ignorar_cookies_do_navegador(self):
        options = _yt_dlp_options(use_browser_cookies=False)

        self.assertNotIn('cookiesfrombrowser', options)

    def test_audio_ytdlp_options_permite_download(self):
        options = _audio_yt_dlp_options(Path('downloads'))

        self.assertEqual(options['format'], 'bestaudio/best')
        self.assertFalse(options['skip_download'])
        self.assertIn('%(id)s.%(ext)s', options['outtmpl'])
        self.assertIs(options['match_filter'], _filtro_duracao_audio)

    def test_audio_ytdlp_options_envia_progresso(self):
        progress_callback = Mock()
        options = _audio_yt_dlp_options(Path('downloads'), progress_callback=progress_callback)

        options['progress_hooks'][0]({
            'status': 'downloading',
            'downloaded_bytes': 50,
            'total_bytes': 100,
            'speed': 10,
            'eta': 5,
        })

        progress_callback.assert_called_once_with({
            'status': 'downloading',
            'downloaded_bytes': 50,
            'total_bytes': 100,
            'percent': 50.0,
            'speed': 10,
            'eta': 5,
        })

    def test_normaliza_progresso_yt_dlp_sem_total(self):
        progress = _normaliza_progresso_yt_dlp({
            'status': 'downloading',
            'downloaded_bytes': 50,
        })

        self.assertEqual(progress['downloaded_bytes'], 50)
        self.assertEqual(progress['total_bytes'], 0)
        self.assertIsNone(progress['percent'])

    @patch.dict(
        os.environ,
        {
            YOUTUBE_COOKIES_BROWSER_ENV: 'chrome',
            YOUTUBE_COOKIES_PROFILE_ENV: '',
            YOUTUBE_COOKIES_FILE_ENV: '',
        },
    )
    @patch('src.utils.scrapers.YoutubeDL')
    def test_carrega_legendas_tenta_sem_cookies_quando_dpapi_falha(self, mock_youtube_dl):
        second_context = MagicMock()
        ydl = second_context.__enter__.return_value
        ydl.extract_info.return_value = {
            'subtitles': {},
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
        response.read.return_value = b'{"events": [{"segs": [{"utf8": "legenda ok"}]}]}'
        ydl.urlopen.return_value = response
        mock_youtube_dl.side_effect = [
            RuntimeError('Failed to decrypt with DPAPI'),
            second_context,
        ]

        with self.assertLogs('src.utils.scrapers', level='WARNING'):
            text, error = _carrega_legendas_yt_dlp('https://youtu.be/abc123')

        self.assertEqual(text, 'legenda ok')
        self.assertEqual(error, '')
        first_options = mock_youtube_dl.call_args_list[0].args[0]
        second_options = mock_youtube_dl.call_args_list[1].args[0]
        self.assertIn('cookiesfrombrowser', first_options)
        self.assertNotIn('cookiesfrombrowser', second_options)

    @patch('src.utils.scrapers.YoutubeDL')
    def test_baixa_audio_usa_download_do_ytdlp(self, mock_youtube_dl):
        with tempfile.TemporaryDirectory() as temp_dir:
            ydl = mock_youtube_dl.return_value.__enter__.return_value

            def cria_arquivo_baixado(_urls):
                Path(temp_dir, 'audio.webm').write_text('audio')
                return 0

            ydl.download.side_effect = cria_arquivo_baixado

            audio_path = _baixa_audio_yt_dlp('https://youtu.be/abc123', temp_dir)

        self.assertEqual(audio_path.name, 'audio.webm')
        ydl.extract_info.assert_not_called()
        ydl.download.assert_called_once_with(['https://youtu.be/abc123'])

    @patch.dict(
        os.environ,
        {
            YOUTUBE_COOKIES_BROWSER_ENV: 'chrome',
            YOUTUBE_COOKIES_PROFILE_ENV: '',
            YOUTUBE_COOKIES_FILE_ENV: '',
        },
    )
    @patch('src.utils.scrapers.YoutubeDL')
    def test_baixa_audio_tenta_sem_cookies_quando_dpapi_falha(self, mock_youtube_dl):
        second_context = MagicMock()
        ydl = second_context.__enter__.return_value

        with tempfile.TemporaryDirectory() as temp_dir:
            def cria_arquivo_baixado(_urls):
                Path(temp_dir, 'audio.webm').write_text('audio')
                return 0

            ydl.download.side_effect = cria_arquivo_baixado
            mock_youtube_dl.side_effect = [
                RuntimeError('Failed to decrypt with DPAPI'),
                second_context,
            ]

            with self.assertLogs('src.utils.scrapers', level='WARNING'):
                audio_path = _baixa_audio_yt_dlp('https://youtu.be/abc123', temp_dir)

        self.assertEqual(audio_path.name, 'audio.webm')
        first_options = mock_youtube_dl.call_args_list[0].args[0]
        second_options = mock_youtube_dl.call_args_list[1].args[0]
        self.assertIn('cookiesfrombrowser', first_options)
        self.assertNotIn('cookiesfrombrowser', second_options)
        ydl.download.assert_called_once_with(['https://youtu.be/abc123'])

    @patch.dict(os.environ, {'CITYBOT_WHISPER_MAX_AUDIO_SECONDS': '60'})
    def test_filtro_duracao_audio_rejeita_video_longo(self):
        message = _filtro_duracao_audio({'duration': 120})

        self.assertIn('excede o limite de 60 segundos', message)

    @patch.dict(os.environ, {YOUTUBE_COOKIES_BROWSER_ENV: '', YOUTUBE_COOKIES_FILE_ENV: '', 'CITYBOT_WHISPER_MAX_AUDIO_SECONDS': ''})
    def test_filtro_duracao_audio_permite_video_de_pouco_mais_de_uma_hora(self):
        self.assertIsNone(_filtro_duracao_audio({'duration': 3886, 'live_status': 'was_live'}))

    def test_filtro_duracao_audio_rejeita_live_em_andamento(self):
        message = _filtro_duracao_audio({'is_live': True, 'live_status': 'is_live'})

        self.assertIn('transmissão terminar', message)

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
