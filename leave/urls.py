from django.urls import path
from . import views
urlpatterns=[path('',views.my_leaves,name='my_leaves'),path('nowy/',views.new_leave,name='new_leave'),path('do-akceptacji/',views.leaves_to_approve,name='leaves_to_approve'),path('akceptuj/<int:leave_id>/',views.approve_leave,name='approve_leave'),path('odrzuc/<int:leave_id>/',views.reject_leave,name='reject_leave')]
