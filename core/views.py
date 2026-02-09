from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render
from django.utils import timezone

@login_required
def home(request):
    return render(request, "core/home.html", {"today": timezone.localdate()})

def manifest(request):
    return JsonResponse({
        "name":"Ewidencja Czasu Pracy",
        "short_name":"CzasPracy",
        "start_url":"/",
        "display":"standalone",
        "background_color":"#ffffff",
        "theme_color":"#0d6efd",
        "icons":[
            {"src":"/static/icons/icon-192.png","sizes":"192x192","type":"image/png"},
            {"src":"/static/icons/icon-512.png","sizes":"512x512","type":"image/png"},
        ]
    })

def service_worker(request):
    js = """
self.addEventListener('install', e => {e.waitUntil(caches.open('v1').then(c=>c.addAll(['/'])));});
self.addEventListener('fetch', e => {e.respondWith(caches.match(e.request).then(r=>r||fetch(e.request)));});
"""
    return HttpResponse(js, content_type="application/javascript")
