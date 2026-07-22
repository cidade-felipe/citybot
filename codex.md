# CityBot - Documento tecnico vivo do projeto

Arquivo criado em 03/06/2026.

Ultima atualizacao documentada: 22/07/2026, apos adicionar geracao de imagens com `gpt-image-2` pela GUI PySide6.

Este documento foi criado para servir como memoria tecnica detalhada do projeto `citybot`. Ele deve ser atualizado sempre que houver alteracao relevante no codigo, dependencias, arquitetura, comportamento, dados, riscos conhecidos ou forma de execucao.

Importante: este arquivo separa explicitamente fato, inferencia e opiniao tecnica.

- Fato: informacao verificada em arquivos do projeto, comandos locais ou estrutura observada.
- Inferencia: deducao baseada no contexto do projeto, mas que nao foi confirmada diretamente por uma especificacao externa.
- Opiniao tecnica: julgamento de engenharia sobre qualidade, risco, trade-off ou melhor caminho.

## 1. Resumo executivo

Fato: o CityBot e um assistente inteligente em Python que combina conversa com LLM, leitura de PDFs, leitura de paginas web, transcricao de videos do YouTube, OCR de imagens e persistencia de historico em SQLite.

Fato: o projeto tem dois provedores de IA implementados:

- Google Gemini, via pacote `google-genai`.
- Azure OpenAI, via pacote `openai` e classe `AzureOpenAI`.

Fato: o ponto de entrada ativo e `main.py`, que permite escolher:

- Provedor: `gemini` ou `azure_openai`.
- Modo: `gui` ou `cli`.

Fato: a interface grafica ativa usa PySide6. A base visual fica em `src/gui/app_pyside.py`; os arquivos dos providers sao wrappers leves sobre essa base:

- `src/gui/app_pyside.py`.
- `src/gui/app_gemini.py`.
- `src/gui/app_azure_openai.py`.

Inferencia: o projeto nasceu ou passou por uma fase de scripts monoliticos, depois foi refatorado para uma estrutura modular em `src/`. A pasta `testes/` contem scripts antigos ou experimentais. A suite automatizada ativa fica em `tests/`.

Opiniao tecnica: o CityBot ja tem uma base funcional boa para uso pessoal, estudo, prototipacao e automacao leve. Para uso em producao, os maiores ganhos viriam de corrigir confiabilidade, seguranca de dados, tratamento de contexto longo, testes automatizados e reducao de duplicacao entre providers.

Impacto pratico:

- Ganho de eficiencia: centraliza analise de PDFs, sites, videos e imagens em uma unica interface.
- Reducao de custo operacional: automatiza leitura e resumo de conteudo que normalmente consumiria tempo manual.
- Mitigacao de risco: com melhorias de validacao, logs e privacidade, pode reduzir perda de informacao e uso acidental de dados sensiveis.
- Potencial de receita: pode virar uma ferramenta de produtividade para atendimento, pesquisa, estudos, analise documental ou suporte interno.

## 2. Estado observado do repositorio

Fato: o diretorio analisado foi:

```text
c:\Users\felip\OneDrive\git_work\citybot
```

Fato: antes da criacao deste arquivo, `codex.md` nao existia.

Fato: o comando `git status --short` estava limpo antes da criacao deste arquivo.

Fato: em 27/06/2026, o `venv` antigo, que referenciava uma instalacao removida do Python 3.11, foi preservado em `Backup/27_06_2026` e substituido por um ambiente limpo com Python 3.12.10. Todas as dependencias de `requirements.txt` foram instaladas, `pip check` nao encontrou conflitos e os 15 modulos diretos importaram corretamente.

Fato: existe uma pasta `Backup` na raiz.

Fato: em 13/07/2026, os arquivos alterados foram preservados em `Backup/13_07_2026` antes das mudancas.

Fato: existe um arquivo `.env` na raiz, mas os valores dele nao foram lidos neste estudo para evitar exposicao de chaves ou configuracoes sensiveis. As variaveis esperadas foram inferidas a partir do codigo e do `README.md`.

Fato: existe um banco local `citybot.db`. A consulta feita leu somente schema e contagem de linhas, nao o conteudo das conversas.

Fato: em 03/06/2026, o banco local tinha:

- Tabela `conversations`, com 6 registros.
- Tabela `users`, com 0 registros.

Fato: a validacao de sintaxe com `python -m py_compile` passou nos arquivos Python ativos:

- `main.py`.
- `src/core/database.py`.
- `src/core/bot_gemini.py`.
- `src/core/bot_azure_openai.py`.
- `src/utils/scrapers.py`.
- `src/utils/pdf_reader.py`.
- `src/utils/ocr.py`.
- `src/utils/file_writer.py`.
- `src/utils/paths.py`.
- `src/gui/app_gemini.py`.
- `src/gui/app_azure_openai.py`.
- `src/gui/app_pyside.py`.
- `src/gui/markdown_renderer.py`.

## 3. Estrutura de arquivos observada

Fato: a estrutura principal observada e:

```text
citybot/
├── main.py
├── README.md
├── requirements.txt
├── requirements-whisperx.txt
├── LICENSE
├── citybot.db
├── .env
├── .gitignore
├── venv/
├── Backup/
├── imagens/
├── textos/
├── testes/
├── tests/
│   ├── test_database.py
│   ├── test_gui_history.py
│   ├── test_provider_config.py
│   └── test_utils.py
└── src/
    ├── core/
    │   ├── database.py
    │   ├── bot_gemini.py
    │   └── bot_azure_openai.py
    ├── gui/
    │   ├── app_pyside.py
    │   ├── app_gemini.py
    │   ├── app_azure_openai.py
    │   └── markdown_renderer.py
    ├── figures/
    │   ├── citybot_banner_minimal.png
    │   ├── citybot_logo.png
    │   ├── citybot_logo.svg
    │   └── logo.png
    └── utils/
        ├── paths.py
        ├── scrapers.py
        ├── pdf_reader.py
        ├── ocr.py
        ├── image_generator.py
        └── file_writer.py
```

Fato: `src/` contem o codigo ativo modular.

Fato: em 03/06/2026, os assets visuais observados estavam em `src/figures/`:

- `citybot_banner_minimal.png`, banner PNG minimalista usado no topo da area de chat da GUI PySide6.
- `citybot_logo.png`, imagem PNG de 1600 x 1600 em RGBA.
- `citybot_logo.svg`, versao vetorial do logo.
- `logo.png`, imagem PNG de 2816 x 1536 em modo de paleta.

Fato: o antigo `logo.png` na raiz nao apareceu na lista atual de arquivos do projeto.

Inferencia: os logos foram reorganizados para uma pasta de assets dentro de `src`, provavelmente para deixar a raiz mais limpa e aproximar recursos visuais do codigo da aplicacao.

Opiniao tecnica: a GUI deve resolver o caminho do logo a partir da raiz real do projeto, e nao depender do diretorio atual de execucao. Isso evita falha quando o app for aberto por outro working directory.

Fato: `testes/` contem arquivos como `citybot.py`, `citybot_2.py`, `citybot copy.py`, `gui.py` e `gui_3.py`.

Inferencia: a pasta `testes/` funciona como historico de experimentos e scripts legados, nao como testes automatizados. Isso e reforcado pelo fato de estar ignorada no `.gitignore`.

Fato: o arquivo residual `tempCodeRunnerFile.py`, que continha Python invalido, foi salvo em `Backup/27_06_2026`, removido do codigo versionado e adicionado ao `.gitignore`.

## 4. Arquivos versionados e arquivos locais

Fato: o `.gitignore` ignora itens importantes para seguranca e ambiente local:

- `.env`.
- `venv/`.
- `.venv`.
- `citybot.db`.
- `testes/`.
- `tempCodeRunnerFile.py`.
- `textos`.
- `Backup`.
- arquivos de cache Python.

Opiniao tecnica: ignorar `.env`, banco local, backups e ambiente virtual e correto. Isso reduz risco de vazar chave de API, conversas privadas ou arquivos gerados pelo usuario.

Risco real: embora `.env` esteja ignorado, arquivos de texto gerados por OCR e conversas salvas em SQLite podem conter dados sensiveis. O projeto deve tratar esses arquivos como privados.

## 5. Objetivo funcional do CityBot

Fato: pelo `README.md` e pelo codigo, o CityBot suporta os fluxos abaixo:

- Chat livre com LLM.
- Perguntas sobre conteudo de site.
- Perguntas sobre transcricao de video do YouTube.
- Perguntas sobre conteudo de PDF.
- OCR de imagem.
- Historico persistido em SQLite.
- Uso por GUI PySide6 ou CLI.

