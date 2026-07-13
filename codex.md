# CityBot - Documento tecnico vivo do projeto

Arquivo criado em 03/06/2026.

Ultima atualizacao documentada: 13/07/2026, apos padronizacao de caminhos de dados pela raiz do projeto e validacao explicita de configuracao nos providers Gemini e Groq.

Este documento foi criado para servir como memoria tecnica detalhada do projeto `citybot`. Ele deve ser atualizado sempre que houver alteracao relevante no codigo, dependencias, arquitetura, comportamento, dados, riscos conhecidos ou forma de execucao.

Importante: este arquivo separa explicitamente fato, inferencia e opiniao tecnica.

- Fato: informacao verificada em arquivos do projeto, comandos locais ou estrutura observada.
- Inferencia: deducao baseada no contexto do projeto, mas que nao foi confirmada diretamente por uma especificacao externa.
- Opiniao tecnica: julgamento de engenharia sobre qualidade, risco, trade-off ou melhor caminho.

## 1. Resumo executivo

Fato: o CityBot e um assistente inteligente em Python que combina conversa com LLM, leitura de PDFs, leitura de paginas web, transcricao de videos do YouTube, OCR de imagens e persistencia de historico em SQLite.

Fato: o projeto tem tres provedores de IA implementados:

- Google Gemini, via pacote `google-genai`.
- Groq, via `langchain-groq` e `ChatGroq`.
- Azure OpenAI, via pacote `openai` e classe `AzureOpenAI`.

Fato: o ponto de entrada ativo e `main.py`, que permite escolher:

- Provedor: `gemini`, `groq` ou `azure_openai`.
- Modo: `gui` ou `cli`.

Fato: a interface grafica ativa usa Tkinter. Existem dois arquivos de GUI completos e um app Azure que reaproveita a base visual do Gemini:

- `src/gui/app_gemini.py`.
- `src/gui/app_groq.py`.
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
- `src/core/bot_groq.py`.
- `src/core/bot_gemini.py`.
- `src/core/bot_azure_openai.py`.
- `src/utils/scrapers.py`.
- `src/utils/pdf_reader.py`.
- `src/utils/ocr.py`.
- `src/utils/file_writer.py`.
- `src/utils/paths.py`.
- `src/gui/app_groq.py`.
- `src/gui/app_gemini.py`.
- `src/gui/app_azure_openai.py`.
- `src/gui/markdown_renderer.py`.

## 3. Estrutura de arquivos observada

Fato: a estrutura principal observada e:

```text
citybot/
├── main.py
├── README.md
├── requirements.txt
├── LICENSE
├── citybot.db
├── .env
├── .gitignore
├── venv/
├── Backup/
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
    │   ├── bot_groq.py
    │   ├── bot_gemini.py
    │   └── bot_azure_openai.py
    ├── gui/
    │   ├── app_groq.py
    │   ├── app_gemini.py
    │   ├── app_azure_openai.py
    │   └── markdown_renderer.py
    ├── figures/
    │   ├── citybot_logo.png
    │   ├── citybot_logo.svg
    │   └── logo.png
    └── utils/
        ├── paths.py
        ├── scrapers.py
        ├── pdf_reader.py
        ├── ocr.py
        └── file_writer.py
```

Fato: `src/` contem o codigo ativo modular.

Fato: em 03/06/2026, os assets visuais observados estavam em `src/figures/`:

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
- Uso por GUI Tkinter ou CLI.

Inferencia: o publico-alvo inicial parece ser o proprio desenvolvedor ou usuarios internos que precisam consultar conteudo de forma rapida, em vez de um produto SaaS multiusuario.

Opiniao tecnica: o projeto esta mais proximo de um assistente desktop pessoal do que de uma aplicacao web ou servico em producao. Isso muda as prioridades tecnicas: primeiro vem confiabilidade local, privacidade e ergonomia; depois escalabilidade multiusuario.

## 6. Como executar

Fato: o ponto de entrada e `main.py`.

Comandos documentados pelo projeto:

```powershell
python main.py
python main.py --provider groq
python main.py --provider azure_openai
python main.py --mode cli
python main.py --provider groq --mode cli
python main.py --provider azure_openai --mode cli
```

Fato: valores padrao em `main.py`:

- `--provider` default: `gemini`.
- `--mode` default: `gui`.

Fato: `main.py` usa `argparse` e aceita somente:

- Provider: `groq`, `gemini`, `azure_openai`.
- Mode: `gui`, `cli`.

