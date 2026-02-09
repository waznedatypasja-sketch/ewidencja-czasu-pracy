from django.db import models
from django.contrib.auth.models import User

class EntrySource(models.TextChoices):
    RCP="RCP","RCP (START/STOP)"
    MANUAL="MANUAL","Wpis ręczny"

class EntryStatus(models.TextChoices):
    DRAFT="DRAFT","Szkic"
    SUBMITTED="SUBMITTED","Wysłane do akceptacji"
    APPROVED="APPROVED","Zaakceptowane"
    REJECTED="REJECTED","Odrzucone"

class Project(models.Model):
    name=models.CharField(max_length=200)
    code=models.CharField(max_length=50,blank=True,default="")
    active=models.BooleanField(default=True)
    def __str__(self):
        return f"{self.code + ' - ' if self.code else ''}{self.name}"

class TimeEntry(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE,related_name="time_entries")
    date=models.DateField()
    start_time=models.TimeField(null=True,blank=True)
    end_time=models.TimeField(null=True,blank=True)
    break_minutes=models.PositiveIntegerField(default=0)
    source=models.CharField(max_length=10,choices=EntrySource.choices,default=EntrySource.RCP)
    project=models.ForeignKey(Project,on_delete=models.SET_NULL,null=True,blank=True)
    comment=models.TextField()
    manual_reason=models.CharField(max_length=255,blank=True,default="")
    status=models.CharField(max_length=12,choices=EntryStatus.choices,default=EntryStatus.DRAFT)
    submitted_at=models.DateTimeField(null=True,blank=True)
    approved_at=models.DateTimeField(null=True,blank=True)
    approved_by=models.ForeignKey(User,on_delete=models.SET_NULL,null=True,blank=True,related_name="approved_entries")
    manager_note=models.TextField(blank=True,default="")
    created_at=models.DateTimeField(auto_now_add=True)
    class Meta:
        unique_together=("user","date")
        ordering=["-date","-created_at"]

class WorkSession(models.Model):
    user=models.OneToOneField(User,on_delete=models.CASCADE,related_name="work_session")
    date=models.DateField()
    start_dt=models.DateTimeField()
    break_start_dt=models.DateTimeField(null=True,blank=True)
    break_minutes=models.PositiveIntegerField(default=0)
    project=models.ForeignKey(Project,on_delete=models.SET_NULL,null=True,blank=True)
    comment=models.TextField(blank=True,default="")
