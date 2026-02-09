from django.urls import path
from . import views
urlpatterns=[path('logowanie/',views.login_view,name='login'),path('wyloguj/',views.logout_view,name='logout'),path('profil/',views.profile_view,name='profile')]
