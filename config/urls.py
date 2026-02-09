from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
    path('konto/', include('accounts.urls')),
    path('czas/', include('time_tracking.urls')),
    path('urlopy/', include('leave.urls')),
    path('wyplaty/', include('payroll.urls')),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