Inferencia: o publico-alvo inicial parece ser o proprio desenvolvedor ou usuarios internos que precisam consultar conteudo de forma rapida, em vez de um produto SaaS multiusuario.

Opiniao tecnica: o projeto esta mais proximo de um assistente desktop pessoal do que de uma aplicacao web ou servico em producao. Isso muda as prioridades tecnicas: primeiro vem confiabilidade local, privacidade e ergonomia; depois escalabilidade multiusuario.

## 6. Como executar

Fato: o ponto de entrada e `main.py`.

Comandos documentados pelo projeto:

```powershell
python main.py
python main.py --provider azure_openai
python main.py --mode cli
python main.py --provider azure_openai --mode cli
```

Fato: valores padrao em `main.py`:

- `--provider` default: `azure_openai`.
- `--mode` default: `gui`.

Fato: `main.py` usa `argparse` e aceita somente:

- Provider: `gemini`, `azure_openai`.
- Mode: `gui`, `cli`.

Opiniao tecnica: esse ponto de entrada e simples e bom para uso local. Para producao ou distribuicao, valeria separar configuracao de ambiente, logs e validacao de dependencias antes de abrir a GUI.

## 7. Variaveis de ambiente

Fato: o codigo espera as seguintes variaveis:

```text
GEMINI_API_KEY
GEMINI_MODEL
AZURE_OPENAI_API_KEY
AZURE_ENDPOINT
AZURE_API_VERSION
AZURE_DEPLOYMENT
AZURE_MAX_OUTPUT_TOKENS
CITYBOT_YOUTUBE_COOKIES_BROWSER
CITYBOT_YOUTUBE_COOKIES_PROFILE
CITYBOT_YOUTUBE_COOKIES_FILE
CITYBOT_WHISPER_ENGINE
CITYBOT_WHISPER_MODEL
CITYBOT_WHISPER_DEVICE
CITYBOT_WHISPER_COMPUTE_TYPE
CITYBOT_WHISPER_LANGUAGE
CITYBOT_WHISPER_BATCH_SIZE
CITYBOT_WHISPERX_ALIGN
CITYBOT_WHISPER_MAX_AUDIO_SECONDS
CITYBOT_IMAGE_MODEL
CITYBOT_IMAGE_BASE_URL
CITYBOT_IMAGE_API_KEY
CITYBOT_IMAGE_AZURE_SCOPE
OPENAI_API_KEY
```

Fato: `CityBotGemini` le explicitamente `GEMINI_API_KEY` e `GEMINI_MODEL`.

Fato: `CityBotAzureOpenAI` le explicitamente `AZURE_OPENAI_API_KEY`, `AZURE_ENDPOINT`, `AZURE_API_VERSION`, `AZURE_DEPLOYMENT` e opcionalmente `AZURE_MAX_OUTPUT_TOKENS`.

Fato: `CITYBOT_YOUTUBE_COOKIES_BROWSER`, `CITYBOT_YOUTUBE_COOKIES_PROFILE` e `CITYBOT_YOUTUBE_COOKIES_FILE` sao opcionais. Quando definidos, o fallback de video via `yt-dlp` tenta usar cookies para reduzir bloqueios do YouTube em transcricoes anonimas.

Fato: `CITYBOT_YOUTUBE_COOKIES_FILE` tem prioridade sobre `CITYBOT_YOUTUBE_COOKIES_BROWSER`, porque evita acessar diretamente o banco de cookies vivo do Chrome/Edge.

Fato: `CITYBOT_WHISPER_ENGINE`, `CITYBOT_WHISPER_MODEL`, `CITYBOT_WHISPER_DEVICE`, `CITYBOT_WHISPER_COMPUTE_TYPE`, `CITYBOT_WHISPER_LANGUAGE`, `CITYBOT_WHISPER_BATCH_SIZE`, `CITYBOT_WHISPERX_ALIGN` e `CITYBOT_WHISPER_MAX_AUDIO_SECONDS` sao opcionais e controlam o fallback local de transcricao de audio.

Fato: `CITYBOT_WHISPER_ENGINE=auto` e o padrao. Nesse modo, o CityBot tenta WhisperX primeiro quando o pacote opcional esta instalado; se nao estiver, continua usando `faster-whisper`. Tambem e possivel forcar `whisperx` ou `faster-whisper`.

Fato: `CITYBOT_IMAGE_MODEL` e opcional e usa `gpt-image-2` por padrao para geracao de imagens.

Fato: `CITYBOT_IMAGE_BASE_URL` e opcional. Quando configurado, a geracao de imagens usa o SDK `OpenAI` apontando para esse `base_url`. Se `CITYBOT_IMAGE_API_KEY` tambem estiver configurado, essa chave e usada no endpoint. Sem `CITYBOT_IMAGE_API_KEY`, o app autentica com `DefaultAzureCredential` via `azure-identity`. `CITYBOT_IMAGE_AZURE_SCOPE` permite trocar o escopo, com padrao `https://ai.azure.com/.default`.

Fato: quando `CITYBOT_IMAGE_BASE_URL` nao esta configurado, a geracao de imagens usa `OPENAI_API_KEY` diretamente com a API OpenAI.

Fato: Gemini e Azure OpenAI validam variaveis obrigatorias no construtor, guardam `config_error` e retornam erro claro em `resposta_bot` quando a configuracao esta incompleta.

Risco residual:

- A presenca das variaveis nao garante que chaves, deployments ou modelos estejam validos nos provedores externos.
- A validacao evita erro confuso por variavel ausente, mas nao substitui testes reais de conectividade.

## 8. Dependencias

Fato: `requirements.txt` lista dependencias diretas usadas pelo codigo ativo e por scripts legados.

Dependencias principais:

- `python-dotenv`: carrega `.env`.
- `google-genai`: SDK do Gemini.
- `openai`: SDK usado pelo provider Azure OpenAI com `AzureOpenAI`.
- `requests`: leitura de paginas web.
- `beautifulsoup4`: parse HTML.
- `youtube-transcript-api`: transcricao do YouTube.
- `yt-dlp`: fallback para metadados e URLs de legendas do YouTube.
- `faster-whisper`: fallback local para transcricao de audio quando transcricao e legendas do YouTube falham.
- `whisperx`: dependencia opcional em `requirements-whisperx.txt`, usada como primeiro motor local quando instalada e `CITYBOT_WHISPER_ENGINE=auto`.
- `truststore`: validacao HTTPS usando certificados confiaveis do sistema operacional.
- `pypdf`: leitura de PDF.
- `opencv-python`: pre-processamento de imagem para OCR Tesseract.
- `pytesseract`: OCR local.
- `langdetect`: deteccao de idioma para OCR.
- `python-docx`: escrita de `.docx`.
- `pyperclip`: leitura/limpeza da area de transferencia no CLI.
- `pillow`: imagens na GUI e OCR Gemini.
- `PySide6`: interface grafica desktop baseada em Qt.
- `azure-identity`: autenticacao Azure AD para gerar imagens via Azure AI Foundry quando `CITYBOT_IMAGE_BASE_URL` estiver configurado.

Fato: `PySide6==6.11.1` foi adicionado ao `requirements.txt` em 13/07/2026. `tkinter` permanece apenas em `src/gui/markdown_renderer.py`, arquivo legado que nao e mais usado pela GUI ativa.

Fato: `yt-dlp==2026.7.4` foi adicionado ao `requirements.txt` em 13/07/2026 como fallback para extracao de legendas do YouTube.

Fato: `faster-whisper==1.2.1` foi adicionado ao `requirements.txt` em 13/07/2026 como fallback local de transcricao de audio para videos do YouTube.

Fato: `requirements-whisperx.txt` foi adicionado em 17/07/2026 para instalar `whisperx==3.8.6` de forma opcional.

Fato: `azure-identity>=1.17.1` foi adicionado em 22/07/2026 para suportar o fluxo opcional de geracao de imagens via Azure AI Foundry com `DefaultAzureCredential`.

Fato: em 17/07/2026, o provider Groq e as dependencias `langchain`, `langchain-groq` e `langchain-community` foram removidos porque conflitam com `whisperx==3.8.6`, que exige `numpy>=2.1.0`.

Fato: ambientes virtuais criados antes dessa remocao podem manter pacotes Groq/LangChain instalados. Para limpar o ambiente local, use `python -m pip uninstall -y langchain langchain-groq langchain-community groq` antes de instalar o WhisperX opcional.

