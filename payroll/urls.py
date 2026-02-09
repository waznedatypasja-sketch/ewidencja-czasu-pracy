from django.urls import path
from . import views
urlpatterns=[path('',views.payroll_report,name='payroll_report')]
