import html
import json
import logging
import os
import re
import tempfile
from pathlib import Path
from urllib.parse import parse_qs, urlparse
from xml.etree import ElementTree

import truststore

truststore.inject_into_ssl()

import requests
from bs4 import BeautifulSoup
from youtube_transcript_api import YouTubeTranscriptApi

try:
    from yt_dlp import YoutubeDL
except ImportError:
    YoutubeDL = None

try:
    from faster_whisper import WhisperModel
except ImportError:
    WhisperModel = None


logger = logging.getLogger(__name__)
REQUEST_TIMEOUT_SECONDS = 15
VIDEO_LANGUAGES = ['pt', 'pt-BR', 'en']
CAPTION_SOURCE_KEYS = ('subtitles', 'automatic_captions')
CAPTION_FORMAT_PRIORITY = ('json3', 'vtt', 'srv3', 'ttml')
YOUTUBE_COOKIES_BROWSER_ENV = 'CITYBOT_YOUTUBE_COOKIES_BROWSER'
YOUTUBE_COOKIES_PROFILE_ENV = 'CITYBOT_YOUTUBE_COOKIES_PROFILE'
YOUTUBE_COOKIES_FILE_ENV = 'CITYBOT_YOUTUBE_COOKIES_FILE'
YOUTUBE_RATE_LIMIT_HINT = (
    'O YouTube bloqueou temporariamente as requisições de transcrição/legenda '
    '(HTTP 429 Too Many Requests). Tente novamente mais tarde, feche totalmente '
    'o navegador antes de usar CITYBOT_YOUTUBE_COOKIES_BROWSER ou configure '
    'CITYBOT_YOUTUBE_COOKIES_FILE com um arquivo cookies.txt.'
)
YOUTUBE_COOKIE_DATABASE_HINT = (
    'O yt-dlp não conseguiu acessar ou descriptografar os cookies do navegador. '
    'O CityBot tenta continuar sem esses cookies, mas se o YouTube bloquear a '
    'requisição anônima, feche totalmente o Chrome/Edge ou use '
    'CITYBOT_YOUTUBE_COOKIES_FILE apontando para um arquivo cookies.txt.'
)
YOUTUBE_INVALID_COOKIES_FILE_HINT = (
    'O arquivo configurado em CITYBOT_YOUTUBE_COOKIES_FILE não está no formato '
    'Netscape cookies.txt aceito pelo yt-dlp. Exporte os cookies novamente nesse '
    'formato; arquivos JSON, HTML ou SQLite do navegador não funcionam.'
)
YOUTUBE_AUDIO_DOWNLOAD_HINT = (
    'Também não foi possível baixar o áudio do vídeo para tentar a transcrição '
    'local. Isso pode acontecer por bloqueio do YouTube, vídeo privado/restrito, '
    'cookies inválidos ou falha de conexão.'
)
WHISPER_MODEL_ENV = 'CITYBOT_WHISPER_MODEL'
WHISPER_DEVICE_ENV = 'CITYBOT_WHISPER_DEVICE'
WHISPER_COMPUTE_TYPE_ENV = 'CITYBOT_WHISPER_COMPUTE_TYPE'
WHISPER_LANGUAGE_ENV = 'CITYBOT_WHISPER_LANGUAGE'
WHISPER_MAX_AUDIO_SECONDS_ENV = 'CITYBOT_WHISPER_MAX_AUDIO_SECONDS'
DEFAULT_WHISPER_MODEL = 'base'
DEFAULT_WHISPER_DEVICE = 'cpu'
DEFAULT_WHISPER_COMPUTE_TYPE = 'int8'
DEFAULT_WHISPER_MAX_AUDIO_SECONDS = 7200


class ExtractedContent(str):
    def __new__(cls, value, error_message=''):
        obj = super().__new__(cls, value)
        obj.error_message = error_message
        return obj