Fato: o Tesseract OCR e dependencia externa do sistema, nao apenas pacote Python.

Opiniao tecnica: para reduzir risco de ambiente quebrado, seria bom incluir uma rotina de diagnostico que verifique:

- Versao do Python.
- Presenca do Tesseract no PATH.
- Chaves e modelos configurados.
- Acesso ao banco SQLite.
- Importacao das dependencias principais.

## 9. Arquitetura geral

Fato: a arquitetura atual pode ser entendida em quatro camadas:

```text
main.py
  ├── seleciona provider e modo
  ├── GUI PySide6
  │   ├── src/gui/app_pyside.py
  │   ├── src/gui/app_gemini.py
  │   └── src/gui/app_azure_openai.py
  ├── Core de IA e persistencia
  │   ├── src/core/bot_gemini.py
  │   ├── src/core/bot_azure_openai.py
  │   └── src/core/database.py
  └── Utilitarios de entrada/saida
      ├── src/utils/scrapers.py
      ├── src/utils/pdf_reader.py
      ├── src/utils/ocr.py
      └── src/utils/file_writer.py
```

Inferencia: `main.py` foi desenhado para ser um roteador simples, mantendo detalhes de GUI e LLM fora do ponto de entrada.

Opiniao tecnica: a separacao `core`, `gui` e `utils` e boa. A duplicacao visual principal foi reduzida em 13/07/2026 com `app_pyside.py`, que concentra a interface grafica e recebe a factory do bot.

Melhor caminho tecnico:

- Manter a GUI unica recebendo uma instancia de bot ou uma factory de bot.
- Manter `CityBotGemini` e `CityBotAzureOpenAI` como adaptadores de provider.
- Definir uma interface comum de bot, por exemplo `resposta_bot`, `carrega_site`, `carrega_video`, `carrega_pdf`, `carrega_imagem_ocr`, `save_conversation`.

Trade-off:

- Complexidade: baixa a media.
- Custo de implementacao: moderado, porque exige mexer em GUI e inicializacao.
- Manutencao: melhora bastante, pois bugs visuais seriam corrigidos uma vez.
- Risco: medio, porque GUI desktop com threads exige cuidado para atualizar a interface somente pela thread principal.

## 10. `main.py`

Fato: `main.py` importa `argparse`, `sys` e `os`.

Fato: adiciona a raiz do projeto ao `sys.path`:

```python
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
```

Fato: desde 13/07/2026, `run_gui(provider)`:

- Cria ou reutiliza um `QApplication`.
- Seleciona a factory do bot conforme o provider.
- Instancia `src.gui.app_pyside.ModernCityBotGUI`.
- Exibe a janela e retorna `app.exec()`.

Fato: `run_cli(provider)`:

- Instancia `CityBotGemini` ou `CityBotAzureOpenAI`.
- Chama `bot.menu()`.

Opiniao tecnica: o uso de import dentro das funcoes reduz carregamento desnecessario do provider nao escolhido. Isso e util quando uma dependencia ou chave de API pode estar ausente. Por outro lado, erros de import aparecem somente em tempo de execucao.

Opiniao tecnica: se o projeto crescer, seria melhor transformar `src` em pacote Python instalavel, com `pyproject.toml`, e evitar manipular `sys.path`.

## 11. Banco de dados

Arquivo: `src/core/database.py`.

Fato: o projeto usa SQLite via `sqlite3`.

Fato: a classe principal e `CityBotDatabase`.

Fato: o construtor abre conexao com:

```python
sqlite3.connect(db_path, check_same_thread=False)
```

Fato: o caminho padrao do banco e resolvido pela raiz do projeto:

```text
PROJECT_ROOT/citybot.db
```

Fato: `src/utils/paths.py` define `PROJECT_ROOT` a partir da localizacao do pacote `src`, e `CityBotDatabase` usa esse caminho por padrao. Caminhos relativos customizados tambem sao resolvidos a partir da raiz do projeto. O valor especial `:memory:` continua preservado para testes SQLite em memoria.

Fato: as tabelas criadas sao:

```sql
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    name TEXT,
    preferences TEXT
);
```

```sql
CREATE TABLE IF NOT EXISTS conversations (
    id INTEGER PRIMARY KEY,
    user_message TEXT,
    assistant_response TEXT
);
```

```sql
CREATE TABLE IF NOT EXISTS contexts (
    id INTEGER PRIMARY KEY,
    source_type TEXT NOT NULL,
    source_ref TEXT,
    display_name TEXT NOT NULL,
    content TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
```

Fato: metodos disponiveis:

- `create_table()`.
- `save_user(name, preferences)`.
- `load_user(name)`.
- `save_conversation(user_message, assistant_response)`.
- `load_conversations()`.
- `save_context(source_type, source_ref, display_name, content)`.
- `load_contexts(limit=50)`.
- `load_context(context_id)`.
- `limpar_conversas()`.
- `limpar_banco()`.

Fato: `limpar_conversas()` apaga somente o historico de conversas e preserva contextos salvos. `limpar_banco()` executa `DELETE` nas tabelas `conversations`, `users` e `contexts`. Ambos preservam o schema para novas gravacoes.

Risco real:

- `check_same_thread=False` permite usar a conexao em threads diferentes, mas nao torna o acesso automaticamente seguro. Em GUI com threads, pode haver risco de concorrencia se varias operacoes acessarem o banco ao mesmo tempo.
- Nao ha timestamps em `conversations`, entao fica dificil auditar ordem real, periodo, duracao, volume e comportamento de uso.
- Nao ha `user_id` em `conversations`, entao a tabela de usuarios ainda nao se conecta ao historico.

Opiniao tecnica: para uso pessoal, o schema e suficiente. Para uso profissional, o minimo recomendado seria adicionar:

- `created_at`.
- `provider`.
- `model`.
- `source_type`, como `chat`, `site`, `video`, `pdf`, `ocr`.
- `source_ref`, como URL, caminho de arquivo ou nome do documento.
- `user_id` opcional.
- `metadata` em JSON para diagnostico.

Impacto pratico: com esses campos, seria possivel medir custo, uso por fonte, qualidade das respostas, erros frequentes e dados necessarios para melhoria do produto.

## 12. Provider Gemini

Arquivo: `src/core/bot_gemini.py`.

Fato: a classe principal e `CityBotGemini`.

Fato: no construtor:

- Chama `load_dotenv()`.
- Le `GEMINI_API_KEY`.
- Le `GEMINI_MODEL`.
- Valida variaveis obrigatorias em `config_error`.
- Cria `genai.Client(api_key=self.api_key)` somente se a configuracao estiver completa.
- Cria instancia de `CityBotDatabase`.

Fato: metodos de carregamento delegam para utilitarios:

- `carrega_site(url)` chama `src.utils.scrapers.carrega_site`.
- `carrega_video(url)` chama `src.utils.scrapers.carrega_video`.
- `carrega_pdf(path)` chama `src.utils.pdf_reader.carrega_pdf`.
- `carrega_imagem_ocr(path, nome)` chama `src.utils.ocr.carrega_imagem_ocr_gemini`.

Fato: o parametro `nome` em `carrega_imagem_ocr(path, nome)` nao e usado na implementacao Gemini atual.

Fato: `resposta_bot(mensagens, documento='')` monta uma instrucao de sistema com o contexto do documento e usa:

```python
types.GenerateContentConfig(
    system_instruction=instrucao_sistema,
    temperature=0.7
)
```

Fato: o historico e formatado com roles:

- `user` para mensagens `user` ou `human`.
- `model` para demais tipos.

Fato: a ultima mensagem e enviada com `chat.send_message(ultima_mensagem)`.

Fato: se houver excecao na API, retorna texto no formato:

```text
Erro na API do Gemini: ...
```

Fato: se `GEMINI_API_KEY` ou `GEMINI_MODEL` estiverem ausentes, `resposta_bot` retorna texto no formato:

```text
Erro de configuracao Gemini: ...
```

Opiniao tecnica: retornar erro como texto para o usuario e simples, mas mistura resposta de assistente com falha tecnica. Para producao, seria melhor retornar um objeto ou excecao tratada pela camada de interface, permitindo log tecnico e mensagem amigavel separada.

Risco real:

- Nao ha timeout ou politica de retry configurada no nivel do app.
- O contexto completo do documento e inserido diretamente na instrucao do sistema, sem chunking, sumarizacao ou controle de tamanho.
- Se o documento for grande, pode haver alto custo, lentidao ou erro por limite de contexto.

## 13. Provider Azure OpenAI

Arquivo: `src/core/bot_azure_openai.py`.

