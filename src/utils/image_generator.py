import base64
import binascii
import os
import re
import unicodedata
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

import openai
from dotenv import load_dotenv
from openai import OpenAI

from src.utils.paths import PROJECT_ROOT


OPENAI_API_KEY_ENV = 'OPENAI_API_KEY'
IMAGE_API_KEY_ENV = 'CITYBOT_IMAGE_API_KEY'
IMAGE_BASE_URL_ENV = 'CITYBOT_IMAGE_BASE_URL'
IMAGE_AZURE_SCOPE_ENV = 'CITYBOT_IMAGE_AZURE_SCOPE'
IMAGE_MODEL_ENV = 'CITYBOT_IMAGE_MODEL'
DEFAULT_IMAGE_MODEL = 'gpt-image-2'
DEFAULT_IMAGE_AZURE_SCOPE = 'https://ai.azure.com/.default'
DEFAULT_IMAGE_SIZE = '1536x1024'
DEFAULT_IMAGE_QUALITY = 'medium'
DEFAULT_IMAGE_FORMAT = 'png'
DEFAULT_IMAGE_OUTPUT_DIR = PROJECT_ROOT / 'imagens'

SUPPORTED_IMAGE_QUALITIES = ('low', 'medium', 'high', 'auto')
SUPPORTED_IMAGE_FORMATS = ('png', 'jpeg', 'webp')


@dataclass(frozen=True)
class GeneratedImage:
    path: Path
    prompt: str
    model: str
    size: str
    quality: str
    output_format: str


def generate_image(
    prompt,
    size=DEFAULT_IMAGE_SIZE,
    quality=DEFAULT_IMAGE_QUALITY,
    output_format=DEFAULT_IMAGE_FORMAT,
    output_dir=None,
    client=None,
):
    load_dotenv()
    clean_prompt = str(prompt or '').strip()
    if not clean_prompt:
        raise ValueError('Informe um prompt para gerar a imagem.')

    model = os.getenv(IMAGE_MODEL_ENV, DEFAULT_IMAGE_MODEL).strip() or DEFAULT_IMAGE_MODEL
    size = _validate_size(size)
    quality = _validate_choice(quality, SUPPORTED_IMAGE_QUALITIES, 'qualidade')
    output_format = _validate_choice(output_format, SUPPORTED_IMAGE_FORMATS, 'formato')

    if client is None:
        client = _build_openai_client()

    try:
        result = client.images.generate(
            model=model,
            prompt=clean_prompt,
            n=1,
            size=size,
            quality=quality,
            output_format=output_format,
            moderation='auto',
        )
    except openai.AuthenticationError as error:
        raise RuntimeError(_authentication_error_message()) from error
    except openai.BadRequestError as error:
        raise RuntimeError(_bad_request_message(error)) from error
    except openai.OpenAIError as error:
        raise RuntimeError(f'Erro na API de imagens da OpenAI: {error}') from error

    image_base64 = _first_image_base64(result)
    image_bytes = _decode_base64_image(image_base64)
    target_path = _unique_output_path(output_dir or DEFAULT_IMAGE_OUTPUT_DIR, clean_prompt, output_format)
    target_path.write_bytes(image_bytes)

    return GeneratedImage(
        path=target_path,
        prompt=clean_prompt,
        model=model,
        size=size,
        quality=quality,
        output_format=output_format,
    )


def _validate_size(size):
    value = str(size or DEFAULT_IMAGE_SIZE).strip().lower()
    if value == 'auto':
        return value

    match = re.fullmatch(r'(\d{3,4})x(\d{3,4})', value)
    if not match:
        raise ValueError('Tamanho inválido. Use auto ou WIDTHxHEIGHT, como 1536x1024.')

    width, height = (int(match.group(1)), int(match.group(2)))
    long_edge = max(width, height)
    short_edge = min(width, height)
    total_pixels = width * height

    if long_edge > 3840:
        raise ValueError('Tamanho inválido. O maior lado deve ter no máximo 3840px.')
    if width % 16 or height % 16:
        raise ValueError('Tamanho inválido. Largura e altura devem ser múltiplos de 16.')
    if long_edge / short_edge > 3:
        raise ValueError('Tamanho inválido. A proporção não pode passar de 3:1.')
    if not 655_360 <= total_pixels <= 8_294_400:
        raise ValueError('Tamanho inválido. Use entre 655.360 e 8.294.400 pixels no total.')

    return value


