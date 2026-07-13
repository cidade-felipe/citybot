import os
import pyperclip
from dotenv import load_dotenv
from google import genai
from google.genai import types

from src.core.database import CityBotDatabase
from src.utils.scrapers import carrega_site, carrega_video
from src.utils.pdf_reader import carrega_pdf
from src.utils.ocr import carrega_imagem_ocr_gemini

class CityBotGemini:
    REQUIRED_ENV = (
        'GEMINI_API_KEY',
        'GEMINI_MODEL',
    )

    def __init__(self):
        load_dotenv()
        self.api_key = os.getenv('GEMINI_API_KEY')
        self.model_name = os.getenv('GEMINI_MODEL')
        self.config_error = self._validate_config()

        self.client = None
        if not self.config_error:
            self.client = genai.Client(api_key=self.api_key)
        
        self.db = CityBotDatabase()

    def _validate_config(self):
        missing = [name for name in self.REQUIRED_ENV if not os.getenv(name)]
        if not missing:
            return ''

        return 'Variaveis de ambiente ausentes para Gemini: ' + ', '.join(missing)

    def carrega_site(self, url):
        return carrega_site(url)
        
    def carrega_video(self, url):
        return carrega_video(url)
        
    def carrega_pdf(self, path):
        return carrega_pdf(path)
        
    def carrega_imagem_ocr(self, path, nome):
        if self.config_error:
            return ''
        return carrega_imagem_ocr_gemini(path, self.client, self.model_name)

    def save_conversation(self, user_message, assistant_response):
        self.db.save_conversation(user_message, assistant_response)

    def load_conversations(self):
        return self.db.load_conversations()

    def limpar_conversas(self):
        self.db.limpar_conversas()

    def limpar_banco(self):
        self.db.limpar_banco()

    def resposta_bot(self, mensagens, documento=''):
        if self.config_error:
            return f'Erro de configuracao Gemini: {self.config_error}'

        instrucao_sistema = (
            f"Você é um assistente amigável chamado CityBot. "
            f"Você é capaz de conversar sobre qualquer assunto. "
            f"Use as seguintes informações como contexto principal se houver dúvida: {documento}"
        )

        config = types.GenerateContentConfig(
            system_instruction=instrucao_sistema,
            temperature=0.7
        )

        historico_formatado = []
        for tipo, conteudo in mensagens[:-1]:
            role = 'user' if tipo in ['user', 'human'] else 'model'
            historico_formatado.append(
                types.Content(
                    role=role, 
                    parts=[types.Part.from_text(text=conteudo)]
                )
            )

        try:
            chat = self.client.chats.create(
                model=self.model_name,
                config=config,
                history=historico_formatado
            )
            
            ultima_mensagem = mensagens[-1][1] if mensagens else ""
            
            response = chat.send_message(ultima_mensagem)
            return response.text
            
        except Exception as e:
            return f"Erro na API do Gemini: {e}"

    def menu(self):
        pyperclip.copy('')
        menu_txt = 'MENU\n1. Bora conversar?\n2. Informações sobre um site\n3. Informações sobre um vídeo do YouTube\n4. Informações sobre um PDF\n5. OCR imagem\n6. Sair'
        print(menu_txt)
        nova_informacao = ''
        
        dados_banco = self.load_conversations()
        mensagens = []
        for user_msg, bot_msg in dados_banco:
            mensagens.append(('user', user_msg))
            mensagens.append(('assistant', bot_msg))

        while True:
            opcao = input('\nEscolha uma opção: ')
            
            if opcao == '6':
                print('Saindo...')
                break
            elif opcao not in '12345':
                print('Opção inválida!')
                continue
                
            if opcao == '2':
                url_site = input('Informe a URL do site: ').strip()
                print("Carregando site...")
                nova_informacao = self.carrega_site(url_site)
            elif opcao == '3':
                url_video = input('Informe a URL do vídeo: ').strip()
                print("Carregando transcrição do vídeo...")
                nova_informacao = self.carrega_video(url_video)
            elif opcao == '4':
                caminho_pdf = input('Informe o caminho do PDF: ').strip().replace('\\', '/').replace('"','')
                print("Lendo PDF...")
                nova_informacao = self.carrega_pdf(caminho_pdf)
            elif opcao == '5':
                caminho_imagem = input('Informe o caminho da imagem: ').strip().replace('\\', '/').replace('"','')
                nome_imagem = input('Informe o nome da imagem (para salvar): ').strip().replace('\\', '/').replace('"','')
                nova_informacao = self.carrega_imagem_ocr(caminho_imagem, nome_imagem)
            
            if opcao in '2345':
                print(f'\n--- Contexto carregado ({len(nova_informacao)} caracteres) ---')
                
            print('\nDigite sua mensagem (ou "menu" para voltar, "sair" para encerrar):')
            
            while True:
                paste = pyperclip.paste()
                if not paste:
                    pergunta = input("\nVocê: ")
                else:
                    print("\nDetectado na área de transferência (pressione Enter para usar ou digite algo):")
                    entrada_manual = []
                    while True:
                        linha = input()
                        if linha == '' and not entrada_manual: 
                            pergunta = paste
                            break
                        if linha == '' and entrada_manual: 
                            pergunta = '\n'.join(entrada_manual)
                            break
                        entrada_manual.append(linha)
                    pyperclip.copy('') 

                if pergunta.lower().strip() == 'menu':
                    print("\n" + menu_txt)
                    break 
                if pergunta.lower().strip() == 'sair':
                    print('Saindo...')
                    exit()

                if not pergunta.strip():
                    continue

                mensagens.append(('user', pergunta))
                
                print("CityBot digitando...")
                resposta = self.resposta_bot(mensagens, nova_informacao)
                
                mensagens.append(('assistant', resposta))
                self.save_conversation(pergunta, resposta)
                
                print(f"\nCityBot: {resposta}")
