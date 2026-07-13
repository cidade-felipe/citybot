import logging
import re

from docx import Document

from src.utils.paths import project_path


logger = logging.getLogger(__name__)
INVALID_FILENAME_CHARS = re.compile(r'[<>:"/\\|?*\x00-\x1f]')
TEXTOS_DIR = project_path('textos')


def _nome_seguro(nome):
    nome_base = re.split(r'[/\\]', str(nome))[-1]
    nome_base = INVALID_FILENAME_CHARS.sub('_', nome_base).strip(' .')

    for extensao in ('.docx', '.txt'):
        if nome_base.lower().endswith(extensao):
            nome_base = nome_base[:-len(extensao)].rstrip(' .')

    if not nome_base or nome_base in {'.', '..'}:
        raise ValueError('Informe um nome de arquivo válido.')

    return nome_base


def salvar_texto(texto, nome):
    nome_seguro = _nome_seguro(nome)
    pasta_textos = TEXTOS_DIR

    try:
        pasta_textos.mkdir(exist_ok=True)
        documento = Document()
        documento.add_paragraph(texto)
        path_docx = pasta_textos / f'{nome_seguro}.docx'
        path_txt = pasta_textos / f'{nome_seguro}.txt'
        documento.save(path_docx)
        with path_txt.open('w', encoding='utf-8') as file:
            file.write(texto)
        return texto
    except Exception as e:
        logger.error('Erro ao salvar texto: %s', e)
        return ''
