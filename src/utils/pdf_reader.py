import logging
import os

from pypdf import PdfReader


logger = logging.getLogger(__name__)


def carrega_pdf(caminho):
    try:
        if not os.path.exists(caminho):
            raise FileNotFoundError(f'Arquivo não encontrado: {caminho}')
        
        reader = PdfReader(caminho)
        paginas = [page.extract_text() or '' for page in reader.pages]
        return '\n'.join(paginas)
    except Exception as e:
        logger.error('Erro ao carregar o PDF: %s', e)
        return ''