Opiniao tecnica: esse ponto de entrada e simples e bom para uso local. Para producao ou distribuicao, valeria separar configuracao de ambiente, logs e validacao de dependencias antes de abrir a GUI.

## 7. Variaveis de ambiente

Fato: o codigo espera as seguintes variaveis:

```text
GEMINI_API_KEY
GEMINI_MODEL
GROQ_API_KEY
GROQ_API_MODEL
AZURE_OPENAI_API_KEY
AZURE_ENDPOINT
AZURE_API_VERSION
AZURE_DEPLOYMENT
AZURE_MAX_OUTPUT_TOKENS
```

Fato: `CityBotGemini` le explicitamente `GEMINI_API_KEY` e `GEMINI_MODEL`.

Fato: `CityBotGroq` le explicitamente `GROQ_API_KEY` e `GROQ_API_MODEL`.

Fato: `CityBotAzureOpenAI` le explicitamente `AZURE_OPENAI_API_KEY`, `AZURE_ENDPOINT`, `AZURE_API_VERSION`, `AZURE_DEPLOYMENT` e opcionalmente `AZURE_MAX_OUTPUT_TOKENS`.

Fato: em 13/07/2026, Gemini e Groq passaram a validar variaveis obrigatorias no construtor, guardar `config_error` e retornar erro claro em `resposta_bot` quando a configuracao esta incompleta.

Risco residual:

- A presenca das variaveis nao garante que chaves, deployments ou modelos estejam validos nos provedores externos.
- A validacao evita erro confuso por variavel ausente, mas nao substitui testes reais de conectividade.

## 8. Dependencias

Fato: `requirements.txt` lista dependencias diretas usadas pelo codigo ativo e por scripts legados.

Dependencias principais:

- `python-dotenv`: carrega `.env`.
- `google-genai`: SDK do Gemini.
- `openai`: SDK usado pelo provider Azure OpenAI com `AzureOpenAI`.
- `langchain`: usado por Groq para prompt/memoria.
- `langchain-groq`: cliente Groq via LangChain.
- `requests`: leitura de paginas web.
- `beautifulsoup4`: parse HTML.
- `youtube-transcript-api`: transcricao do YouTube.
- `truststore`: validacao HTTPS usando certificados confiaveis do sistema operacional.
- `pypdf`: leitura de PDF.
- `opencv-python`: pre-processamento de imagem para OCR Tesseract.
- `pytesseract`: OCR local.
- `langdetect`: deteccao de idioma para OCR.
- `python-docx`: escrita de `.docx`.
- `pyperclip`: leitura/limpeza da area de transferencia no CLI.
- `pillow`: imagens na GUI e OCR Gemini.

Fato: `tkinter` nao aparece em `requirements.txt`, pois normalmente faz parte da biblioteca padrao do Python em instalacoes desktop.

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
  ├── GUI Tkinter
  │   ├── src/gui/app_gemini.py
  │   ├── src/gui/app_groq.py
  │   └── src/gui/app_azure_openai.py
  ├── Core de IA e persistencia
  │   ├── src/core/bot_gemini.py
  │   ├── src/core/bot_groq.py
  │   ├── src/core/bot_azure_openai.py
  │   └── src/core/database.py
  └── Utilitarios de entrada/saida
      ├── src/utils/scrapers.py
      ├── src/utils/pdf_reader.py
      ├── src/utils/ocr.py
      └── src/utils/file_writer.py
