import html
import json
import logging
import os
import re
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
    'O yt-dlp não conseguiu copiar o banco de cookies do navegador. Feche '
    'totalmente o Chrome/Edge, inclusive processos em segundo plano, ou use '
    'CITYBOT_YOUTUBE_COOKIES_FILE apontando para um arquivo cookies.txt.'
)
YOUTUBE_INVALID_COOKIES_FILE_HINT = (
    'O arquivo configurado em CITYBOT_YOUTUBE_COOKIES_FILE não está no formato '
    'Netscape cookies.txt aceito pelo yt-dlp. Exporte os cookies novamente nesse '
    'formato; arquivos JSON, HTML ou SQLite do navegador não funcionam.'
)


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

    try:
        with YoutubeDL(_yt_dlp_options()) as ydl:
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


def _yt_dlp_options():
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

    cookies_from_browser = _cookies_from_browser()
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
        return YOUTUBE_COOKIE_DATABASE_HINT
    if _is_invalid_cookie_file(details):
        return YOUTUBE_INVALID_COOKIES_FILE_HINT
    if _is_youtube_rate_limit(details):
        return YOUTUBE_RATE_LIMIT_HINT

    if details:
        return f'Não foi possível extrair conteúdo desse vídeo. Detalhes: {details}'
    return 'Não foi possível extrair conteúdo desse vídeo.'


def _is_youtube_rate_limit(message):
    lowered_message = message.lower()
    return '429' in lowered_message or 'too many requests' in lowered_message


def _is_browser_cookie_database_locked(message):
    lowered_message = message.lower()
    return (
        'could not copy' in lowered_message
        and 'cookie database' in lowered_message
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
