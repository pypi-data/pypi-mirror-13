from tracker.models import Tracker


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def track_this(view):
    def tracker(request, *args, **kwargs):
        data = {
            'path': request.path,
            'method': request.method,
            'ip_address': get_client_ip(request),
            'user_agent': request.META['HTTP_USER_AGENT']
        }
        try:
            user = request.user if not request.user.is_anonymous() else None
            Tracker.objects.create(user=user, data=data, path=request.path, user_agent=request.META['HTTP_USER_AGENT'])
        except Exception as e:
            print 'Error ! need a logger here :) %s' % (str(e), )

        return view(request, *args, **kwargs)
    return tracker


# Create your views here.
