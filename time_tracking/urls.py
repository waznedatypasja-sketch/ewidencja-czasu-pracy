from django.urls import path
from . import views

urlpatterns = [
    path('', views.my_entries, name='my_entries'),
    path('dzis/', views.today, name='today'),
    path('rcp/start/', views.rcp_start, name='rcp_start'),
    path('rcp/przerwa/', views.rcp_break_toggle, name='rcp_break_toggle'),
    path('rcp/stop/', views.rcp_stop, name='rcp_stop'),
    path('wpis-reczny/', views.manual_entry, name='manual_entry'),
    path('wyslij/<int:entry_id>/', views.submit_entry, name='submit_entry'),
    path('usun/<int:entry_id>/', views.delete_draft, name='delete_draft'),
    path('do-akceptacji/', views.to_approve, name='to_approve'),
    path('akceptuj/<int:entry_id>/', views.approve_entry, name='approve_entry'),
    path('odrzuc/<int:entry_id>/', views.reject_entry, name='reject_entry'),
]
