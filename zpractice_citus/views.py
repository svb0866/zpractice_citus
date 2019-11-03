from django.shortcuts import render
from sentry_sdk import last_event_id
from django.shortcuts import render


def handler404(request, exception):
    return render(request, '404.html', status=404)


def handler500(request, *args, **argv):
    print("yoyo")
    print(last_event_id())
    return render(request, "500.html", {
        'sentry_event_id': last_event_id(),
    }, status=500)