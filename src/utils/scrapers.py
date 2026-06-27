import logging
from urllib.parse import parse_qs, urlparse

import truststore

truststore.inject_into_ssl()

import requests
from bs4 import BeautifulSoup
from youtube_transcript_api import YouTubeTranscriptApi


logger = logging.getLogger(__name__)
REQUEST_TIMEOUT_SECONDS = 15


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
    try:
        video_id = _extrai_video_id(url_video)
        
        if not video_id:
            logger.warning('ID do vídeo não encontrado na URL informada.')
            return ''

        transcript = YouTubeTranscriptApi().fetch(
            video_id,
            languages=['pt', 'en'],
        )
        
        return ' '.join(
            item.text
            for item in transcript
            if item.text
        )
        
    except Exception as e:
        logger.error('Erro ao carregar o vídeo: %s', e)
        return ''