def carrega_site(url_site):
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(
            url_site,
            headers=headers,
            timeout=REQUEST_TIMEOUT_SECONDS,
        )
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        for script in soup(['script', 'style']):
            script.decompose()
            
        texto = soup.get_text(separator=' ')
        lines = (line.strip() for line in texto.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split('  '))
        return '\n'.join(chunk for chunk in chunks if chunk)
        
    except Exception as e:
        logger.error('Erro ao carregar o site: %s', e)
        return ''


def _extrai_video_id(url_video):
    parsed = urlparse(url_video.strip())
    hostname = (parsed.hostname or '').lower()
    path_parts = [part for part in parsed.path.split('/') if part]

    if hostname in {'youtu.be', 'www.youtu.be'}:
        return path_parts[0] if path_parts else ''

    if hostname.endswith('youtube.com'):
        if parsed.path == '/watch':
            return parse_qs(parsed.query).get('v', [''])[0]
        if path_parts and path_parts[0] in {'embed', 'shorts', 'live'}:
            return path_parts[1] if len(path_parts) > 1 else ''

    return ''


def carrega_video(url_video):
    video_id = _extrai_video_id(url_video)

    if not video_id:
        message = 'ID do vídeo não encontrado na URL informada.'
        logger.warning(message)
        return ExtractedContent('', message)

    errors = []
    transcript_text, transcript_error = _carrega_transcricao_youtube(video_id)
    if transcript_text:
        return transcript_text
    errors.append(transcript_error)

    caption_text, caption_error = _carrega_legendas_yt_dlp(url_video)
    if caption_text:
        return caption_text
    errors.append(caption_error)

    audio_text, audio_error = _transcreve_audio_youtube(url_video)
    if audio_text:
        return audio_text
    errors.append(audio_error)

    return ExtractedContent('', _mensagem_erro_video(errors))


def _carrega_transcricao_youtube(video_id):
    try:
        transcript = YouTubeTranscriptApi().fetch(
            video_id,
            languages=VIDEO_LANGUAGES,
        )
        text = _normaliza_texto(item.text for item in transcript if item.text)
        if text:
            return text, ''
        return '', 'A transcrição direta do YouTube veio vazia.'
    except Exception as e:
        message = f'Falha ao carregar transcrição com youtube-transcript-api: {e}'
        logger.warning(message)
        return '', message


def _carrega_legendas_yt_dlp(url_video):
    if YoutubeDL is None:
        message = 'yt-dlp não está instalado. Execute pip install -r requirements.txt.'
        logger.warning(message)
        return '', message

    text, error = _tenta_carregar_legendas_yt_dlp(url_video, use_browser_cookies=True)
    if text or not _deve_tentar_sem_cookies_do_navegador(error):
        return text, error

    logger.warning('Falha ao usar cookies do navegador no yt-dlp. Tentando novamente sem cookies do navegador.')
    retry_text, retry_error = _tenta_carregar_legendas_yt_dlp(url_video, use_browser_cookies=False)
    if retry_text:
        return retry_text, ''
    return '', f'{error} | Tentativa sem cookies do navegador: {retry_error}'


def _tenta_carregar_legendas_yt_dlp(url_video, use_browser_cookies):
    try:
        with YoutubeDL(_yt_dlp_options(use_browser_cookies=use_browser_cookies)) as ydl:
            video_info = ydl.extract_info(url_video, download=False)
            caption = _seleciona_legenda(video_info or {})
            if not caption:
                message = 'Nenhuma legenda compatível encontrada para o vídeo.'
                logger.warning(message)
                return '', message

            content = _baixa_legenda_yt_dlp(ydl, caption)
            text = _extrai_texto_legenda(content, caption.get('ext', ''))
            if text:
                return text, ''
            message = 'A legenda encontrada foi baixada, mas não continha texto legível.'
            logger.warning(message)
            return '', message
    except Exception as e:
        message = f'Erro ao carregar legenda do vídeo com yt-dlp: {e}'
        logger.error(message)
        return '', message


def _baixa_legenda_yt_dlp(ydl, caption):
    response = ydl.urlopen(caption['url'])
    return response.read().decode('utf-8', errors='replace')


