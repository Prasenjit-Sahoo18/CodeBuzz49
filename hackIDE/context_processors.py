from django.utils import timezone

def current_time(request):
    """Add current time to template context"""
    return {
        'now': timezone.now()
    }
