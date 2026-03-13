import os
from docx import Document

def salvar_texto(texto, nome):
    try:
        os.makedirs('textos', exist_ok=True)
        documento = Document()
        documento.add_paragraph(texto)
        path_docx = os.path.join('textos', f'{nome}.docx')
        path_txt = os.path.join('textos', f'{nome}.txt')
        documento.save(path_docx)
        with open(path_txt, 'w', encoding='utf-8') as file:
            file.write(texto)
        return texto
    except Exception as e:
        print(f'Erro ao salvar texto: {e}')
        return ''
