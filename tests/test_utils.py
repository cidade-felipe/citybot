import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

from src.utils.file_writer import salvar_texto
from src.utils.pdf_reader import carrega_pdf
from src.utils.scrapers import (
    REQUEST_TIMEOUT_SECONDS,
    _extrai_video_id,
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
            languages=['pt', 'en'],
        )


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