def _transcreve_audio_youtube(url_video):
    if YoutubeDL is None:
        message = 'yt-dlp não está instalado. Execute pip install -r requirements.txt.'
        logger.warning(message)
        return '', message
    if WhisperModel is None:
        message = 'faster-whisper não está instalado. Execute pip install -r requirements.txt.'
        logger.warning(message)
        return '', message

    try:
        with tempfile.TemporaryDirectory(prefix='citybot_youtube_audio_') as temp_dir:
            try:
                audio_path = _baixa_audio_yt_dlp(url_video, temp_dir)
            except Exception as e:
                message = f'Não foi possível baixar o áudio do vídeo para transcrição local: {e}'
                logger.error(message)
                return '', message

            try:
                text = _transcreve_audio_whisper(audio_path)
            except Exception as e:
                message = f'O áudio foi baixado, mas não foi possível transcrever com faster-whisper: {e}'
                logger.error(message)
                return '', message

            if text:
                return text, ''
            message = 'O áudio foi baixado, mas o Whisper não encontrou fala legível.'
            logger.warning(message)
            return '', message
    except Exception as e:
        message = f'Erro ao transcrever áudio do vídeo com faster-whisper: {e}'
        logger.error(message)
        return '', message


def _baixa_audio_yt_dlp(url_video, output_dir):
    try:
        return _tenta_baixar_audio_yt_dlp(url_video, output_dir, use_browser_cookies=True)
    except Exception as e:
        if not _deve_tentar_sem_cookies_do_navegador(str(e)):
            raise

        logger.warning('Falha ao usar cookies do navegador no download de áudio. Tentando novamente sem cookies do navegador.')
        try:
            return _tenta_baixar_audio_yt_dlp(url_video, output_dir, use_browser_cookies=False)
        except Exception as retry_error:
            raise RuntimeError(
                f'{e} | Tentativa sem cookies do navegador: {retry_error}'
            ) from retry_error


def _tenta_baixar_audio_yt_dlp(url_video, output_dir, use_browser_cookies):
    output_path = Path(output_dir)
    options = _audio_yt_dlp_options(output_path, use_browser_cookies=use_browser_cookies)

    with YoutubeDL(options) as ydl:
        before_download = set(output_path.iterdir())
        result = ydl.download([url_video])
        if result:
            raise RuntimeError(f'yt-dlp retornou código {result} ao baixar áudio.')

    downloaded_files = [
        path
        for path in output_path.iterdir()
        if path.is_file() and path not in before_download
    ]
    if not downloaded_files:
        downloaded_files = [path for path in output_path.iterdir() if path.is_file()]
    if not downloaded_files:
        raise RuntimeError('yt-dlp não gerou arquivo de áudio.')

    return max(downloaded_files, key=lambda path: path.stat().st_size)


def _audio_yt_dlp_options(output_path, use_browser_cookies=True):
    options = _yt_dlp_options(use_browser_cookies=use_browser_cookies)
    options.update({
        'format': 'bestaudio/best',
        'outtmpl': str(output_path / '%(id)s.%(ext)s'),
        'skip_download': False,
        'match_filter': _filtro_duracao_audio,
    })
    return options


def _filtro_duracao_audio(video_info, incomplete=False):
    if incomplete:
        return None
    try:
        _valida_duracao_audio(video_info or {})
    except RuntimeError as e:
        return str(e)
    return None


def _valida_duracao_audio(video_info):
    live_status = str(video_info.get('live_status') or '').lower()
    if video_info.get('is_live') or live_status in {'is_live', 'is_upcoming'}:
        raise RuntimeError(
            'Vídeo ao vivo ou agendado ainda não está disponível para transcrição local. '
            'Tente novamente quando a transmissão terminar.'
        )

    max_seconds = _env_int(WHISPER_MAX_AUDIO_SECONDS_ENV, DEFAULT_WHISPER_MAX_AUDIO_SECONDS)
    duration = int(video_info.get('duration') or 0)
    if max_seconds > 0 and duration > max_seconds:
        raise RuntimeError(
            f'Vídeo com {duration} segundos excede o limite de {max_seconds} segundos '
            f'para transcrição local. Ajuste {WHISPER_MAX_AUDIO_SECONDS_ENV} se quiser permitir vídeos maiores.'
        )


