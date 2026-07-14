# CityBot

CityBot é um assistente inteligente em Python que combina modelos de linguagem, OCR, leitura de PDFs, páginas da web e vídeos do YouTube em uma única interface.
Ele permite conversar em linguagem natural sobre o conteúdo de arquivos e links, além de manter histórico em um banco SQLite e contar com memória de conversas.

<div align="center">

![Status](https://img.shields.io/badge/status-em%20desenvolvimento-yellow)
![License](https://img.shields.io/badge/license-MIT-green)
![Python](https://img.shields.io/badge/python-3.x-blue)
![Interface](https://img.shields.io/badge/interface-CLI%20%7C%20PySide6-lightblue)

</div>

---

## Visão geral

O CityBot foi pensado como um assistente pessoal para estudo e trabalho, capaz de:

- Conversar em linguagem natural sobre qualquer assunto
- Ler e resumir PDFs
- Ler e interpretar páginas da web
- Transcrever e analisar vídeos do YouTube
- Ler texto em imagens usando OCR e salvar o resultado
- Manter histórico de conversas em um banco SQLite
- Oferecer interação tanto por linha de comando quanto por interface gráfica desenvolvida em PySide6

Ele suporta opções de inteligência artificial através das APIs da Groq, Google Gemini ou Azure OpenAI, integrando várias fontes de informação num fluxo único de conversa.

---

## Principais funcionalidades

- Chat em linguagem natural com modelos LLM via Groq, Gemini ou Azure OpenAI
- Leitura de conteúdo de sites com `requests` e `BeautifulSoup`
- Transcrição de vídeos do YouTube com `youtube-transcript-api` e fallback de legendas via `yt-dlp`
- Leitura de PDFs com `pypdf`
- OCR de imagens com OpenCV + Tesseract + langdetect
- Salvamento de texto de imagens em `.docx` e `.txt`
- Histórico de conversas e usuários em SQLite
- Interface de linha de comando com menu interativo
- Interface gráfica com PySide6, área de chat e botões para PDF, site e imagem

---

## Estrutura do Projeto

O projeto segue agora uma estrutura modular organizada na pasta `src/`:

```text
citybot/
├── main.py                 # Ponto de entrada unificado (CLI e GUI)
├── requirements.txt        # Dependências
├── codex.md                # Documentação técnica viva
├── .env                    # Configurações de API
├── tests/                  # Testes automatizados
│
├── src/
│   ├── core/               # Lógica de negócio e banco de dados
│   │   ├── database.py     # Gerenciamento SQLite
│   │   ├── bot_groq.py     # Implementação Groq
│   │   ├── bot_gemini.py   # Implementação Gemini
│   │   └── bot_azure_openai.py # Implementação Azure OpenAI
│   │
│   ├── gui/                # Interface gráfica PySide6
│   │   ├── app_pyside.py   # Base visual reutilizada pelos providers
│   │   ├── app_groq.py
│   │   ├── app_gemini.py
│   │   ├── app_azure_openai.py
│   │   └── markdown_renderer.py # Renderer legado Tkinter
│   │
│   └── utils/              # Funções utilitárias (OCR, Scrapers, PDF)
│       ├── scrapers.py
│       ├── pdf_reader.py
│       ├── ocr.py
│       └── file_writer.py
```

---

## Arquitetura e Organização

A refatoração dividiu as responsabilidades em níveis:

1. **Core (`src/core`)**: Contém a inteligência e o banco de dados. As classes `CityBotGroq`, `CityBotGemini` e `CityBotAzureOpenAI` gerenciam o fluxo de mensagens e persistência.
2. **GUI (`src/gui`)**: Responsável exclusiva pela apresentação visual e eventos da interface PySide6.
3. **Utils (`src/utils`)**: Contém funções puras para extração de dados (OCR, Web, YouTube, PDF), facilitando a reutilização e testes.

---

## Tecnologias utilizadas

- Python 3.x
- LangChain (com `ChatGroq` e `ChatPromptTemplate`)
- Groq API, Google Gemini API e Azure OpenAI para modelos de linguagem
- OpenAI Python SDK (`AzureOpenAI`) para integração com Azure OpenAI
- SQLite (via `sqlite3`)
- PySide6 (interface gráfica)
- OpenCV (`cv2`)
- Tesseract OCR (`pytesseract`)
- `langdetect` para detectar idioma do texto
- `python-docx` para gerar arquivos `.docx`
- `pyperclip` para integração com área de transferência
- `python-dotenv` para carregamento de variáveis de ambiente
- `truststore` para usar os certificados confiáveis do sistema operacional
- `Pillow` (PIL) para tratar imagem do logo na interface

---

## Requisitos

Lista geral de dependências principais:

```text
python-dotenv
langchain
langchain-groq
google-genai
openai
requests
beautifulsoup4
youtube-transcript-api
yt-dlp
truststore
pytesseract
opencv-python
python-docx
langdetect
pyperclip
pillow
pypdf
PySide6
```

Requisitos externos:

* Tesseract instalado na máquina e acessível pelo sistema
* Uma chave de API válida da Groq, Google Gemini ou Azure OpenAI, dependendo de qual provedor for utilizado
* Para Azure OpenAI com `responses.create`, use `openai>=1.68.0`

---

## Configuração das variáveis de ambiente

O CityBot espera encontrar as variáveis abaixo em um arquivo `.env` na raiz do projeto:

```text
# Para utilizar a versão com Groq
GROQ_API_KEY=SuaChaveAqui
GROQ_API_MODEL=nome_do_modelo_groq

# Para utilizar a versão com Google Gemini
GEMINI_API_KEY=SuaChaveAqui
GEMINI_MODEL=nome_do_modelo_gemini

# Para utilizar a versão com Azure OpenAI
AZURE_OPENAI_API_KEY=SuaChaveAqui
AZURE_ENDPOINT=https://seu-recurso.openai.azure.com/
AZURE_API_VERSION=versao_da_api
AZURE_DEPLOYMENT=nome_do_deployment
AZURE_MAX_OUTPUT_TOKENS=1200

# Opcional: ajuda o yt-dlp quando o YouTube bloqueia transcrições anônimas
CITYBOT_YOUTUBE_COOKIES_BROWSER=chrome
CITYBOT_YOUTUBE_COOKIES_PROFILE=Default
CITYBOT_YOUTUBE_COOKIES_FILE=C:\caminho\para\youtube_cookies.txt
```

Se as respostas do Azure OpenAI ficarem cortadas, aumente `AZURE_MAX_OUTPUT_TOKENS`. O valor `300` é baixo para resumos longos, análises e respostas com listas.

Para vídeos do YouTube, as variáveis de cookies são opcionais. Use apenas se aparecer erro `HTTP 429 Too Many Requests` ou bloqueio de transcrição. Valores comuns de `CITYBOT_YOUTUBE_COOKIES_BROWSER`: `chrome`, `edge` ou `firefox`. Se o Chrome/Edge estiver bloqueando o banco de cookies, feche o navegador completamente ou prefira `CITYBOT_YOUTUBE_COOKIES_FILE` com um arquivo `cookies.txt` no formato Netscape. Arquivos JSON, HTML, SQLite ou texto copiado manualmente não são aceitos pelo `yt-dlp`.

Exemplos de modelos da Groq que podem ser usados:

* `llama-3.3-70b-versatile`
* `llama-3.1-8b-instant`
* `gemma2-9b-it`

Exemplos de modelos do Google Gemini que podem ser usados:

* `gemini-2.5-flash`
* `gemini-2.5-pro`

---

## Banco de dados

O arquivo `citybot.db` é criado automaticamente, e as tabelas são:

* `users`

  * `user_id`
  * `name`
  * `preferences`
* `conversations`

  * `id`
  * `user_message`
  * `assistant_response`

Há também um método `limpar_banco` que apaga os registros e preserva as tabelas para que novas conversas possam ser gravadas normalmente.

---

## Como executar

O CityBot agora possui um ponto de entrada único: `main.py`.

### 1. Instalação básica

```powershell
git clone https://github.com/cidade-felipe/citybot.git
cd citybot
python -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

### 2. Configurar o `.env`

Certifique-se de configurar suas chaves no arquivo `.env` (conforme seção abaixo).

### 3. Execução

Você pode escolher o provedor de IA e o modo de interface:

#### Interface Gráfica (Padrão)

```bash
# Iniciar com Gemini (Padrão)
python main.py

# Iniciar interface com Groq
python main.py --provider groq

# Iniciar interface com Azure OpenAI
python main.py --provider azure_openai
```

#### Linha de Comando (CLI)

```bash
# Iniciar CLI com Gemini
python main.py --mode cli

# Iniciar CLI com Groq
python main.py --provider groq --mode cli

# Iniciar CLI com Azure OpenAI
python main.py --provider azure_openai --mode cli
```

---

## Testes

Os testes automatizados usam a biblioteca padrão `unittest` e não acessam APIs externas:

```bash
python -m unittest discover -s tests -v
```

Eles cobrem persistência SQLite, restauração e limpeza do histórico na GUI, scraping com timeout, URLs do YouTube, PDFs com páginas sem texto e segurança dos nomes de arquivos OCR.

---

## Fluxos suportados

Resumo dos fluxos principais:

* Chat livre:
  O usuário conversa diretamente com o CityBot, que responde usando o modelo configurado.
* PDF:
  O bot carrega o PDF, extrai o texto e passa a responder com base nesse conteúdo.
* Site:
  O bot faz o scrape da página indicada e usa o texto carregado como contexto da conversa.
* Vídeo do YouTube:
  O bot carrega a transcrição do vídeo e responde conforme as perguntas sobre o conteúdo.
* Imagem (OCR):
  O bot detecta o texto na imagem, salva em `.docx` e `.txt` e pode responder sobre esse conteúdo.
* Histórico:
  A GUI restaura as conversas salvas ao iniciar. Após confirmação, o botão “Limpar Conversa” apaga o histórico persistido e também remove o contexto carregado, sem excluir perfis de usuário.

---

## Melhorias futuras

Algumas ideias de evolução para o projeto:

* Adicionar seleção de modelos direto na interface
* Criar perfis de usuário com preferências reais
* Adicionar logs mais detalhados de erros
* Integrar com outras fontes, como arquivos `.docx` diretos ou bancos externos

---

## Autor

Felipe Cidade

---

## Licença

Este projeto está licenciado sob a licença MIT.
Veja o arquivo `LICENSE` para mais detalhes.