```

Inferencia: `main.py` foi desenhado para ser um roteador simples, mantendo detalhes de GUI e LLM fora do ponto de entrada.

Opiniao tecnica: a separacao `core`, `gui` e `utils` e boa. O maior problema arquitetural atual e duplicacao: as GUIs Gemini e Groq repetem praticamente a mesma estrutura visual e comportamento.

Melhor caminho tecnico:

- Criar uma GUI unica que recebe uma instancia de bot ou uma factory de bot.
- Manter `CityBotGemini` e `CityBotGroq` como adaptadores de provider.
- Definir uma interface comum de bot, por exemplo `resposta_bot`, `carrega_site`, `carrega_video`, `carrega_pdf`, `carrega_imagem_ocr`, `save_conversation`.

Trade-off:

- Complexidade: baixa a media.
- Custo de implementacao: moderado, porque exige mexer em GUI e inicializacao.
- Manutencao: melhora bastante, pois bugs visuais seriam corrigidos uma vez.
- Risco: medio, porque GUI Tkinter e sensivel a pequenas mudancas de callback e threading.

## 10. `main.py`

Fato: `main.py` importa `argparse`, `sys`, `os` e `tkinter`.

Fato: adiciona a raiz do projeto ao `sys.path`:

```python
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
```

Fato: `run_gui(provider)`:

- Cria `tk.Tk()`.
- Se provider for `gemini`, importa `ModernCityBotGUI` de `src.gui.app_gemini`.
- Se provider for `azure_openai`, importa `ModernCityBotGUI` de `src.gui.app_azure_openai`.
- Caso contrario, importa `ModernCityBotGUI` de `src.gui.app_groq`.
- Inicia `root.mainloop()`.

Fato: `run_cli(provider)`:

- Instancia `CityBotGemini` ou `CityBotGroq`.
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

Fato: metodos disponiveis:

- `create_table()`.
- `save_user(name, preferences)`.
- `load_user(name)`.
- `save_conversation(user_message, assistant_response)`.
- `load_conversations()`.
- `limpar_conversas()`.
- `limpar_banco()`.

Fato: `limpar_conversas()` apaga somente o historico. `limpar_banco()` executa `DELETE` nas tabelas `conversations` e `users`. Ambos preservam o schema para novas gravacoes.

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

## 13. Provider Groq

Arquivo: `src/core/bot_groq.py`.

Fato: a classe principal e `CityBotGroq`.

Fato: no construtor:

- Chama `load_dotenv()`.
- Le `GROQ_API_KEY`.
- Le `GROQ_API_MODEL`.
- Valida variaveis obrigatorias em `config_error`.
- Cria `CityBotDatabase`.
- Cria `ConversationBufferWindowMemory(k=1000000)`.

Fato: `chat()` cria:

```python
ChatGroq(model=self.api_model)
```

Fato: `resposta_bot(mensagens, documento='')` cria uma mensagem de sistema:

```text
Você é um assistente amigável chamado CityBot, capaz de conversar sobre qualquer assunto, inclusive qualquer informação sobre {informacoes}.
```

Fato: o historico e convertido para lista de mensagens do `ChatPromptTemplate`.

Fato: a chain e:

```python
template | self.chat()
```

Fato: a resposta final e:

```python
chain.invoke({'informacoes': informacoes}).content
```

Fato: o OCR na versao Groq chama Tesseract e, se houver texto, salva arquivos via `salvar_texto(texto_final, nome)`.

Fato: se `GROQ_API_KEY` ou `GROQ_API_MODEL` estiverem ausentes, `resposta_bot` retorna texto no formato:

```text
Erro de configuracao Groq: ...
```

Risco real:

- `ConversationBufferWindowMemory(k=1000000)` e um valor extremamente alto e pode manter historico demais em memoria.
- A memoria LangChain e usada no CLI, mas o prompt enviado ao modelo tambem usa `mensagens`, entao ha potencial de redundancia conceitual.
- O uso de contexto completo do documento tambem pode estourar limite de tokens.

Opiniao tecnica: a validacao explicita reduziu erro operacional no inicio da conversa, mas o provider ainda precisa de testes mockados do caminho feliz e melhor controle de contexto.

## 13.1 Provider Azure OpenAI

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

Fato: o OCR no provider Azure OpenAI usa Tesseract local e salva o texto via `salvar_texto`, igual ao fluxo Groq. Imagens nao sao enviadas ao Azure OpenAI nessa implementacao.

Opiniao tecnica: essa decisao e conservadora e boa para privacidade, porque o exemplo recebido cobre texto, nao imagem. Caso seja desejado OCR multimodal via Azure no futuro, isso deve ser tratado como nova decisao de produto por envolver custo, privacidade e suporte do deployment.

Trade-offs:

- Complexidade: baixa, porque segue o mesmo contrato dos outros bots.
- Custo de implementacao: baixo a medio, por reaproveitar utilitarios existentes.
- Manutencao: boa, pois a GUI Azure reaproveita a base visual do Gemini.
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
- Usa `YouTubeTranscriptApi().fetch(video_id, languages=['pt', 'en'])`, compativel com a versao `1.2.4` fixada.
- Usa `truststore` para validar HTTPS com o repositorio de certificados do sistema operacional.
- Concatena textos da transcricao.

Risco real em sites:

- Nao ha limite de tamanho de HTML.
- Nao ha validacao de URL.
- Nao ha protecao contra acessar enderecos internos ou locais, caso isso seja usado em ambiente corporativo.
- Conteudo renderizado por JavaScript pode nao ser capturado.

Risco real em YouTube:

- Videos sem transcricao em `pt` ou `en` retornam erro.
- Transcricoes podem estar indisponiveis por configuracao do video.

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

## 18. Interface grafica Tkinter

Arquivos:

- `src/gui/app_gemini.py`.
- `src/gui/app_groq.py`.

Fato: ambos definem uma classe chamada `ModernCityBotGUI`.

Fato: a GUI usa:

- Tema escuro.
- Sidebar com fontes de dados.
- Area de chat com bolhas.
- Entrada de texto.
- Barra de status.
- Logo carregado de `src/figures/citybot_logo.png`.
- Threads para chamadas demoradas.

Fato: em 03/06/2026, foi criado `src/gui/markdown_renderer.py` para renderizar Markdown basico dentro da GUI usando apenas Tkinter.

Fato: as bolhas de mensagem deixaram de usar `tk.Label` para o corpo da mensagem e passaram a usar `tk.Text` readonly com tags de formatacao.

Fato: em 08/06/2026, uma tentativa de redimensionar automaticamente a altura da bolha Markdown apos renderizacao foi removida, porque causava bolhas visualmente grandes demais para mensagens curtas. A causa principal das respostas Azure cortadas era o limite baixo de `AZURE_MAX_OUTPUT_TOKENS`.

Fato: o renderizador Markdown suporta:

- Titulos `#`, `##` e `###`.
- Negrito com `**texto**`.
- Italico com `*texto*`.
- Negrito e italico com `***texto***`.
- Codigo inline com crases.
- Blocos de codigo com cercas de crases triplas.
- Listas simples e numeradas.
- Tabelas Markdown simples no formato GitHub, com cabecalho, separador e linhas iniciadas e encerradas por `|`.
- Citacoes iniciadas com `>`.
- Regras horizontais com `---`, `***` ou `___`.
- Links no formato `[texto](url)`, com clique abrindo o navegador padrao.

