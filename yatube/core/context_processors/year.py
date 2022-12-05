from django.utils import timezone


def year(*args):
    """Добавляет переменную с текущим годом."""
    return {
        'year': timezone.now().year
    }
