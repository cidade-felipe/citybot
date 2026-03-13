import os
import sqlite3
import pyperclip
import requests
from bs4 import BeautifulSoup
from pypdf import PdfReader
from youtube_transcript_api import YouTubeTranscriptApi
from docx import Document
from dotenv import load_dotenv
from PIL import Image
from google import genai
from google.genai import types

os.makedirs('textos', exist_ok=True)  

class CityBot:
    def __init__(self):
        load_dotenv()
        self.api_key = os.getenv('GEMINI_API_KEY')
        if not self.api_key:
            print("ERRO: GOOGLE_API_KEY não encontrada no arquivo .env")
        
        self.client = genai.Client(api_key=self.api_key)
        self.model_name = os.getenv('GEMINI_MODEL')        
        self.conexao = sqlite3.connect('citybot.db')
        self.create_table()

    def create_table(self):
        with self.conexao:
            self.conexao.execute("""
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY,
                user_message TEXT,
                assistant_response TEXT
            )
            """)
            self.conexao.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                name TEXT,
                preferences TEXT
            )
            """)

    def save_conversation(self, user_message, assistant_response):
        with self.conexao:
            self.conexao.execute("INSERT INTO conversations (user_message, assistant_response) VALUES (?, ?)", (user_message, assistant_response))

    def load_conversations(self):
        with self.conexao:
            return self.conexao.execute("SELECT user_message, assistant_response FROM conversations").fetchall()

    def resposta_bot(self, mensagens, documento=''):
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

    def carrega_site(self, url_site):
        try:
            headers = {'User-Agent': 'Mozilla/5.0'}
            response = requests.get(url_site, headers=headers)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            for script in soup(["script", "style"]):
                script.decompose()
            
            texto = soup.get_text(separator=' ')
            lines = (line.strip() for line in texto.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            return '\n'.join(chunk for chunk in chunks if chunk)
        except Exception as e:
            print(f'Erro ao carregar o site: {e}')
            return ''

    def carrega_video(self, url_video):
        try:
            video_id = None
            if "v=" in url_video:
                video_id = url_video.split("v=")[1].split("&")[0]
            elif "youtu.be" in url_video:
                video_id = url_video.split("/")[-1]
            
            if not video_id:
                return "ID do vídeo não encontrado."

            api = YouTubeTranscriptApi()
            transcript_list = api.fetch(video_id, languages=['pt', 'en'])
            
            textos = []
            for t in transcript_list:
                if isinstance(t, dict) and 'text' in t:
                    textos.append(t['text'])
                elif hasattr(t, 'text'):
                    textos.append(t.text)
                    
            return " ".join(textos)
            
        except Exception as e:
            print(f'Erro ao carregar o vídeo: {e}')
            return ''

    def carrega_pdf(self, caminho):
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

    def carrega_imagem_ocr(self, caminho, nome):
        try:
            if not os.path.exists(caminho):
                raise FileNotFoundError(f'Arquivo não encontrado: {caminho}')
            
            print("Enviando imagem para o Gemini analisar...")
            imagem = Image.open(caminho)
            prompt = "Por favor, extraia e transcreva todo o texto visível nesta imagem. Mantenha a formatação original (como tabelas ou listas) na medida do possível. Se não houver texto, apenas descreva o que tem na imagem."
            
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=[imagem, prompt]
            )
            
            texto_final = response.text
            self.salvar_texto(texto_final, nome)
            return texto_final
            
        except Exception as e:
            print(f'Erro ao processar a imagem com Gemini: {e}')
            return ''
        
    def salvar_texto(self, texto, nome):
        try:
            documento = Document()
            documento.add_paragraph(texto)
            documento.save(f'textos/{nome}.docx')
            with open(f'textos/{nome}.txt', 'w', encoding='utf-8') as file:
                file.write(texto)
            return texto
        except Exception as e:
            print(f'Erro ao salvar texto: {e}')
            return ''

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

if __name__ == '__main__':
    city_bot = CityBot()
    city_bot.menu()