Fato: nao foi adicionada dependencia nova para Markdown. A decisao foi manter Tkinter e implementar um renderer pequeno, porque isso preserva simplicidade, reduz custo de instalacao e evita JS.

Fato: em 08/06/2026, `src/gui/markdown_renderer.py` passou a detectar blocos de tabela compostos por linha de cabecalho, linha separadora `|---|---|` e linhas de dados. A renderizacao remove os pipes crus, ignora a linha separadora original e exibe a tabela alinhada em fonte monoespacada.

Opiniao tecnica: a implementacao de tabela e propositalmente simples. Ela cobre bem tabelas comuns geradas por LLMs, mas nao tenta implementar todo o CommonMark, como pipes escapados dentro de celulas, alinhamento por coluna ou tabelas com conteudo multiline.

Fato: `app_groq.py` foi corrigido para importar `Path` de `pathlib`, e nao de `anyio`.

Fato: `app_gemini.py` e `app_groq.py` agora resolvem o logo com base em `root_path`, usando `Path(root_path) / 'src' / 'figures' / 'citybot_logo.png`.

Fato: em 03/06/2026, `src/gui/app_azure_openai.py` foi ajustado para adicionar a raiz do projeto ao `sys.path` antes dos imports `src.*`. Isso permite executar diretamente:

```powershell
& C:/Users/felip/OneDrive/git_work/citybot/venv/Scripts/python.exe c:/Users/felip/OneDrive/git_work/citybot/src/gui/app_azure_openai.py
```

sem `ModuleNotFoundError: No module named 'src'`.

Fato: em 03/06/2026, `conversation_history` na GUI foi corrigido para armazenar tuplas com papel da mensagem:

```python
("user", user_message)
("assistant", response)
```

Impacto pratico: respostas em Markdown agora ficam mais legiveis na interface, especialmente listas, blocos de codigo, titulos e trechos em negrito. A correcao do historico tambem melhora a qualidade das respostas, porque o modelo deixa de receber respostas antigas como se fossem novas mensagens do usuario.

Trade-offs da solucao com Tkinter:

- Complexidade: baixa a media, porque o renderer e local e pequeno.
- Custo de implementacao: baixo, sem dependencia externa.
- Manutencao: melhor do que duplicar regex nas duas GUIs, pois o parser fica centralizado.
- Escalabilidade visual: suficiente para Markdown basico, mas nao substitui um renderer HTML completo.
- Performance: boa para mensagens comuns; respostas extremamente longas ainda podem deixar a bolha grande.

