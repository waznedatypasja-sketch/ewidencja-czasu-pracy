from django.urls import path
from . import views
urlpatterns=[path('',views.home,name='home'),path('pwa/manifest.json',views.manifest,name='manifest'),path('pwa/sw.js',views.service_worker,name='service_worker')]