def _build_openai_client():
    base_url = os.getenv(IMAGE_BASE_URL_ENV, '').strip()
    if base_url:
        api_key = os.getenv(IMAGE_API_KEY_ENV, '').strip()
        if api_key:
            return OpenAI(base_url=base_url, api_key=api_key)
        return OpenAI(
            base_url=base_url,
            api_key=_azure_token_provider(),
        )

    api_key = os.getenv(OPENAI_API_KEY_ENV)
    if not api_key:
        raise ValueError(
            f'Configure {OPENAI_API_KEY_ENV} ou {IMAGE_BASE_URL_ENV} para gerar imagens.'
        )
    return OpenAI(api_key=api_key)


def _azure_token_provider():
    try:
        from azure.identity import DefaultAzureCredential, get_bearer_token_provider
    except ImportError as error:
        raise ValueError(
            'Para gerar imagens via Azure AI Foundry, instale a dependência opcional '
            'azure-identity e configure CITYBOT_IMAGE_BASE_URL.'
        ) from error

    scope = os.getenv(IMAGE_AZURE_SCOPE_ENV, DEFAULT_IMAGE_AZURE_SCOPE).strip()
    return get_bearer_token_provider(DefaultAzureCredential(), scope)


def _validate_choice(value, allowed_values, label):
    clean_value = str(value or '').strip().lower()
    if clean_value in allowed_values:
        return clean_value
    allowed = ', '.join(allowed_values)
    raise ValueError(f'{label.capitalize()} inválido. Use um destes valores: {allowed}.')


def _first_image_base64(result):
    data = getattr(result, 'data', None) or []
    if not data:
        raise RuntimeError('A API de imagens não retornou nenhum resultado.')

    image_base64 = getattr(data[0], 'b64_json', '') or ''
    if not image_base64:
        raise RuntimeError('A API de imagens não retornou conteúdo em base64.')
    return image_base64


def _decode_base64_image(image_base64):
    try:
        return base64.b64decode(image_base64)
    except (binascii.Error, ValueError) as error:
        raise RuntimeError('A API retornou uma imagem em base64 inválida.') from error


def _unique_output_path(output_dir, prompt, output_format):
    target_dir = Path(output_dir)
    target_dir.mkdir(parents=True, exist_ok=True)

    extension = 'jpg' if output_format == 'jpeg' else output_format
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    slug = _slugify(prompt)
    output_path = target_dir / f'{timestamp}_{slug}.{extension}'
    counter = 2
    while output_path.exists():
        output_path = target_dir / f'{timestamp}_{slug}_{counter}.{extension}'
        counter += 1
    return output_path


def _slugify(value):
    normalized = unicodedata.normalize('NFKD', value)
    ascii_text = normalized.encode('ascii', 'ignore').decode('ascii')
    slug = re.sub(r'[^a-zA-Z0-9]+', '_', ascii_text).strip('_').lower()
    return (slug or 'imagem')[:48]


def _bad_request_message(error):
    code = getattr(error, 'code', '')
    if code == 'moderation_blocked':
        return (
            'A geração foi bloqueada pelas regras de segurança da OpenAI. '
            'Tente reescrever o prompt com foco em detalhes visuais neutros.'
        )
    return f'Erro ao gerar imagem com gpt-image-2: {error}'


def _authentication_error_message():
    base_url = os.getenv(IMAGE_BASE_URL_ENV, '').strip()
    if base_url:
        return (
            'Falha de autenticação no endpoint de imagens configurado. '
            f'Verifique se {IMAGE_API_KEY_ENV} é uma chave válida desse recurso ou, '
            f'se estiver usando login Azure, se o DefaultAzureCredential tem acesso ao deployment gpt-image-2.'
        )

    return (
        'Falha de autenticação na API pública da OpenAI. '
        f'Se você quer usar Azure AI Foundry, configure {IMAGE_BASE_URL_ENV} com o endpoint '
        f'no formato https://seu-recurso.services.ai.azure.com/openai/v1. '
        f'Use {IMAGE_API_KEY_ENV} para uma chave desse recurso ou deixe sem essa variável '
        f'para usar DefaultAzureCredential. Use {OPENAI_API_KEY_ENV} somente com chave da OpenAI pública.'
    )
