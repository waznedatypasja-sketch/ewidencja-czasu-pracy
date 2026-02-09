from django.contrib import admin
from .models import LeaveRequest
@admin.register(LeaveRequest)
class LeaveAdmin(admin.ModelAdmin):
    list_display=('user','leave_type','start_date','end_date','status')
    list_filter=('leave_type','status')
