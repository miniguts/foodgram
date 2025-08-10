import base64
import uuid
from io import BytesIO

from django.core.files.base import ContentFile
from PIL import Image
from rest_framework import serializers


class Base64ImageField(serializers.ImageField):

    def to_internal_value(self, data):
        if not isinstance(data, str):
            raise serializers.ValidationError(
                "Аватар должен быть строкой в формате base64."
            )

        if not data.startswith("data:image"):
            raise serializers.ValidationError(
                "Ожидалась base64-строка изображения с префиксом data:image/."
            )

        try:
            format_info, img_str = data.split(";base64,")
            ext = format_info.split("/")[-1].lower()
            decoded_file = base64.b64decode(img_str)
        except (ValueError, TypeError, base64.binascii.Error):
            raise serializers.ValidationError(
                "Ошибка декодирования изображения."
            )

        try:
            image = Image.open(BytesIO(decoded_file))
            file_ext = image.format.lower()
        except Exception:
            raise serializers.ValidationError(
                "Файл не является допустимым изображением."
            )

        if ext == "jpg":
            ext = "jpeg"
        if file_ext == "jpg":
            file_ext = "jpeg"

        allowed_formats = {"jpeg", "png"}
        if ext not in allowed_formats:
            raise serializers.ValidationError(
                f'Недопустимый формат: {ext}. '
                f'Разрешены только: {", ".join(allowed_formats)}.'
            )

        if file_ext not in allowed_formats:
            raise serializers.ValidationError(
                f"Недопустимый определённый формат файла: {file_ext}. "
                f'Разрешены только: {", ".join(allowed_formats)}.'
            )

        if file_ext != ext:
            raise serializers.ValidationError(
                f"Формат не совпадает: ожидался {ext}, получен {file_ext}."
            )

        if ext == "jpeg" and "jpg" in format_info:
            save_ext = "jpg"
        else:
            save_ext = ext

        file_name = f"{uuid.uuid4()}.{save_ext}"
        data = ContentFile(decoded_file, name=file_name)

        return super().to_internal_value(data)
