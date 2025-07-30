from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser
from .aes_utils import encrypt_data, decrypt_data
from io import BytesIO

class AESJSONRenderer(JSONRenderer):
    def render(self, data, accepted_media_type=None, renderer_context=None):
        encrypted = encrypt_data(data)
        return super().render({'data': encrypted}, accepted_media_type, renderer_context)

class AESJSONParser(JSONParser):
    def parse(self, stream, media_type=None, parser_context=None):
        raw = super().parse(stream, media_type=media_type, parser_context=parser_context)
        if 'data' in raw:
            return decrypt_data(raw['data'])
        return raw 