Fato: em 03/06/2026, foi adicionada a classe `CityBotAzureOpenAI`.

Fato: o provider usa `AzureOpenAI` do pacote `openai`, seguindo o exemplo fornecido pelo usuario:

```python
client.responses.create(
    model=os.getenv('AZURE_DEPLOYMENT'),
    input='...',
    max_output_tokens=self.max_output_tokens,
)
```

Fato: variaveis esperadas:

- `AZURE_OPENAI_API_KEY`.
- `AZURE_ENDPOINT`.
- `AZURE_API_VERSION`.
- `AZURE_DEPLOYMENT`.
- `AZURE_MAX_OUTPUT_TOKENS`, opcional, com padrao `1200`.

Fato: `CityBotAzureOpenAI` valida configuracao antes de criar o cliente. Se faltar variavel obrigatoria, ele guarda `config_error`, nao instancia `AzureOpenAI` e retorna erro claro em `resposta_bot`.

Fato: antes da recriacao do ambiente em 27/06/2026, o Python global tinha `openai 1.59.5`, que nao expunha `client.responses`. O novo `venv` instalou `openai 2.44.0`, e a disponibilidade da Responses API foi validada. O `requirements.txt` exige `openai>=1.68.0`.

Fato: `CityBotAzureOpenAI` tambem valida se o cliente criado possui `responses`. Se a versao instalada do pacote nao suportar `client.responses.create`, o provider retorna mensagem pedindo `pip install -r requirements.txt`.

Fato: em 08/06/2026, o padrao de `AZURE_MAX_OUTPUT_TOKENS` foi aumentado de `300` para `1200`, porque `300` corta respostas medias de resumo, analise e listas.

Fato: `CityBotAzureOpenAI` passou a verificar `response.status` e `response.incomplete_details.reason`. Se a API retornar resposta incompleta por `max_output_tokens`, o texto exibido inclui um aviso pedindo para aumentar `AZURE_MAX_OUTPUT_TOKENS`.

Fato: o prompt enviado ao Azure OpenAI e uma string unica, montada por `_monta_prompt`, contendo instrucao do CityBot, contexto carregado e historico da conversa.

Inferencia: a escolha por `input` textual foi feita para ficar alinhada ao exemplo recebido e reduzir risco de incompatibilidade com formatos mais complexos da Responses API.

Fato: o OCR no provider Azure OpenAI usa Tesseract local e salva o texto via `salvar_texto`. Imagens nao sao enviadas ao Azure OpenAI nessa implementacao.

Opiniao tecnica: essa decisao e conservadora e boa para privacidade, porque o exemplo recebido cobre texto, nao imagem. Caso seja desejado OCR multimodal via Azure no futuro, isso deve ser tratado como nova decisao de produto por envolver custo, privacidade e suporte do deployment.

Trade-offs:

- Complexidade: baixa, porque segue o mesmo contrato dos outros bots.
- Custo de implementacao: baixo a medio, por reaproveitar utilitarios existentes.
- Manutencao: boa, pois a GUI Azure reaproveita a base visual unica em `app_pyside.py`.
- Escalabilidade: ainda limitada por prompt textual completo, sem chunking ou recuperacao.
- Risco: depende da versao do pacote `openai` suportar `client.responses.create` com Azure OpenAI.

## 14. Utilitario de scraping

Arquivo: `src/utils/scrapers.py`.

Fato: `carrega_site(url_site)`:

- Usa `requests.get` com `User-Agent` e timeout de 15 segundos.
- Chama `response.raise_for_status()`.
- Usa BeautifulSoup com parser `html.parser`.
- Remove tags `script` e `style`.
- Extrai texto com `soup.get_text(separator=' ')`.
- Limpa linhas e chunks vazios.
- Retorna texto unido por quebra de linha.

Fato: se ocorrer erro, registra a falha com `logging` e retorna string vazia.

Fato: `carrega_video(url_video)`:

- Extrai `video_id` de URLs `watch`, `youtu.be`, `shorts`, `embed` e `live`.
- Tenta primeiro `YouTubeTranscriptApi().fetch(video_id, languages=['pt', 'pt-BR', 'en'])`, compativel com a versao `1.2.4` fixada.
- Se a transcricao direta falhar ou vier vazia, usa `yt-dlp` para buscar metadados do video e selecionar legendas oficiais ou automaticas.
- O fallback via `yt-dlp` prioriza legendas em portugues e ingles, baixa somente o arquivo de legenda pela propria camada de rede do `yt-dlp` e extrai texto de formatos como `json3`, `vtt`, `srv3` e `ttml`.
- Se transcricao e legendas falharem, baixa temporariamente apenas o audio com `yt-dlp` e transcreve localmente com WhisperX opcional ou `faster-whisper`.
- O fallback de audio usa `CITYBOT_WHISPER_ENGINE=auto`, `CITYBOT_WHISPER_MODEL=base`, `CITYBOT_WHISPER_DEVICE=cpu`, `CITYBOT_WHISPER_COMPUTE_TYPE=int8`, `CITYBOT_WHISPER_BATCH_SIZE=8` e limite de 7200 segundos por padrao; transmissoes ainda ao vivo sao recusadas ate terminarem.
- Quando `CITYBOT_WHISPER_ENGINE=auto`, o WhisperX e tentado primeiro se estiver instalado; se nao estiver disponivel ou falhar, `faster-whisper` continua funcionando como fallback.
- `CITYBOT_WHISPERX_ALIGN=true` ativa alinhamento no WhisperX, mas pode baixar modelos extras e aumentar o tempo de processamento.
- Quando o YouTube retorna `HTTP 429 Too Many Requests`, a GUI exibe uma mensagem especifica sugerindo configurar `CITYBOT_YOUTUBE_COOKIES_BROWSER`; se o fallback local tambem nao conseguir baixar o audio, a mensagem informa essa falha adicional.
- Quando o `yt-dlp` nao consegue copiar ou descriptografar cookies do Chrome/Edge, o fallback tenta novamente sem cookies do navegador; se a requisicao anonima tambem falhar, a GUI exibe uma mensagem especifica sugerindo fechar o navegador ou usar `CITYBOT_YOUTUBE_COOKIES_FILE`.
- Quando `CITYBOT_YOUTUBE_COOKIES_FILE` aponta para arquivo fora do formato Netscape cookies.txt, a GUI exibe uma mensagem especifica explicando que JSON, HTML ou SQLite nao funcionam.
- Usa `truststore` para validar HTTPS com o repositorio de certificados do sistema operacional.
- Concatena textos da transcricao.

Risco real em sites:

- Nao ha limite de tamanho de HTML.
- Nao ha validacao de URL.
- Nao ha protecao contra acessar enderecos internos ou locais, caso isso seja usado em ambiente corporativo.
- Conteudo renderizado por JavaScript pode nao ser capturado.

Risco real em YouTube:

- Videos sem transcricao ou legenda disponivel em idiomas suportados continuam sem conteudo.
- Transcricoes podem estar indisponiveis por configuracao do video.
- O YouTube muda com frequencia; `yt-dlp` pode exigir atualizacao caso a extracao de metadados quebre.
- Usar cookies do navegador melhora alguns casos de bloqueio, mas depende do estado local do navegador e pode falhar se o perfil estiver bloqueado, deslogado ou indisponivel.
- Em Windows, Chrome/Edge podem bloquear o arquivo `Network/Cookies` enquanto estao abertos. Nesses casos, fechar totalmente o navegador ou usar um arquivo `cookies.txt` exportado e mais robusto.
- Arquivos de cookies exportados sao sensiveis e ficam ignorados pelo Git por padroes como `cookies.txt`, `youtube_cookies.txt`, `*_cookies.txt` e `*.cookies.txt`.
- O primeiro uso de `faster-whisper` ou WhisperX pode baixar modelos pelo Hugging Face Hub e demorar. Sem internet ou cache local de modelo, esse fallback pode falhar.
- Transcricao local de audio e mais lenta e consome mais CPU/RAM do que usar legenda pronta.

Opiniao tecnica: para uso pessoal, a abordagem e simples e adequada. Para ambiente real, validacao de URL, limites de tamanho e protecao contra enderecos internos ainda trariam ganho de seguranca.

Fato: em 27/06/2026, a leitura de videos falhava primeiro por certificado HTTPS nao reconhecido pelo `certifi` e, depois da correcao SSL, pela incompatibilidade do parser `youtube-transcript-api 0.6.3` com a resposta atual do YouTube. Com `truststore 0.10.4` e `youtube-transcript-api 1.2.4`, um video publico retornou 61 trechos de transcricao.

