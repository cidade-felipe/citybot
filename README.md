# CityBot

CityBot é um assistente inteligente em Python que combina modelos de linguagem, OCR, leitura de PDFs, páginas da web e vídeos do YouTube em uma única interface.
Ele permite conversar em linguagem natural sobre o conteúdo de arquivos e links, além de manter histórico em um banco SQLite e contar com memória de conversas.

<div align="center">

![Status](https://img.shields.io/badge/status-em%20desenvolvimento-yellow)
![License](https://img.shields.io/badge/license-MIT-green)
![Python](https://img.shields.io/badge/python-3.x-blue)
![Interface](https://img.shields.io/badge/interface-CLI%20%7C%20Tkinter-lightblue)

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
- Oferecer interação tanto por linha de comando quanto por interface gráfica desenvolvida em Tkinter

Ele suporta opções de inteligência artificial através das APIs da Groq ou Google Gemini, integrando várias fontes de informação num fluxo único de conversa.

---

## Principais funcionalidades

- Chat em linguagem natural com modelos LLM via Groq ou Gemini
- Leitura de conteúdo de sites com `WebBaseLoader`
- Transcrição de vídeos do YouTube com `YoutubeLoader`
- Leitura de PDFs com `PyPDFLoader`
- OCR de imagens com OpenCV + Tesseract + langdetect
- Salvamento de texto de imagens em `.docx` e `.txt`
- Histórico de conversas e usuários em SQLite
- Interface de linha de comando com menu interativo
- Interface gráfica com Tkinter, área de chat e botões para PDF, site e imagem

---

## Estrutura do Projeto

O projeto segue agora uma estrutura modular organizada na pasta `src/`:

```text
citybot/
├── main.py                 # Ponto de entrada unificado (CLI e GUI)
├── logo.png                # Logo da aplicação
├── requirements.txt        # Dependências
├── .env                    # Configurações de API
│
├── src/
│   ├── core/               # Lógica de negócio e banco de dados
│   │   ├── database.py     # Gerenciamento SQLite
│   │   ├── bot_groq.py     # Implementação Groq
│   │   └── bot_gemini.py   # Implementação Gemini
│   │
│   ├── gui/                # Interfaces gráficas (Tkinter)
│   │   ├── app_groq.py
│   │   └── app_gemini.py
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

1. **Core (`src/core`)**: Contém a inteligência e o banco de dados. As classes `CityBotGroq` e `CityBotGemini` gerenciam o fluxo de mensagens e persistência.
2. **GUI (`src/gui`)**: Responsável exclusiva pela apresentação visual e eventos do Tkinter.
3. **Utils (`src/utils`)**: Contém funções puras para extração de dados (OCR, Web, YouTube, PDF), facilitando a reutilização e testes.

---

## Tecnologias utilizadas

- Python 3.x
- LangChain (com `ChatGroq` e `ChatPromptTemplate`)
- Groq API e Google Gemini API para modelos de linguagem
- SQLite (via `sqlite3`)
- Tkinter (interface gráfica)
- OpenCV (`cv2`)
- Tesseract OCR (`pytesseract`)
- `langdetect` para detectar idioma do texto
- `python-docx` para gerar arquivos `.docx`
- `pyperclip` para integração com área de transferência
- `python-dotenv` para carregamento de variáveis de ambiente
- `Pillow` (PIL) para tratar imagem do logo na interface

---

## Requisitos

Lista geral de dependências principais:

```text
python-dotenv
langchain
langchain-groq
langchain-community
pytesseract
opencv-python
python-docx
langdetect
pyperclip
pillow
pypdf
yt-dlp ou dependências do YoutubeLoader
```

Requisitos externos:

* Tesseract instalado na máquina e acessível pelo sistema
* Uma chave de API válida da Groq ou do Google Gemini, dependendo de qual modelo for utilizado

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
```

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

Há também um método `limpar_banco` que remove todas as tabelas, caso seja necessário começar do zero.

---

## Como executar

O CityBot agora possui um ponto de entrada único: `main.py`.

### 1. Instalação básica

```bash
git clone https://github.com/cidade-felipe/citybot.git
cd citybot
pip install -r requirements.txt
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
```

#### Linha de Comando (CLI)

```bash
# Iniciar CLI com Gemini
python main.py --mode cli

# Iniciar CLI com Groq
python main.py --provider groq --mode cli
```

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
