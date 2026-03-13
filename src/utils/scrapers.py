import requests
from bs4 import BeautifulSoup
from youtube_transcript_api import YouTubeTranscriptApi

def carrega_site(url_site):
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url_site, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        for script in soup(["script", "style"]):
            script.decompose()
            
        texto = soup.get_text(separator=' ')
        lines = (line.strip() for line in texto.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        return '\n'.join(chunk for chunk in chunks if chunk)
        
    except Exception as e:
        print(f'Erro ao carregar o site: {e}')
        return ''

def carrega_video(url_video):
    try:
        video_id = None
        if "v=" in url_video:
            video_id = url_video.split("v=")[1].split("&")[0]
        elif "youtu.be" in url_video:
            video_id = url_video.split("/")[-1]
        
        if not video_id:
            return "ID do vídeo não encontrado."

        api = YouTubeTranscriptApi()
        transcript_list = api.fetch(video_id, languages=['pt', 'en'])
        
        textos = []
        for t in transcript_list:
            if isinstance(t, dict) and 'text' in t:
                textos.append(t['text'])
            elif hasattr(t, 'text'):
                textos.append(t.text)
                
        return " ".join(textos)
        
    except Exception as e:
        print(f'Erro ao carregar o vídeo: {e}')
        return ''
