from rest_framework.serializers import ValidationError
from urllib.parse import urlparse


class YouTubeLinkValidator:

    allowed_domains = ["youtube.com", "www.youtube.com", "m.youtube.com"]

    def __init__(self, field):
        self.field = field

    def __call__(self, value):
        url = value.get(self.field)

        if not url:
            return

        parsed_url = urlparse(url)
        domain = parsed_url.netloc.lower()

        if domain not in self.allowed_domains:
            raise ValidationError(
                f"Ссылка должна вести только на YouTube. "
                f"Домен «{domain}» не разрешён."
            )