## 15. Utilitario de PDF

Arquivo: `src/utils/pdf_reader.py`.

Fato: `carrega_pdf(caminho)`:

- Verifica se o caminho existe com `os.path.exists`.
- Usa `PdfReader(caminho)`.
- Itera por `reader.pages`.
- Trata `page.extract_text() is None` como texto vazio.
- Une as paginas com quebra de linha.
- Em erro, registra mensagem com `logging` e retorna string vazia.

Risco real:

- PDFs escaneados sem camada de texto nao serao lidos por `pypdf`.
- PDFs grandes podem gerar contexto grande demais para o modelo.
- Nao ha contagem de paginas, tamanho de arquivo ou estrategia de chunking.

Opiniao tecnica: o utilitario e bom para PDFs simples com texto embutido. Para documentos reais, especialmente contratos, relatorios e PDFs escaneados, seria melhor:

- Tratar `None` como string vazia.
- Registrar paginas sem texto.
- Limitar tamanho.
- Opcionalmente usar OCR por pagina quando necessario.
- Dividir texto em chunks e recuperar trechos relevantes antes de chamar o LLM.

Impacto pratico: isso reduz custo de API, melhora qualidade das respostas e evita falhas em documentos grandes ou digitalizados.

## 16. Utilitario de OCR

Arquivo: `src/utils/ocr.py`.

Fato: existem duas funcoes:

- `carrega_imagem_ocr_tesseract(caminho)`.
- `carrega_imagem_ocr_gemini(caminho, client, model_name)`.

### 16.1 OCR com Tesseract

Fato: o fluxo Tesseract:

- Verifica existencia do arquivo.
- Le imagem com `cv2.imread`.
- Converte para escala de cinza.
- Aplica threshold binario com Otsu.
- Executa OCR bruto com `pytesseract.image_to_string(..., config='--psm 6')`.
- Detecta idioma com `langdetect.detect`.
- Mapeia idioma para codigos do Tesseract.
- Executa OCR novamente com idioma escolhido.

Fato: idiomas mapeados incluem portugues, ingles, espanhol, frances, alemao, italiano, russo, japones, chines simplificado, chines tradicional, coreano, arabe, holandes, polones, turco, dinamarques, finlandes, sueco e noruegues.

Fato: se a deteccao falhar, usa portugues como padrao.

Fato: em 27/06/2026, o Tesseract local disponibilizava os idiomas `eng`, `osd` e `por`.

Risco real:

- Se `cv2.imread` retornar `None`, `cv2.cvtColor` falha. O erro e capturado, mas a mensagem nao explica que a imagem nao foi carregada corretamente.
- A deteccao de idioma com pouco texto pode ser instavel.
- O Tesseract precisa estar instalado no sistema, nao basta instalar `pytesseract`.
- Nem todos os pacotes de idioma do Tesseract podem estar instalados.

Opiniao tecnica: a estrategia de pre-processamento e simples e boa como primeira versao. Para OCR mais robusto, valeria permitir parametros por tipo de imagem, como documento, cupom, print, tabela ou foto.

### 16.2 OCR com Gemini

Fato: o fluxo Gemini:

- Verifica existencia da imagem.
- Abre a imagem com `PIL.Image.open`.
- Envia imagem mais prompt ao Gemini.
- Pede para extrair e transcrever texto visivel, mantendo formatacao quando possivel.
- Se nao houver texto, pede descricao do conteudo da imagem.

Risco real:

- Enviar imagem para API externa pode expor dados sensiveis se a imagem tiver documento, rosto, endereco, dados financeiros ou informacoes corporativas.
- Nao ha aviso explicito ao usuario antes de enviar a imagem.
- Nao ha controle de tamanho do arquivo.

Opiniao tecnica: Gemini OCR tende a ser mais flexivel para imagens complexas, mas Tesseract e melhor quando privacidade local e prioridade. A escolha ideal depende do caso:

- Tesseract: menor custo e mais privacidade, mas pode ter qualidade pior.
- Gemini: melhor interpretacao e formatacao, mas com custo, dependencia de internet e risco de privacidade.

## 17. Escrita de arquivos OCR

Arquivo: `src/utils/file_writer.py`.

Fato: `salvar_texto(texto, nome)`:

- Cria pasta `PROJECT_ROOT/textos` se nao existir.
- Cria documento Word com `python-docx`.
- Normaliza o nome para um basename seguro.
- Remove extensoes `.docx` e `.txt` informadas pelo usuario para evitar duplicacao.
- Salva `PROJECT_ROOT/textos/{nome_seguro}.docx`.
- Salva `PROJECT_ROOT/textos/{nome_seguro}.txt`.
- Retorna o texto original.

Fato: desde 13/07/2026, a pasta de saida de OCR nao depende mais do diretorio atual de execucao. Ela usa `TEXTOS_DIR = project_path('textos')`.

Fato: em caso de erro de escrita, registra a falha com `logging` e retorna string vazia.

Risco real:

- Pode haver sobrescrita silenciosa se o mesmo nome for usado novamente.
- Nao ha timestamp, UUID ou confirmacao de substituicao.

Opiniao tecnica: o risco de path traversal foi corrigido. Para evitar perda por sobrescrita, ainda pode ser util adicionar confirmacao ou timestamp.

Impacto pratico: isso evita perda de documentos OCR e reduz risco de gravar arquivo fora da pasta esperada.

## 18. Interface grafica PySide6

Arquivos:

- `src/gui/app_pyside.py`.
- `src/gui/app_gemini.py`.
- `src/gui/app_azure_openai.py`.
- `src/gui/markdown_renderer.py`, legado Tkinter nao usado pela GUI ativa.

Fato: os wrappers GUI de Gemini e Azure OpenAI expõem uma classe chamada `ModernCityBotGUI`.

Fato: desde 13/07/2026, `src/gui/app_pyside.py` concentra a base visual em PySide6. `src/gui/app_gemini.py` e `src/gui/app_azure_openai.py` sao wrappers que injetam, respectivamente, `CityBotGemini` e `CityBotAzureOpenAI`.

Fato: os wrappers de provider resolvem a raiz do projeto e adicionam esse caminho ao `sys.path` antes dos imports `src.*`. Isso permite executar diretamente arquivos como `src/gui/app_azure_openai.py` por caminho absoluto, alem de executar pelo `main.py`.

Fato: a GUI usa:

- Tema escuro via Qt stylesheet.
- Sidebar com fontes de dados.
- Area de chat com bolhas.
- Entrada de texto com `QTextEdit`.
- Barra de status.
- Logo carregado de `src/figures/citybot_logo.png`.
- Banner minimalista carregado de `src/figures/citybot_banner_minimal.png` no topo da area de chat.
- Dialogo de geracao de imagens com prompt, tamanho, qualidade e formato.
- Threads para chamadas demoradas.

Fato: em 13/07/2026, a interface ativa foi migrada de Tkinter/ttk para PySide6. A implementacao usa `QMainWindow`, `QFrame`, `QPushButton`, `QLabel`, `QTextEdit`, `QTextBrowser`, `QScrollArea`, `QFileDialog`, `QInputDialog` e `QMessageBox`.

Fato: em 22/07/2026, a GUI passou a abrir maximizada tanto pelo `main.py` quanto pelos wrappers diretos de provider.

Fato: em 22/07/2026, a GUI passou a exibir um banner minimalista fixo acima da conversa. O banner e renderizado por um widget proprio com recorte responsivo, sem entrar no historico de mensagens.

Fato: em 22/07/2026, a GUI passou a gerar imagens com `gpt-image-2`, exibindo um preview na conversa e salvando o arquivo em `PROJECT_ROOT/imagens/`.

Fato: as bolhas de mensagem usam `QTextBrowser.setMarkdown()` para renderizar Markdown basico e abrir links externos.

Fato: em 13/07/2026, as bolhas de resposta passaram a calcular largura pela area disponivel do chat e altura pelo tamanho total do conteudo, sem rolagem interna. Respostas longas ficam mais largas e aparecem completas dentro da bolha, usando a rolagem geral da conversa quando necessario.

Fato: em 13/07/2026, os dialogos Qt passaram a receber estilos explicitos de fundo, texto, campos e botoes para evitar texto invisivel em caixas como a confirmacao de limpar conversa.

Fato: `src/gui/markdown_renderer.py` permanece no projeto como legado da interface Tkinter anterior. Ele nao e importado pela GUI PySide6 ativa.

