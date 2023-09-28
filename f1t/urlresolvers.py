from django.conf import settings
from django.urls import LocalePrefixPattern, URLResolver
from django.utils.translation import get_language


def solid_i18n_patterns(*urls, prefix_default_language=True):
    """
    Same as i18n_patterns but uses SolidLocalePrefixPattern instead of LocalePrefixPattern
    """
    if not settings.USE_I18N:
        return list(urls)
    return [
        URLResolver(
            SolidLocalePrefixPattern(prefix_default_language=prefix_default_language),
            list(urls),
        )
    ]


class SolidLocalePrefixPattern(LocalePrefixPattern):
    """
    Based on django-solid-i18n-urls.
    """

    @property
    def language_prefix(self):
        language_code = get_language() or settings.LANGUAGE_CODE
        if language_code == settings.LANGUAGE_CODE:
            return ""
        else:
            return "%s/" % language_code
