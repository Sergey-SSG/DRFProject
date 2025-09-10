from urllib.parse import urlparse

from rest_framework import serializers


def validate_youtube_only(value):
    """Валидатор для проверки, что ссылка ведет только на youtube.com"""
    if value:
        parsed_url = urlparse(value)
        domain = parsed_url.netloc.lower()

        # Разрешаем только youtube.com и youtu.be (короткие ссылки YouTube)
        allowed_domains = ["youtube.com", "www.youtube.com", "youtu.be", "www.youtu.be"]

        if not any(
            domain.endswith(allowed_domain) for allowed_domain in allowed_domains
        ):
            raise serializers.ValidationError(
                "Разрешены только ссылки на YouTube."
                "Пожалуйста, используйте ссылки вида: "
                "https://www.youtube.com/... или https://youtu.be/..."
            )
    return value