Fato: em 03/06/2026, `conversation_history` na GUI foi corrigido para armazenar tuplas com papel da mensagem:

```python
("user", user_message)
("assistant", response)
```

Impacto pratico: a GUI passou a usar uma biblioteca desktop mais robusta que Tkinter, com melhor base para layout, estilo, dialogos e evolucao visual.

Trade-offs da solucao com PySide6:

- Complexidade: media, porque Qt tem mais conceitos do que Tkinter.
- Custo de instalacao: maior, pois `PySide6` e uma dependencia grande.
- Manutencao: melhor, pois a GUI ativa e unica e os providers sao wrappers pequenos.
- Escalabilidade visual: melhor para evoluir a interface desktop.
- Performance: boa para mensagens comuns; respostas extremamente longas ainda podem gerar bolhas altas.

Fato: opcoes de fonte na sidebar:

- Chat Livre.
- Carregar Site.
- Carregar Video.
- Carregar PDF.
- OCR Imagem.
- Gerar Imagem.
- Baixar Texto OCR apos carregar uma imagem com OCR.
- Barra de progresso no rodape da GUI durante download de audio do YouTube para fallback local.
- Conteudos extraidos podem carregar metadado `source_title`; a GUI usa esse titulo no contexto atual e no card de carregamento quando disponivel, evitando mostrar apenas a URL do video.
- Contextos carregados de site, video, PDF e OCR sao salvos na tabela `contexts`.
- Ao entrar em chat livre, carregar outra fonte ou restaurar um contexto salvo, a GUI limpa somente a sessao visivel e o `conversation_history` em memoria. O banco de conversas e os contextos salvos sao preservados.
- A sidebar possui botao para selecionar contextos salvos e reativar o conteudo como contexto atual.
- Limpar Conversa.

Fato: a GUI usa `threading.Thread(..., daemon=True)` para processar mensagens e carregamentos externos.

Fato: atualizacoes de interface vindas de threads sao encaminhadas por sinais Qt (`WorkerSignals.finished` e `WorkerSignals.failed`), evitando atualizacao direta da UI pela thread de trabalho.

Risco real:

- O Markdown agora depende do suporte de Markdown do Qt em `QTextBrowser`, que cobre casos comuns, mas nao substitui um renderer completo de HTML/CommonMark.

Risco residual:

- A base visual agora e compartilhada entre Gemini e Azure OpenAI; isso reduz duplicacao, mas faz qualquer regressao em `app_pyside.py` afetar os dois providers ao mesmo tempo.

Fato: apos confirmacao do usuario, `clear_chat()` apaga somente as conversas persistidas, limpa a tela, o historico em memoria e o contexto carregado. Perfis de usuario sao preservados. A limpeza e bloqueada enquanto uma resposta esta em processamento.

Fato: ao iniciar, as GUIs Gemini e Azure restauram o historico salvo com roles `user` e `assistant`.

Impacto pratico: o comportamento visual agora corresponde ao estado persistido e o botao nao deixa conversas antigas no banco.

## 19. Interface CLI

Arquivos:

- `src/core/bot_gemini.py`.
- `src/core/bot_azure_openai.py`.

Fato: os providers Gemini e Azure OpenAI possuem metodo `menu()`.

Fato: o menu CLI oferece:

```text
1. Bora conversar?
2. Informações sobre um site
3. Informações sobre um vídeo do YouTube
4. Informações sobre um PDF
5. OCR imagem
6. Sair
```

Fato: a CLI usa `pyperclip.copy('')` para limpar a area de transferencia ao iniciar.

Fato: a versao Gemini detecta texto na area de transferencia e oferece uso do conteudo colado.

Risco real:

- Ler automaticamente area de transferencia pode gerar comportamento inesperado se houver senha, token, documento sensivel ou texto grande copiado.
- Nao ha confirmacao explicita de uso de dados da area de transferencia em todos os caminhos.

Opiniao tecnica: para uso pessoal e pratico, isso pode ser conveniente. Para uso profissional, melhor pedir confirmacao clara antes de usar conteudo do clipboard.

## 20. Fluxos de dados

### 20.1 Chat livre

Fato:

```text
Usuario -> GUI/CLI -> CityBotGemini ou CityBotAzureOpenAI -> API LLM -> resposta -> SQLite
```

Riscos:

- Historico pode crescer sem limite pratico.
- Conversas sao salvas localmente sem criptografia.
- Nao ha filtros de privacidade antes de enviar mensagens para API externa.

### 20.2 Site

Fato:

```text
URL -> requests -> BeautifulSoup -> texto limpo -> contexto do bot -> resposta LLM
```

Riscos:

- Site pode bloquear scraping.
- Conteudo dinamico pode nao aparecer.
- Paginas grandes podem estourar contexto.
- O timeout de 15 segundos limita espera excessiva, mas nao ha retry automatico.

### 20.3 Video do YouTube

Fato:

```text
URL -> extracao de video_id -> YouTubeTranscriptApi -> fallback yt-dlp para legendas -> fallback yt-dlp audio + WhisperX opcional ou faster-whisper -> transcricao -> contexto do bot -> resposta LLM
```

Riscos:

- Sem transcricao ou legenda disponivel, nao ha conteudo.
- URL fora dos formatos esperados pode falhar.
- Transcricao automatica pode conter erros.

### 20.4 PDF

Fato:

```text
Caminho PDF -> PdfReader -> texto de paginas -> contexto do bot -> resposta LLM
```

Riscos:

- PDF escaneado pode retornar pouco ou nenhum texto.
- PDF grande pode gerar contexto excessivo.
- Sem metadados de pagina, a resposta nao cita origem por pagina.

### 20.5 OCR Tesseract

Fato:

```text
Imagem -> OpenCV -> Tesseract -> texto -> textos/*.docx e textos/*.txt -> contexto do bot
```

Riscos:

- Depende de Tesseract local.
- Qualidade varia conforme imagem.
- Nome de arquivo nao sanitizado.

### 20.6 Geracao de imagens

Fato:

```text
Prompt -> src/utils/image_generator.py -> OpenAI SDK images.generate -> base64 -> PROJECT_ROOT/imagens/
```

Fato: a geracao usa `gpt-image-2` por padrao, envia `n=1`, valida tamanho, qualidade e formato, decodifica `data[0].b64_json` e salva a imagem localmente.

Fato: quando `CITYBOT_IMAGE_BASE_URL` esta configurado, o client usa `OpenAI(base_url=..., api_key=...)` com `CITYBOT_IMAGE_API_KEY` ou token provider do `DefaultAzureCredential`. Sem esse endpoint, usa `OPENAI_API_KEY`.

Riscos:

- Requer permissao e quota no deployment `gpt-image-2`.
- O uso via Azure AI Foundry depende do login/credencial disponivel para `DefaultAzureCredential`.
- Prompts e imagens geradas passam pelos filtros de seguranca do provedor.

### 20.7 Contextos salvos

Fato:

```text
Fonte carregada -> contexto extraido -> tabela contexts -> selecao na GUI -> contexto atual do bot
```

Fato: a troca de fonte ou modo limpa apenas a sessao ativa na interface e na memoria temporaria, sem apagar conversas persistidas nem contextos salvos.

### 20.8 OCR Gemini

Fato:

```text
Imagem -> PIL -> Gemini multimodal -> texto ou descricao -> contexto do bot
```

Riscos:

- Envia imagem para API externa.
- Nao salva automaticamente em `.docx` e `.txt` na implementacao atual.
- Custo e privacidade dependem do uso.

## 21. Correspondencia entre README e codigo

Fato: em 27/06/2026, o `README.md` foi atualizado para refletir que o codigo ativo em `src/utils` usa:

- `requests` e `BeautifulSoup` para site.
- `youtube-transcript-api`, `yt-dlp`, `faster-whisper` e WhisperX opcional para YouTube.
- `pypdf.PdfReader` para PDF.

Fato: referencias antigas a `WebBaseLoader`, `YoutubeLoader` e `PyPDFLoader` foram removidas da documentacao principal.

## 22. Qualidade de codigo

Pontos positivos verificados:

- Estrutura modular em `src`.
- Ponto de entrada unico.
- Providers separados.
- Utilitarios com funcoes pequenas.
- Uso de SQLite simples e direto.
- GUI com chamadas demoradas em threads.
- Dependencias fixadas em `requirements.txt`.
- `.env`, banco local e outputs ignorados no Git.

Pontos de atencao:

