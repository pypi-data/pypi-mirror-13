from .choices import CURRENCY_CHOICES, CURRENCY_LABELS, TIMEZONE_CHOICES


def base(request):
    return {
        'CURRENCY_CHOICES': CURRENCY_CHOICES,
        'CURRENCY_LABELS': CURRENCY_LABELS,
        'TIMEZONE_CHOICES': TIMEZONE_CHOICES
    }