Fato: opcoes de fonte na sidebar:

- Chat Livre.
- Carregar Site.
- Carregar Video.
- Carregar PDF.
- OCR Imagem.
- Limpar Conversa.

Fato: a GUI usa `threading.Thread(..., daemon=True)` para processar mensagens e carregamentos externos.

Fato: atualizacoes de interface vindas de threads usam em varios pontos `self.root.after(0, ...)`, que e o caminho correto em Tkinter.

Risco real:

- A duplicacao entre `app_gemini.py` e `app_groq.py` aumenta custo de manutencao.
- Correcoes feitas em uma GUI podem ficar faltando na outra.
- O Markdown implementado cobre os casos comuns, incluindo tabelas simples, mas ainda nao oferece imagens embutidas, notas de rodape, celulas multiline ou parser CommonMark completo.

Fato: apos confirmacao do usuario, `clear_chat()` apaga somente as conversas persistidas, limpa a tela, o historico em memoria e o contexto carregado. Perfis de usuario sao preservados. A limpeza e bloqueada enquanto uma resposta esta em processamento.

Fato: ao iniciar, as GUIs Gemini, Groq e Azure restauram o historico salvo com roles `user` e `assistant`.

Impacto pratico: o comportamento visual agora corresponde ao estado persistido e o botao nao deixa conversas antigas no banco.

## 19. Interface CLI

Arquivos:

- `src/core/bot_gemini.py`.
- `src/core/bot_groq.py`.
- `src/core/bot_azure_openai.py`.

Fato: os tres providers possuem metodo `menu()`.

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

Fato: a versao Groq tambem usa `pyperclip.paste()` em parte do fluxo.

Fato: em 27/06/2026, a restauracao do historico no CLI Groq foi corrigida para converter cada registro do banco em duas mensagens, `user` e `assistant`.

Risco real:

- Ler automaticamente area de transferencia pode gerar comportamento inesperado se houver senha, token, documento sensivel ou texto grande copiado.
- Nao ha confirmacao explicita de uso de dados da area de transferencia em todos os caminhos.

Opiniao tecnica: para uso pessoal e pratico, isso pode ser conveniente. Para uso profissional, melhor pedir confirmacao clara antes de usar conteudo do clipboard.

## 20. Fluxos de dados

### 20.1 Chat livre

Fato:

```text
Usuario -> GUI/CLI -> CityBotGemini ou CityBotGroq -> API LLM -> resposta -> SQLite
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
URL -> extracao de video_id -> YouTubeTranscriptApi -> transcricao -> contexto do bot -> resposta LLM
```

Riscos:

- Sem transcricao disponivel, nao ha conteudo.
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

### 20.6 OCR Gemini

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
- `youtube-transcript-api` para YouTube.
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

- Duplicacao forte entre GUIs.
- Cobertura automatizada ainda concentrada em banco e utilitarios.
- Alguns providers e o OCR ainda tratam erros com `print` ou mensagens genericas.
- Logging ainda nao possui configuracao central.
- A validacao de configuracao cobre variaveis ausentes em Gemini, Groq e Azure OpenAI, mas ainda nao valida credenciais contra as APIs externas.
- Falta de limites de contexto e tamanho de entrada.
- Falta de timestamps e metadados no banco.

Opiniao tecnica: o projeto esta em um bom estagio de MVP funcional, mas ainda nao esta pronto para ser tratado como produto confiavel em producao.

## 23. Testes e validacao

Fato: existe uma suite automatizada versionada em `tests/`, implementada com `unittest`.

Fato: a pasta `testes/` esta ignorada no `.gitignore` e contem scripts legados.

Fato: os testes cobrem:

- persistencia e limpeza do banco;
- continuidade de gravacao depois da limpeza;
- restauracao e limpeza do historico nas GUIs Gemini e Groq;
- timeout e remocao de scripts no scraping;
- parser de URLs do YouTube;
- uso da API de transcricao compativel com a dependencia;
- paginas PDF sem texto;
- contencao de arquivos OCR dentro de `PROJECT_ROOT/textos/`;
- caminho padrao do banco na raiz do projeto;
- erro claro quando Gemini ou Groq estao sem variaveis obrigatorias.

Fato: em 27/06/2026, os 10 testes passaram e 16 arquivos Python de producao e teste passaram na validacao de AST.