- Cobertura automatizada ainda concentrada em banco e utilitarios.
- Alguns providers e o OCR ainda tratam erros com `print` ou mensagens genericas.
- Logging ainda nao possui configuracao central.
- A validacao de configuracao cobre variaveis ausentes em Gemini e Azure OpenAI, mas ainda nao valida credenciais contra as APIs externas.
- Falta de limites de contexto e tamanho de entrada.
- Falta de timestamps e metadados no historico de conversas.

Opiniao tecnica: o projeto esta em um bom estagio de MVP funcional, mas ainda nao esta pronto para ser tratado como produto confiavel em producao.

## 23. Testes e validacao

Fato: existe uma suite automatizada versionada em `tests/`, implementada com `unittest`.

Fato: a pasta `testes/` esta ignorada no `.gitignore` e contem scripts legados.

Fato: os testes cobrem:

- persistencia e limpeza do banco;
- salvamento, listagem e restauracao de contextos no banco;
- continuidade de gravacao depois da limpeza;
- restauracao e limpeza do historico nas GUIs Gemini e Azure;
- reset da sessao ativa ao voltar para chat livre ou restaurar um contexto salvo;
- timeout e remocao de scripts no scraping;
- parser de URLs do YouTube;
- uso da API de transcricao compativel com a dependencia;
- fallback via `yt-dlp` para legendas do YouTube quando a transcricao direta falha;
- fallback via `faster-whisper` para transcricao local de audio quando transcricao e legendas falham;
- fallback via WhisperX opcional quando `CITYBOT_WHISPER_ENGINE=whisperx` ou quando ele esta instalado no modo `auto`;
- limite de duracao para transcricao local de audio;
- mensagem contextual de bloqueio `HTTP 429 Too Many Requests` no fluxo de video;
- configuracao opcional de cookies do navegador para `yt-dlp`;
- configuracao opcional por arquivo `cookies.txt` e mensagem contextual para banco de cookies bloqueado;
- mensagem contextual para arquivo de cookies fora do formato Netscape;
- paginas PDF sem texto;
- contencao de arquivos OCR dentro de `PROJECT_ROOT/textos/`;
- caminho padrao do banco na raiz do projeto;
- erro claro quando Gemini esta sem variaveis obrigatorias.

Fato: em 27/06/2026, os 10 testes passaram e 16 arquivos Python de producao e teste passaram na validacao de AST.

Fato: em 13/07/2026, os 22 testes passaram com:

```powershell
venv\Scripts\python.exe -m unittest discover -s tests -v
```

Fato: em 13/07/2026, apos a migracao para PySide6, as GUIs Gemini, Groq e Azure foram instanciadas com `QApplication` e fechadas sem chamar APIs externas para validar construcao de janela, estilos, widgets e layout. Em 17/07/2026, o provider Groq foi removido.

Limitacao: ainda faltam testes de chamadas reais ou mockadas do caminho feliz dos providers, OCR e fluxos completos da GUI.

## 24. Observabilidade e logs

Fato: o projeto usa `print` para erros em varios utilitarios e providers.

Opiniao tecnica: para uso local, `print` funciona. Para suporte, debug e producao, e insuficiente.

Melhor abordagem:

- Usar modulo `logging`.
- Definir niveis `INFO`, `WARNING`, `ERROR`.
- Registrar fonte carregada, tamanho do contexto, provider, modelo e duracao.
- Nao registrar prompts completos por padrao, para proteger privacidade.
- Permitir modo debug por variavel de ambiente.

Impacto pratico:

- Ajuda a entender por que OCR, PDF, site ou API falhou.
- Reduz tempo de suporte.
- Permite medir gargalos e custo.

## 25. Privacidade e seguranca

Fatos:

- Conversas sao salvas em `citybot.db`.
- Contextos carregados tambem sao salvos em `citybot.db`.
- Textos de OCR podem ser salvos em `textos/`.
- `.env` e `citybot.db` estao ignorados pelo Git.
- Gemini e Azure OpenAI enviam mensagens para APIs externas.

Riscos:

- Dados sensiveis podem ficar no banco local, tanto em conversas quanto em contextos salvos.
- Imagens enviadas ao Gemini podem conter dados privados.
- Conteudo do clipboard pode ser usado sem o usuario perceber claramente.
- Nomes de arquivos OCR podem permitir caminhos indesejados se nao forem sanitizados.

Opiniao tecnica: antes de uso profissional, o projeto deveria ter:

- Aviso claro de envio para API externa.
- Botao real de apagar historico salvo.
- Opcao de nao salvar conversas.
- Sanitizacao de arquivos gerados.
- Logs sem dados sensiveis.
- Politica de retencao local.

Impacto pratico: essas melhorias reduzem risco juridico, operacional e reputacional, principalmente se o bot for usado com documentos de clientes, contratos, dados pessoais ou informacoes internas.

## 26. Performance e custo

Fato: o texto de site, PDF, video ou OCR e passado como contexto diretamente ao modelo.

Risco real:

- Documentos grandes podem aumentar custo de API.
- Contextos longos podem reduzir qualidade da resposta.
- Pode haver erro por limite de tokens.
- Latencia pode crescer bastante.

Opiniao tecnica: a melhoria mais importante para escala e implementar uma estrategia de recuperacao de contexto:

- Dividir documentos em chunks.
- Criar resumo inicial.
- Recuperar apenas trechos relevantes por pergunta.
- Opcionalmente usar embeddings e busca vetorial.

Trade-off:

- Complexidade: media.
- Custo inicial: maior do que concatenar texto.
- Escalabilidade: muito melhor.
- Performance: melhora em documentos grandes, mas adiciona custo de indexacao.
- Manutencao: exige testes e desenho cuidadoso.

Para o estagio atual, uma solucao simples e eficaz seria limitar tamanho do contexto e avisar o usuario quando o documento for grande demais.

## 27. Recomendacoes priorizadas

### Prioridade 0 - Corrigir riscos que podem causar perda, vazamento ou confusao

Concluido em 27/06/2026:

- Sanitizacao de nomes em `salvar_texto`.
- Limpeza real do historico persistido pela GUI.
- Restauracao do historico com roles corretos.

Concluido em 13/07/2026:

- `citybot.db` padronizado na raiz do projeto quando o caminho padrao e usado.
- Arquivos OCR padronizados em `PROJECT_ROOT/textos`, sem depender do diretorio atual.
- Gemini valida `GEMINI_API_KEY` e `GEMINI_MODEL` antes de criar cliente.
- Provider Groq removido para evitar conflito entre LangChain antigo e `numpy>=2` exigido pelo WhisperX opcional.
- GUI ativa migrada para PySide6 com base visual unica em `src/gui/app_pyside.py`.

Pendente:

1. Validar caminho feliz dos providers com mocks de API.
   - Motivo: a validacao de variaveis cobre ausencia de configuracao, mas nao garante que request e parsing estejam corretos.
   - Impacto: reduz risco de regressao ao atualizar SDKs.
   - Complexidade: baixa.

2. Evitar sobrescrita silenciosa dos arquivos OCR.
   - Motivo: nomes repetidos ainda substituem arquivos anteriores.
   - Impacto: reduz risco de perda de resultados.
   - Complexidade: baixa.

### Prioridade 1 - Melhorar confiabilidade

Concluido em 27/06/2026:

- Timeout em `requests.get`.
- Tratamento de paginas PDF sem texto.
- Parser de URLs do YouTube e compatibilidade com a API fixada.
- Testes unitarios iniciais para `utils` e banco.

Pendente:

1. Adicionar limites de tamanho para HTML, PDF e contexto enviado aos modelos.
2. Expandir testes para providers, OCR e GUI.

### Prioridade 2 - Melhorar manutencao

1. Criar interface comum para providers.
   - Motivo: desacoplar GUI do provider.
   - Impacto: facilita adicionar novos modelos.
   - Complexidade: media.

2. Substituir `print` por `logging`.
   - Motivo: melhorar debug sem poluir interface.
   - Impacto: suporte mais rapido.
   - Complexidade: baixa a media.

### Prioridade 3 - Evoluir produto

1. Implementar chunking e recuperacao de contexto.
   - Motivo: lidar com documentos grandes.
   - Impacto: melhor qualidade e menor custo em escala.
   - Complexidade: media a alta.

2. Adicionar seletor de modelo na GUI.
   - Motivo: permitir equilibrar custo e qualidade.
   - Impacto: flexibilidade para diferentes usuarios.
   - Complexidade: media.

3. Adicionar citacoes por fonte/pagina.
   - Motivo: aumentar confianca em respostas sobre documentos.
   - Impacto: melhor para uso profissional e analitico.
   - Complexidade: media.

