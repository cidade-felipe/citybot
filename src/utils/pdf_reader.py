import os
from pypdf import PdfReader

def carrega_pdf(caminho):
    try:
        if not os.path.exists(caminho):
            raise FileNotFoundError(f'Arquivo não encontrado: {caminho}')
        
        reader = PdfReader(caminho)
        texto_completo = ""
        for page in reader.pages:
            texto_completo += page.extract_text() + "\n"
        return texto_completo
    except Exception as e:
        print(f'Erro ao carregar o PDF: {e}')
        return ''
