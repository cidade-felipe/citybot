import os
import sqlite3
import cv2
import pytesseract
from langchain_groq import ChatGroq
from langchain.prompts import ChatPromptTemplate
from langchain.memory import ConversationBufferWindowMemory
import pyperclip
from langchain_community.document_loaders import PyPDFLoader, WebBaseLoader, YoutubeLoader
from docx import Document
from dotenv import load_dotenv
from langdetect import detect, LangDetectException

class CityBot:
    def __init__(self):
        load_dotenv()
        self.api_key = os.getenv('GROQ_API_KEY')
        self.api_model = os.getenv('GROQ_API_MODEL')
        self.conexao = sqlite3.connect('citybot.db')
        self.create_table()
        self.memory = ConversationBufferWindowMemory(k=1000000)

    def create_table(self):
        with self.conexao:
            self.conexao.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                name TEXT,
                preferences TEXT
            )
            """)

            self.conexao.execute("""
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY,
                user_message TEXT,
                assistant_response TEXT
            )
            """)

    def save_user(self, name, preferences):
        with self.conexao:
            self.conexao.execute("INSERT INTO users (name, preferences) VALUES (?, ?)", (name, preferences))

    def load_user(self, name):
        with self.conexao:
            return self.conexao.execute("SELECT * FROM users WHERE name = ?", (name,)).fetchone()

    def save_conversation(self, user_message, assistant_response):
        with self.conexao:
            self.conexao.execute("INSERT INTO conversations (user_message, assistant_response) VALUES (?, ?)", (user_message, assistant_response))

    def load_conversations(self):
        with self.conexao:
            return self.conexao.execute("SELECT user_message, assistant_response FROM conversations").fetchall()

    def chat(self):
        return ChatGroq(model=self.api_model)

    def resposta_bot(self, mensagens, documento=''):
        mensagem_sistema = 'Você é um assistente amigável chamado CityBot, capaz de conversar sobre qualquer assunto, inclusive qualquer informação sobre {informacoes}.'
        informacoes = documento or ''
        mensagem_modelo = [('system', mensagem_sistema.format(informacoes=informacoes))]
        for tipo, conteudo in mensagens:
            if tipo not in ['user', 'assistant']:
                tipo = 'user' if tipo == 'human' else 'assistant'
            mensagem_modelo.append((tipo, conteudo))
        template = ChatPromptTemplate.from_messages(mensagem_modelo)
        chain = template | self.chat()
        return chain.invoke({'informacoes': informacoes}).content

    def carrega_site(self, url_site):
        try:
            loader = WebBaseLoader(url_site)
            return ''.join(doc.page_content for doc in loader.load())
        except Exception as e:
            print(f'Erro ao carregar o site: {e}')
            return ''

    def carrega_video(self, url_video):
        try:
            loader = YoutubeLoader.from_youtube_url(url_video)
            return ''.join(doc.page_content for doc in loader.load())
        except Exception as e:
            print(f'Erro ao carregar o vídeo: {e}')
            return ''

    def carrega_pdf(self, caminho):
        try:
            if not os.path.exists(caminho):
                raise FileNotFoundError(f'Arquivo não encontrado: {caminho}')
            loader = PyPDFLoader(caminho)
            return ''.join(doc.page_content for doc in loader.load())
        except Exception as e:
            print(f'Erro ao carregar o PDF: {e}')
            return ''

    def carrega_imagem_ocr(self, caminho, nome):
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
                'pt': 'por',
                'en': 'eng',
                'es': 'spa',
                'fr': 'fra',
                'de': 'deu',
                'it': 'ita',
                'ru': 'rus',
                'ja': 'jpn',
                'zh-cn': 'chi_sim',
                'zh-tw': 'chi_tra',
                'ko': 'kor',
                'ar': 'ara',
                'nl': 'nld',
                'pl': 'pol',
                'tr': 'tur',
                'da': 'dan',
                'fi': 'fin',
                'sv': 'swe',
                'no': 'nor',
            }
            idioma_tesseract = map_idioma.get(idioma, 'por')
            if idioma_tesseract:
                texto_final = pytesseract.image_to_string(imagem_tratada, lang=idioma_tesseract, config='--psm 6')
            else:
                texto_final = texto_bruto
            self.salvar_texto(texto_final, nome)
            return texto_final
        except Exception as e:
            print(f'Erro ao carregar a imagem: {e}')
            return ''
        
    def salvar_texto(self,texto, nome):
        try:
            documento = Document()
            documento.add_paragraph(texto)
            documento.save(f'{nome}.docx')
            with open(f'{nome}.txt', 'w', encoding='utf-8') as file:
                file.write(texto)
            return texto
        except Exception as e:
            print(f'Erro ao salvar a imagem: {e}')
            return ''

    def limpar_banco(self):
        cursor = self.conexao.cursor()

        # Obter lista de tabelas existentes
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tabelas = cursor.fetchall()

        # Deletar todas as tabelas
        for (tabela,) in tabelas:
            cursor.execute(f"DROP TABLE IF EXISTS {tabela}")

        self.conexao.commit()
            

    def menu(self):
        memory = self.memory
        pyperclip.copy('')
        menu = 'MENU\n1. Bora conversar?\n2. Informações sobre um site\n3. Informações sobre um vídeo do YouTube\n4. Informações sobre um PDF\n5. OCR imagem\n6. Sair'
        print(menu)
        nova_informacao = ''
        mensagens = list(self.load_conversations())
        while True:
            opcao = input('Escolha uma opção: ')
            if opcao not in '123456':
                print('Opção inválida!')
            else:
                if opcao == '1':
                    print('Comece a conversar ou digite "menu" para voltar ao menu. Digite "sair" para sair do programa')
                    while True:
                        paste = pyperclip.paste()
                        if not paste:
                            pergunta = input()
                            if pergunta.lower().strip() == 'menu':
                                print(menu)
                                break
                            if pergunta.lower().strip() == 'sair':
                                print('Saindo...')
                                exit()
                            mensagens.append(('user', pergunta))
                            resposta = self.resposta_bot(mensagens, nova_informacao)
                            mensagens.append(('assistant', resposta))
                            memory.save_context({'input': pergunta}, {'output': resposta})
                            self.save_conversation(pergunta, resposta)
                            print()
                            print(resposta)
                        else:
                            pergunta = []
                            while True:
                                linha = input()
                                if linha == 'menu':
                                    print(menu)
                                    break
                                if linha == '':
                                    break
                                if linha == 'sair':
                                    print('Saindo...')
                                    exit()
                                pergunta.append(linha)
                            pergunta = '\n'.join(pergunta).strip()
                            mensagens.append(('user', pergunta))
                            resposta = self.resposta_bot(mensagens, nova_informacao)
                            mensagens.append(('assistant', resposta))
                            memory.save_context({'input': pergunta}, {'output': resposta})
                            self.save_conversation(pergunta, resposta)
                            print()
                            print(resposta)
                            pyperclip.copy('')
                elif opcao == '2':
                    url_site = input('Informe a URL do site: ').strip()
                    nova_informacao = self.carrega_site(url_site)
                    print('Me faça perguntas sobre esse site. Digite "menu" para voltar ao menu ou "sair" para sair do programa')
                    while True:
                        pergunta = input()
                        if pergunta.lower().strip() == 'menu':
                            print(menu)
                            break
                        if pergunta.lower().strip() == 'sair':
                            print('Saindo...')
                            exit()
                        mensagens.append(('user', pergunta))
                        resposta = self.resposta_bot(mensagens, nova_informacao)
                        mensagens.append(('assistant', resposta))
                        memory.save_context({'input': pergunta}, {'output': resposta})
                        self.save_conversation(pergunta, resposta)
                        print()
                        print(resposta)
                elif opcao == '3':
                    url_video = input('Informe a URL do vídeo: ').strip()
                    nova_informacao = self.carrega_video(url_video)
                    print('Faça perguntas sobre o vídeo. Digite "menu" para voltar ao menu ou "sair" para sair do programa')
                    while True:
                        pergunta = input('')
                        if pergunta.lower().strip() == 'menu':
                            print(menu)
                            break
                        if pergunta.lower().strip() == 'sair':
                            print('Saindo...')
                            exit()
                        mensagens.append(('user', pergunta))
                        resposta = self.resposta_bot(mensagens, nova_informacao)
                        mensagens.append(('assistant', resposta))
                        memory.save_context({'input': pergunta}, {'output': resposta})
                        self.save_conversation(pergunta, resposta)
                        print()
                        print(resposta)
                elif opcao == '4':
                    caminho_pdf = input('Informe o caminho do PDF: ').strip().replace('\\', '/').replace('"','')
                    nova_informacao = self.carrega_pdf(caminho_pdf)
                    print('Me faça perguntas sobre esse PDF. Digite "menu" para voltar ao menu ou "sair" para sair do programa')
                    while True:
                        pergunta = input()
                        if pergunta.lower().strip() == 'menu':
                            print(menu)
                            break
                        if pergunta.lower().strip() == 'sair':
                            print('Saindo...')
                            exit()
                        mensagens.append(('user', pergunta))
                        resposta = self.resposta_bot(mensagens, nova_informacao)
                        mensagens.append(('assistant', resposta))
                        memory.save_context({'input': pergunta}, {'output': resposta})
                        self.save_conversation(pergunta, resposta)
                        print()
                        print(resposta)
                elif opcao == '5':
                    caminho_imagem = input('Informe o caminho da imagem: ').strip().replace('\\', '/').replace('"','')
                    nome_imagem = input('Informe o nome da imagem: ').strip().replace('\\', '/').replace('"','')
                    nova_informacao = self.carrega_imagem_ocr(caminho_imagem, nome_imagem)
                    print('OCR imgem. Digite "menu" para voltar ao menu ou "sair" para sair do programa')
                    while True:
                        pergunta = input('')
                        if pergunta.lower().strip() == 'menu':
                            print(menu)
                            break
                        if pergunta.lower().strip() == 'sair':
                            print('Saindo...')
                            exit()
                        mensagens.append(('user', pergunta))
                        resposta = self.resposta_bot(mensagens, nova_informacao)
                        mensagens.append(('assistant', resposta))
                        memory.save_context({'input': pergunta}, {'output': resposta})
                        self.save_conversation(pergunta, resposta)
                        print()
                        print(resposta)
                elif opcao == '6':
                    print('Saindo...')
                    break

if __name__ == '__main__':
    city_bot = CityBot()
    city_bot.menu()
    # llama-3.3-70b-versatile
    # llama-3.1-8b-instant
    # llama3-70b-8192
    # llama3-8b-8192
    # gemma2-9b-it
    # llama-3.2-1b-preview
    # llama-3.2-3b-preview
    # llama-3.2-11b-vision-preview
    # llama-3.2-90b-vision-preview