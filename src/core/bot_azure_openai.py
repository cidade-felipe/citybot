import os
import pyperclip
from dotenv import load_dotenv
from openai import AzureOpenAI

from src.core.database import CityBotDatabase
from src.utils.scrapers import carrega_site, carrega_video
from src.utils.pdf_reader import carrega_pdf
from src.utils.ocr import carrega_imagem_ocr_tesseract
from src.utils.file_writer import salvar_texto


class CityBotAzureOpenAI:
    DEFAULT_MAX_OUTPUT_TOKENS = 1200
    REQUIRED_ENV = (
        'AZURE_OPENAI_API_KEY',
        'AZURE_ENDPOINT',
        'AZURE_API_VERSION',
        'AZURE_DEPLOYMENT',
    )

    def __init__(self):
        load_dotenv()
        self.api_key = os.getenv('AZURE_OPENAI_API_KEY')
        self.azure_endpoint = os.getenv('AZURE_ENDPOINT')
        self.api_version = os.getenv('AZURE_API_VERSION')
        self.deployment = os.getenv('AZURE_DEPLOYMENT')
        self.max_output_tokens = self._get_max_output_tokens()
        self.config_error = self._validate_config()

        self.client = None
        if not self.config_error:
            self.client = AzureOpenAI(
                api_key=self.api_key,
                azure_endpoint=self.azure_endpoint,
                api_version=self.api_version,
            )
            if not hasattr(self.client, 'responses'):
                self.config_error = (
                    'A versao instalada do pacote openai nao suporta client.responses.create. '
                    'Atualize as dependencias com pip install -r requirements.txt.'
                )
                self.client = None

        self.db = CityBotDatabase()

    def _validate_config(self):
        missing = [name for name in self.REQUIRED_ENV if not os.getenv(name)]
        if not missing:
            return ''

        return 'Variaveis de ambiente ausentes para Azure OpenAI: ' + ', '.join(missing)

    def _get_max_output_tokens(self):
        value = os.getenv('AZURE_MAX_OUTPUT_TOKENS', str(self.DEFAULT_MAX_OUTPUT_TOKENS))
        try:
            return int(value)
        except ValueError:
            return self.DEFAULT_MAX_OUTPUT_TOKENS

    def carrega_site(self, url):
        return carrega_site(url)

    def carrega_video(self, url):
        return carrega_video(url)

    def carrega_pdf(self, path):
        return carrega_pdf(path)

    def carrega_imagem_ocr(self, path, nome):
        texto_final = carrega_imagem_ocr_tesseract(path)
        if texto_final:
            salvar_texto(texto_final, nome)
        return texto_final

    def save_conversation(self, user_message, assistant_response):
        self.db.save_conversation(user_message, assistant_response)

    def load_conversations(self):
        return self.db.load_conversations()

    def limpar_banco(self):
        self.db.limpar_banco()

    def resposta_bot(self, mensagens, documento=''):
        if self.config_error:
            return f'Erro de configuracao Azure OpenAI: {self.config_error}'

        prompt = self._monta_prompt(mensagens, documento)

        try:
            response = self.client.responses.create(
                model=self.deployment,
                input=prompt,
                max_output_tokens=self.max_output_tokens,
            )
            texto = getattr(response, 'output_text', '') or str(response)
            return self._adiciona_aviso_se_resposta_incompleta(texto, response)
        except Exception as e:
            return f'Erro na API do Azure OpenAI: {e}'

    def _adiciona_aviso_se_resposta_incompleta(self, texto, response):
        incomplete_details = getattr(response, 'incomplete_details', None)
        reason = getattr(incomplete_details, 'reason', '') if incomplete_details else ''
        status = getattr(response, 'status', '')

        if status == 'incomplete' or reason == 'max_output_tokens':
            return (
                f'{texto}\n\n'
                f'[Resposta interrompida pelo limite atual de saída '
                f'({self.max_output_tokens} tokens). '
                f'Aumente AZURE_MAX_OUTPUT_TOKENS no .env para respostas mais longas.]'
            )

        return texto

    def _monta_prompt(self, mensagens, documento=''):
        linhas = [
            'Voce e um assistente amigavel chamado CityBot.',
            'Responda de forma clara, util e direta, porém amigável. Seja conciso, mas completo. Evite respostas vagas ou genéricas.',
        ]

        if documento:
            linhas.extend([
                '',
                'Use as informacoes abaixo como contexto principal quando elas forem relevantes.',
                'Se o contexto nao tiver a resposta, diga isso com clareza.',
                '',
                'Contexto carregado:',
                documento,
            ])

        if mensagens:
            linhas.extend(['', 'Historico da conversa:'])
            for tipo, conteudo in mensagens:
                papel = 'Usuario' if tipo in ['user', 'human'] else 'Assistente'
                linhas.append(f'{papel}: {conteudo}')

        return '\n'.join(linhas)

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
            if opcao not in '12345':
                print('Opção inválida!')
                continue

            if opcao == '2':
                url_site = input('Informe a URL do site: ').strip()
                print('Carregando site...')
                nova_informacao = self.carrega_site(url_site)
            elif opcao == '3':
                url_video = input('Informe a URL do vídeo: ').strip()
                print('Carregando transcrição do vídeo...')
                nova_informacao = self.carrega_video(url_video)
            elif opcao == '4':
                caminho_pdf = input('Informe o caminho do PDF: ').strip().replace('\\', '/').replace('"', '')
                print('Lendo PDF...')
                nova_informacao = self.carrega_pdf(caminho_pdf)
            elif opcao == '5':
                caminho_imagem = input('Informe o caminho da imagem: ').strip().replace('\\', '/').replace('"', '')
                nome_imagem = input('Informe o nome da imagem (para salvar): ').strip().replace('\\', '/').replace('"', '')
                nova_informacao = self.carrega_imagem_ocr(caminho_imagem, nome_imagem)

            if opcao in '2345':
                print(f'\n--- Contexto carregado ({len(nova_informacao)} caracteres) ---')

            print('\nDigite sua mensagem (ou "menu" para voltar, "sair" para encerrar):')

            while True:
                paste = pyperclip.paste()
                if not paste:
                    pergunta = input('\nVocê: ')
                else:
                    print('\nDetectado na área de transferência (pressione Enter para usar ou digite algo):')
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
                    print('\n' + menu_txt)
                    break
                if pergunta.lower().strip() == 'sair':
                    print('Saindo...')
                    exit()

                if not pergunta.strip():
                    continue

                mensagens.append(('user', pergunta))

                print('CityBot digitando...')
                resposta = self.resposta_bot(mensagens, nova_informacao)

                mensagens.append(('assistant', resposta))
                self.save_conversation(pergunta, resposta)

                print(f'\nCityBot: {resposta}')
