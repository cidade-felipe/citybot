import os
import pyperclip
from dotenv import load_dotenv

from langchain.memory import ConversationBufferWindowMemory
from langchain.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq

from src.core.database import CityBotDatabase
from src.utils.scrapers import carrega_site, carrega_video
from src.utils.pdf_reader import carrega_pdf
from src.utils.ocr import carrega_imagem_ocr_tesseract
from src.utils.file_writer import salvar_texto

class CityBotGroq:
    def __init__(self):
        load_dotenv()
        self.api_model = os.getenv('GROQ_API_MODEL')
        
        self.db = CityBotDatabase()
        self.memory = ConversationBufferWindowMemory(k=1000000)

    def carrega_site(self, url_site):
        return carrega_site(url_site)

    def carrega_video(self, url_video):
        return carrega_video(url_video)

    def carrega_pdf(self, caminho):
        return carrega_pdf(caminho)

    def carrega_imagem_ocr(self, caminho, nome):
        texto_final = carrega_imagem_ocr_tesseract(caminho)
        if texto_final:
            salvar_texto(texto_final, nome)
        return texto_final

    def save_conversation(self, user_message, assistant_response):
        self.db.save_conversation(user_message, assistant_response)

    def load_conversations(self):
        return self.db.load_conversations()

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

    def limpar_banco(self):
        self.db.limpar_banco()

    def menu(self):
        memory = self.memory
        pyperclip.copy('')
        menu = 'MENU\n1. Bora conversar?\n2. Informações sobre um site\n3. Informações sobre um vídeo do YouTube\n4. Informações sobre um PDF\n5. OCR imagem\n6. Sair'
        print(menu)
        nova_informacao = ''
        mensagens = list(self.load_conversations())
        while True:
            opcao = input('\nEscolha uma opção: ')
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
                            if not pergunta.strip(): continue
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
                            if not pergunta: continue
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
                        if not pergunta.strip(): continue
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
                        if not pergunta.strip(): continue
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
                        if not pergunta.strip(): continue
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
                        if not pergunta.strip(): continue
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
