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

## Arquitetura em alto nível

O projeto é estruturado em torno da classe `CityBot`, que concentra:

- Conexão com o banco `citybot.db` (SQLite)
- Criação das tabelas `users` e `conversations`
- Métodos de carregamento de dados:
  - `carrega_site`
  - `carrega_video`
  - `carrega_pdf`
  - `carrega_imagem_ocr`
- Método `resposta_bot`, que monta o prompt, envia a requisição ao modelo Groq via LangChain e retorna a resposta
- Métodos de persistência no banco (salvar usuário, carregar usuário, salvar conversa, carregar conversas)
- Menu de linha de comando (`menu`) para interação no terminal

Além disso, há uma camada de interface gráfica em Tkinter que:

- Mostra mensagens do usuário e do bot com cores diferentes
- Permite digitar mensagens de texto
- Possui botões para:
  - Ler site
  - Ler PDF
  - Fazer OCR em imagem
  - Limpar banco de dados
  - Encerrar a aplicação

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
````

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

A estrutura exata de arquivos pode variar, então ajuste o nome do arquivo principal conforme o seu projeto.
Os exemplos abaixo assumem que o arquivo com a classe e o menu CLI é `citybot.py` e que a interface gráfica está no mesmo arquivo ou em um arquivo associado.

### 1. Clonar o repositório

```bash
git clone https://github.com/cidade-felipe/citybot.git
cd citybot
```

### 2. Criar ambiente virtual (opcional)

```bash
python -m venv .venv
source .venv/bin/activate   # Linux / macOS
.\.venv\Scripts\activate    # Windows
```

### 3. Instalar dependências

Se você tiver um `requirements.txt`, use:

```bash
pip install -r requirements.txt
```

Caso ainda não tenha, instale as principais bibliotecas:

```bash
pip install python-dotenv langchain langchain-groq langchain-community pytesseract opencv-python python-docx langdetect pyperclip pillow
```

### 4. Executar o CityBot no terminal (CLI)

Para usar com o modelo da Groq:

```bash
python citybot_groq.py
```

Para usar com o modelo do Google Gemini:

```bash
python citybot_gemini.py
```

O menu oferece opções como:

1. Conversar
2. Informações sobre um site
3. Informações sobre um vídeo do YouTube
4. Informações sobre um PDF
5. OCR de imagem
6. Sair

### 5. Executar o CityBot com interface gráfica (Tkinter)

A interface gráfica possui scripts dedicados para cada provedor de IA na pasta `gui`:

Para rodar a interface usando o modelo da Groq:

```bash
python gui/gui_groq.py
```

Para rodar a interface usando o modelo do Google Gemini:

```bash
python gui/gui_gemini.py
```

A interface de chat permite:

* Escrever mensagens para o CityBot
* Carregar PDF, site e imagem por botões
* Mostrar respostas formatadas em balões coloridos
* Rolagem automática das mensagens

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
* Organizar o projeto em pacotes (`src/`) para facilitar manutenção
* Adicionar logs mais detalhados de erros
* Integrar com outras fontes, como arquivos `.docx` diretos ou bancos externos

---

## Autor

Felipe Cidade

---

## Licença

Este projeto está licenciado sob a licença MIT.
Veja o arquivo `LICENSE` para mais detalhes.