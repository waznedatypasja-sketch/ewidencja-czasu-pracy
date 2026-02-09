from django.contrib import admin
from .models import Project, TimeEntry, WorkSession

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display=("name","code","active")
    list_filter=("active",)
    search_fields=("name","code")

@admin.register(TimeEntry)
class TimeEntryAdmin(admin.ModelAdmin):
    list_display=("user","date","source","status","project")
    list_filter=("status","source","project")
    search_fields=("user__username","user__first_name","user__last_name","comment")

@admin.register(WorkSession)
class WorkSessionAdmin(admin.ModelAdmin):
    list_display=("user","date","start_dt","break_minutes","project")