def _transcreve_audio_whisper(audio_path):
    model = WhisperModel(
        os.getenv(WHISPER_MODEL_ENV, DEFAULT_WHISPER_MODEL).strip() or DEFAULT_WHISPER_MODEL,
        device=os.getenv(WHISPER_DEVICE_ENV, DEFAULT_WHISPER_DEVICE).strip() or DEFAULT_WHISPER_DEVICE,
        compute_type=os.getenv(WHISPER_COMPUTE_TYPE_ENV, DEFAULT_WHISPER_COMPUTE_TYPE).strip() or DEFAULT_WHISPER_COMPUTE_TYPE,
    )
    language = os.getenv(WHISPER_LANGUAGE_ENV, '').strip() or None
    segments, _ = model.transcribe(
        str(audio_path),
        language=language,
        beam_size=5,
        vad_filter=True,
    )
    return _normaliza_texto(segment.text for segment in segments if segment.text)


def _env_int(name, default):
    value = os.getenv(name, '').strip()
    if not value:
        return default
    try:
        return int(value)
    except ValueError:
        return default


def _yt_dlp_options(use_browser_cookies=True):
    options = {
        'quiet': True,
        'no_warnings': True,
        'skip_download': True,
        'noplaylist': True,
        'socket_timeout': REQUEST_TIMEOUT_SECONDS,
        'retries': 1,
        'extractor_retries': 1,
        'http_headers': {
            'User-Agent': (
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                'AppleWebKit/537.36 (KHTML, like Gecko) '
                'Chrome/126.0.0.0 Safari/537.36'
            ),
            'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
        },
    }
    cookie_file = os.getenv(YOUTUBE_COOKIES_FILE_ENV, '').strip()
    if cookie_file:
        options['cookiefile'] = cookie_file
        return options

    cookies_from_browser = _cookies_from_browser() if use_browser_cookies else None
    if cookies_from_browser:
        options['cookiesfrombrowser'] = cookies_from_browser
    return options


def _cookies_from_browser():
    browser = os.getenv(YOUTUBE_COOKIES_BROWSER_ENV, '').strip()
    if not browser:
        return None

    profile = os.getenv(YOUTUBE_COOKIES_PROFILE_ENV, '').strip()
    if profile:
        return (browser, profile)
    return (browser,)


def _seleciona_legenda(video_info):
    captions_by_source = {
        source_key: video_info.get(source_key) or {}
        for source_key in CAPTION_SOURCE_KEYS
    }
    available_captions = {}
    for captions in captions_by_source.values():
        available_captions.update(captions)

    for language in _ordena_idiomas(available_captions):
        for source_key in CAPTION_SOURCE_KEYS:
            captions = captions_by_source[source_key]
            caption = _seleciona_formato_legenda(captions.get(language) or [])
            if caption:
                return caption
    return None


def _ordena_idiomas(captions):
    available_languages = list(captions)
    ordered_languages = []

    for preferred_language in VIDEO_LANGUAGES:
        _add_matching_languages(available_languages, ordered_languages, preferred_language, exact=True)

    for preferred_language in VIDEO_LANGUAGES:
        _add_matching_languages(available_languages, ordered_languages, preferred_language, exact=False)

    return ordered_languages + [
        language
        for language in available_languages
        if language not in ordered_languages
    ]


def _add_matching_languages(available_languages, ordered_languages, preferred_language, exact):
    preferred = preferred_language.lower()
    preferred_prefix = preferred.split('-', 1)[0]

    for language in available_languages:
        normalized_language = language.lower()
        matches = normalized_language == preferred
        if not exact:
            matches = normalized_language.split('-', 1)[0] == preferred_prefix
        if matches and language not in ordered_languages:
            ordered_languages.append(language)