Fato: em 13/07/2026, os 13 testes passaram com:

```powershell
venv\Scripts\python.exe -m unittest discover -s tests -v
```

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
- Textos de OCR podem ser salvos em `textos/`.
- `.env` e `citybot.db` estao ignorados pelo Git.
- Gemini e Groq enviam mensagens para APIs externas.

Riscos:

- Dados sensiveis podem ficar no banco local.
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
- Groq valida `GROQ_API_KEY` e `GROQ_API_MODEL` antes de chamar o modelo.

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

1. Unificar GUI Gemini e Groq.
   - Motivo: reduzir duplicacao.
   - Impacto: menos bugs duplicados e mais velocidade de evolucao.
   - Complexidade: media.

2. Criar interface comum para providers.
   - Motivo: desacoplar GUI do provider.
   - Impacto: facilita adicionar novos modelos.
   - Complexidade: media.

3. Substituir `print` por `logging`.
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

Opiniao tecnica: a melhor proxima refatoracao e criar uma camada comum de provider e uma GUI unica.

Por que essa opcao e superior:

- Ataca a duplicacao mais visivel do projeto.
- Reduz risco de uma interface evoluir diferente da outra.
- Facilita adicionar novos providers no futuro.
- Mantem a mudanca concentrada na arquitetura, sem trocar a experiencia do usuario.

Formato sugerido:

```text
src/
├── core/
│   ├── database.py
│   ├── providers/
│   │   ├── base.py
│   │   ├── gemini.py
│   │   └── groq.py
│   └── citybot_service.py
├── gui/
│   └── app.py
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

Opiniao tecnica: MIT e adequada para projeto aberto, prototipo e reaproveitamento. Se o projeto virar produto com dependencias externas e uso de APIs, sera importante revisar tambem os termos de uso de Gemini, Groq, YouTube Transcript API, Tesseract e demais bibliotecas.

## 32. Coisas que eu nao sei ainda

Estas informacoes nao foram confirmadas nesta analise:

- Quais valores reais estao no `.env`, porque nao foram lidos para proteger chaves.
- Se as chaves de API estao validas.
- Se a GUI abre corretamente no ambiente atual.
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
venv\Scripts\python.exe -m py_compile main.py src\core\database.py src\core\bot_groq.py src\core\bot_gemini.py src\core\bot_azure_openai.py src\utils\paths.py src\utils\scrapers.py src\utils\pdf_reader.py src\utils\ocr.py src\utils\file_writer.py src\gui\app_groq.py src\gui\app_gemini.py src\gui\app_azure_openai.py src\gui\markdown_renderer.py
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

- Testar Gemini e Groq.
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
python main.py
```

Executar GUI Groq:

```powershell
python main.py --provider groq
```

Executar GUI Azure OpenAI:

```powershell
python main.py --provider azure_openai
```

Executar CLI Gemini:

```powershell
python main.py --mode cli
```

Executar CLI Groq:

```powershell
python main.py --provider groq --mode cli
```

Executar CLI Azure OpenAI:

```powershell
python main.py --provider azure_openai --mode cli
```

Validar sintaxe:

```powershell
python -c "import ast, pathlib; files=[pathlib.Path('main.py'), *pathlib.Path('src').rglob('*.py'), *pathlib.Path('tests').rglob('*.py')]; [ast.parse(path.read_text(encoding='utf-8')) for path in files]"
```

Executar testes:

```powershell
python -m unittest discover -s tests -v
```

Ver status do Git:

```powershell
git status --short
```

## 36. Conclusao tecnica

Fato: o CityBot ja possui uma estrutura funcional com entrada unificada, tres provedores de IA, GUI, CLI, utilitarios de conteudo e persistencia local.

Inferencia: o projeto esta em fase de evolucao de prototipo para algo mais organizado, com vestigios de scripts anteriores e algumas inconsistencias de documentacao.

Opiniao tecnica: o projeto merece uma rodada de hardening antes de crescer. A melhor sequencia e:

1. Validar configuracao dos providers antes de criar os clientes.
2. Expandir testes para providers, OCR e GUI.
3. Unificar GUI e providers com uma interface comum.
4. Implementar controle de contexto para documentos grandes.
5. Melhorar privacidade e observabilidade.

Essa ordem e superior porque entrega ganho real rapido, reduz risco de regressao e prepara a base para evolucoes maiores sem reescrever tudo.
