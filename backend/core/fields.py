import base64
import imghdr
import uuid

from django.core.files.base import ContentFile
from rest_framework import serializers


class Base64ImageField(serializers.ImageField):
    """
    Поле для обработки изображений, переданных в формате Base64.
    Ожидает строку с префиксом вида 'data:image/<ext>;base64,...'.
    """

    def to_internal_value(self, data):
        if not isinstance(data, str):
            raise serializers.ValidationError(
                'Аватар должен быть строкой в формате base64.'
            )

        if not data.startswith('data:image'):
            raise serializers.ValidationError(
                'Ожидалась base64-строка изображения с префиксом data:image/.'
            )

        try:
            format_info, img_str = data.split(';base64,')
            ext = format_info.split('/')[-1]
            decoded_file = base64.b64decode(img_str)
        except (ValueError, TypeError, base64.binascii.Error):
            raise serializers.ValidationError(
                'Ошибка декодирования изображения.'
            )

        file_ext = imghdr.what(None, decoded_file)
        if not file_ext:
            raise serializers.ValidationError(
                'Недопустимый формат изображения.'
            )

        if file_ext != ext:
            raise serializers.ValidationError(
                f'Формат не совпадает: ожидался {ext}, получен {file_ext}.'
            )

        file_name = f"{uuid.uuid4()}.{ext}"
        data = ContentFile(decoded_file, name=file_name)

        return super().to_internal_value(data)