## 28. Melhor opcao arquitetural para proxima refatoracao

Opiniao tecnica: como a GUI ativa ja foi unificada em `app_pyside.py`, a melhor proxima refatoracao e criar uma camada comum de provider/servico.

Por que essa opcao e superior:

- Reduz diferencas de contrato entre Gemini e Azure.
- Facilita adicionar novos providers no futuro.
- Mantem a mudanca concentrada no core, sem trocar a experiencia do usuario.

Formato sugerido:

```text
src/
├── core/
│   ├── database.py
│   ├── providers/
│   │   ├── base.py
│   │   ├── gemini.py
│   │   └── azure_openai.py
│   └── citybot_service.py
├── gui/
│   └── app_pyside.py
└── utils/
```

Trade-offs:

- Complexidade: media, porque exige reorganizacao sem quebrar callbacks.
- Custo de implementacao: moderado.
- Escalabilidade: melhora, pois providers passam a ser plugaveis.
- Manutencao: melhora muito.
- Performance: quase nao muda diretamente.
- Risco: controlavel se houver testes basicos antes.

Opiniao tecnica: antes dessa refatoracao, eu criaria testes unitarios minimos para `utils`, `database` e formatacao de historico. Isso evita trocar arquitetura no escuro.

## 29. Dados e analise

Fato: o projeto nao e primariamente um projeto de analise de dados, mas lida com dados textuais vindos de fontes variadas.

Risco real: os dados de entrada nao sao validados profundamente.

Validacoes recomendadas antes de enviar conteudo ao modelo:

- Tipo de fonte.
- Tamanho do texto.
- Texto vazio.
- Quantidade de paginas em PDF.
- Quantidade de caracteres extraidos.
- Presenca de conteudo sensivel, quando possivel.
- Erros de OCR ou baixa confianca.

Opiniao tecnica: sempre que o bot carregar uma fonte, a interface deveria mostrar um resumo tecnico:

- Fonte carregada.
- Tamanho em caracteres.
- Possivel idioma.
- Se houve erro parcial.
- Se o texto parece vazio ou curto demais.

Impacto pratico: isso evita que o usuario faca perguntas sobre um documento que nao foi realmente carregado, reduzindo frustracao e tempo perdido.

## 30. Machine Learning e LLM

Fato: o projeto usa modelos prontos via API. Nao ha treinamento, fine-tuning ou avaliacao ML no repositorio atual.

Riscos especificos de LLM:

- Alucinacao.
- Respostas sem citacao de fonte.
- Uso de contexto grande demais.
- Vazamento de dados para provedor externo.
- Dependencia de disponibilidade das APIs.
- Custo variavel por volume de uso.

Opiniao tecnica: para respostas sobre documentos, o bot deveria informar quando nao encontrou base suficiente no contexto. Isso reduz risco de resposta inventada.

Sugestao de prompt de comportamento:

```text
Quando a resposta depender do documento carregado, responda apenas com base no contexto fornecido.
Se o contexto nao contiver a informacao, diga que nao encontrou essa informacao no material carregado.
```

Trade-off:

- Mais seguranca factual.
- Pode deixar respostas mais conservadoras.
- Melhor para uso profissional.

## 31. Licenca

Fato: o projeto usa licenca MIT.

Fato: o arquivo `LICENSE` indica copyright:

```text
Copyright (c) 2025 Felipe Cidade Soares
```

Opiniao tecnica: MIT e adequada para projeto aberto, prototipo e reaproveitamento. Se o projeto virar produto com dependencias externas e uso de APIs, sera importante revisar tambem os termos de uso de Gemini, Azure OpenAI, YouTube Transcript API, Tesseract e demais bibliotecas.

## 32. Coisas que eu nao sei ainda

Estas informacoes nao foram confirmadas nesta analise:

- Quais valores reais estao no `.env`, porque nao foram lidos para proteger chaves.
- Se as chaves de API estao validas.
- Se todos os fluxos manuais da GUI funcionam com APIs reais. A abertura das GUIs Gemini e Azure em PySide6 deve ser validada localmente sem chamada externa apos a remocao do Groq.
- Se as APIs externas estao funcionando no momento.
- Qual e o objetivo final do projeto, uso pessoal, portfolio, produto interno ou SaaS.

Opiniao tecnica: essas informacoes deveriam ser verificadas antes de qualquer entrega para usuario final.

## 33. Rotina recomendada para manutencao

Sempre que alterar arquivos existentes:

1. Criar ou usar `Backup/`.
2. Criar pasta diaria no formato `dia_mes_ano`, por exemplo `03_06_2026`.
3. Se o arquivo estiver em subpasta, replicar a subpasta dentro do backup conforme convencao do projeto.
4. Salvar copia anterior com nome no formato:

```text
nome_original_03_06_2026_hora_min_seg.extensao
```

5. Fazer a alteracao.
6. Rodar validacao minima.
7. Atualizar este `codex.md`.
8. Verificar `git status --short`.

Fato: neste caso especifico, `codex.md` foi criado do zero, entao nao havia versao anterior para copiar.

Validacao minima recomendada apos mudancas em codigo:

```powershell
venv\Scripts\python.exe -m py_compile main.py src\core\database.py src\core\bot_gemini.py src\core\bot_azure_openai.py src\utils\paths.py src\utils\scrapers.py src\utils\pdf_reader.py src\utils\ocr.py src\utils\file_writer.py src\gui\app_pyside.py src\gui\app_gemini.py src\gui\app_azure_openai.py src\gui\markdown_renderer.py
```

Validacao adicional recomendada quando houver testes:

```powershell
venv\Scripts\python.exe -m unittest discover -s tests -v
```

## 34. Checklist rapido para evoluir sem quebrar

Antes de mexer em provider:

- Validar variaveis de ambiente.
- Mockar chamadas externas.
- Testar historico de mensagens.
- Garantir que erro de API nao trava GUI.

Antes de mexer em GUI:

- Testar Gemini e Azure OpenAI.
- Testar envio de mensagem.
- Testar carregar site, video, PDF e OCR.
- Conferir se `clear_chat` faz exatamente o que o texto do botao promete.

Antes de mexer em banco:

- Fazer backup de `citybot.db` se houver conversas importantes.
- Usar banco temporario nos testes.
- Planejar migracao se alterar schema.

Antes de mexer em OCR:

- Testar imagem inexistente.
- Testar imagem sem texto.
- Testar imagem com texto em portugues.
- Testar nome de arquivo com caracteres invalidos.

Antes de mexer em scraping:

- Testar URL invalida.
- Testar site lento.
- Testar pagina grande.
- Testar video sem transcricao.

## 35. Comandos uteis

Ativar ambiente virtual no PowerShell:

```powershell
.\venv\Scripts\Activate.ps1
```

Instalar dependencias:

```powershell
pip install -r requirements.txt
```

Executar GUI Gemini:

```powershell
python main.py --provider gemini
```

Executar GUI Azure OpenAI:

```powershell
python main.py
```

Executar CLI Gemini:

```powershell
python main.py --mode cli
```

Executar CLI Azure OpenAI:

```powershell
python main.py --provider azure_openai --mode cli
```

Validar sintaxe:

```powershell
venv\Scripts\python.exe -m py_compile main.py src\core\database.py src\core\bot_gemini.py src\core\bot_azure_openai.py src\utils\paths.py src\utils\scrapers.py src\utils\pdf_reader.py src\utils\ocr.py src\utils\file_writer.py src\gui\app_pyside.py src\gui\app_gemini.py src\gui\app_azure_openai.py src\gui\markdown_renderer.py
```

Executar testes:

```powershell
venv\Scripts\python.exe -m unittest discover -s tests -v
```

Ver status do Git:

```powershell
git status --short
```

## 36. Conclusao tecnica

Fato: o CityBot ja possui uma estrutura funcional com entrada unificada, dois provedores de IA, GUI, CLI, utilitarios de conteudo e persistencia local.

Inferencia: o projeto esta em fase de evolucao de prototipo para algo mais organizado, com vestigios de scripts anteriores e algumas inconsistencias de documentacao.

Opiniao tecnica: o projeto merece uma rodada de hardening antes de crescer. A melhor sequencia e:

1. Validar configuracao dos providers antes de criar os clientes.
2. Expandir testes para providers, OCR e GUI.
3. Criar contrato comum de providers.
4. Implementar controle de contexto para documentos grandes.
5. Melhorar privacidade e observabilidade.

Essa ordem e superior porque entrega ganho real rapido, reduz risco de regressao e prepara a base para evolucoes maiores sem reescrever tudo.
