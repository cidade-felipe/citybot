import os

def carrega_imagem_ocr_tesseract(caminho):
    import cv2
    import pytesseract
    from langdetect import LangDetectException, detect
    
    try:
        if not os.path.exists(caminho):
            raise FileNotFoundError(f'Arquivo não encontrado: {caminho}')
            
        imagem = cv2.imread(caminho)
        imagem_cinza = cv2.cvtColor(imagem, cv2.COLOR_BGR2GRAY)
        imagem_tratada = cv2.threshold(imagem_cinza, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
        texto_bruto = pytesseract.image_to_string(imagem_tratada, config='--psm 6')
        
        try:
            idioma = detect(texto_bruto)
        except LangDetectException:
            idioma = None
            
        map_idioma = {
            'pt': 'por', 'en': 'eng', 'es': 'spa', 'fr': 'fra', 'de': 'deu',
            'it': 'ita', 'ru': 'rus', 'ja': 'jpn', 'zh-cn': 'chi_sim',
            'zh-tw': 'chi_tra', 'ko': 'kor', 'ar': 'ara', 'nl': 'nld',
            'pl': 'pol', 'tr': 'tur', 'da': 'dan', 'fi': 'fin',
            'sv': 'swe', 'no': 'nor',
        }
        
        idioma_tesseract = map_idioma.get(idioma, 'por')
        
        if idioma_tesseract:
            texto_final = pytesseract.image_to_string(imagem_tratada, lang=idioma_tesseract, config='--psm 6')
        else:
            texto_final = texto_bruto
            
        return texto_final
        
    except Exception as e:
        print(f'Erro ao processar OCR com Tesseract: {e}')
        return ''

def carrega_imagem_ocr_gemini(caminho, client, model_name):
    from PIL import Image
    try:
        if not os.path.exists(caminho):
            raise FileNotFoundError(f'Arquivo não encontrado: {caminho}')
            
        print("Enviando imagem para o Gemini analisar...")
        imagem = Image.open(caminho)
        prompt = "Por favor, extraia e transcreva todo o texto visível nesta imagem. Mantenha a formatação original (como tabelas ou listas) na medida do possível. Se não houver texto, apenas descreva o que tem na imagem."
        
        response = client.models.generate_content(
            model=model_name,
            contents=[imagem, prompt]
        )
        
        return response.text
        
    except Exception as e:
        print(f'Erro ao processar a imagem com Gemini: {e}')
        return ''