def _seleciona_formato_legenda(captions):
    for extension in CAPTION_FORMAT_PRIORITY:
        for caption in captions:
            if caption.get('url') and (caption.get('ext') or '').lower() == extension:
                return caption

    for caption in captions:
        if caption.get('url'):
            return caption

    return None


def _mensagem_erro_video(errors):
    errors = [error for error in errors if error]
    details = ' | '.join(errors)

    if _is_browser_cookie_database_locked(details):
        return _adiciona_detalhe_download_audio(YOUTUBE_COOKIE_DATABASE_HINT, details)
    if _is_invalid_cookie_file(details):
        return _adiciona_detalhe_download_audio(YOUTUBE_INVALID_COOKIES_FILE_HINT, details)
    if _is_youtube_rate_limit(details):
        return _adiciona_detalhe_download_audio(YOUTUBE_RATE_LIMIT_HINT, details)

    if details:
        return f'Não foi possível extrair conteúdo desse vídeo. Detalhes: {details}'
    return 'Não foi possível extrair conteúdo desse vídeo.'


def _adiciona_detalhe_download_audio(message, details):
    if _is_audio_download_failure(details):
        return f'{message} {YOUTUBE_AUDIO_DOWNLOAD_HINT}'
    return message


def _deve_tentar_sem_cookies_do_navegador(message):
    return (
        bool(_cookies_from_browser())
        and not os.getenv(YOUTUBE_COOKIES_FILE_ENV, '').strip()
        and _is_browser_cookie_database_locked(message)
    )


def _is_audio_download_failure(message):
    lowered_message = message.lower()
    return (
        'não foi possível baixar o áudio do vídeo' in lowered_message
        or 'yt-dlp não gerou arquivo de áudio' in lowered_message
    )


def _is_youtube_rate_limit(message):
    lowered_message = message.lower()
    return '429' in lowered_message or 'too many requests' in lowered_message


def _is_browser_cookie_database_locked(message):
    lowered_message = message.lower()
    return (
        (
            'could not copy' in lowered_message
            and 'cookie database' in lowered_message
        )
        or 'failed to decrypt with dpapi' in lowered_message
    )


def _is_invalid_cookie_file(message):
    return 'does not look like a netscape format cookies file' in message.lower()


def _extrai_texto_legenda(content, extension):
    extension = (extension or '').lower()

    if extension == 'json3':
        return _extrai_texto_json3(content)
    if extension in {'srv3', 'ttml', 'xml'}:
        return _extrai_texto_xml(content)
    return _extrai_texto_vtt(content)


def _extrai_texto_json3(content):
    try:
        data = json.loads(content)
    except json.JSONDecodeError:
        return ''

    caption_parts = []
    for event in data.get('events', []):
        segments = event.get('segs') or []
        caption_parts.append(''.join(segment.get('utf8', '') for segment in segments))

    return _normaliza_texto(caption_parts)


def _extrai_texto_xml(content):
    try:
        root = ElementTree.fromstring(content)
    except ElementTree.ParseError:
        return ''

    caption_parts = []
    for node in root.iter():
        tag = node.tag.rsplit('}', 1)[-1]
        if tag in {'p', 'text'}:
            caption_parts.append(''.join(node.itertext()))

    return _normaliza_texto(caption_parts)


def _extrai_texto_vtt(content):
    caption_parts = []
    for line in content.splitlines():
        line = line.strip()
        if _ignora_linha_vtt(line):
            continue
        line = re.sub(r'<[^>]+>', '', line)
        caption_parts.append(line)

    return _normaliza_texto(caption_parts)


def _ignora_linha_vtt(line):
    return (
        not line
        or line == 'WEBVTT'
        or line.startswith(('Kind:', 'Language:', 'NOTE', 'STYLE'))
        or '-->' in line
        or bool(re.fullmatch(r'\d+', line))
    )


def _normaliza_texto(text_parts):
    normalized_parts = []
    previous_part = ''

    for text_part in text_parts:
        text = re.sub(r'\s+', ' ', html.unescape(str(text_part))).strip()
        if text and text != previous_part:
            normalized_parts.append(text)
            previous_part = text

    return ' '.join(normalized_parts)
