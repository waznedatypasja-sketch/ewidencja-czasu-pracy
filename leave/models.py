from django.db import models
from django.contrib.auth.models import User

class LeaveType(models.TextChoices):
    WYPOCZYNKOWY="WYPOCZYNKOWY","Urlop wypoczynkowy"
    NA_ZADANIE="NA_ZADANIE","Urlop na żądanie"
    BEZPLATNY="BEZPLATNY","Urlop bezpłatny"
    CHOROBOWE="CHOROBOWE","Chorobowe (L4)"
    INNE="INNE","Inne"

class LeaveStatus(models.TextChoices):
    SUBMITTED="SUBMITTED","Wysłany"
    APPROVED="APPROVED","Zaakceptowany"
    REJECTED="REJECTED","Odrzucony"

class LeaveRequest(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE,related_name="leave_requests")
    leave_type=models.CharField(max_length=20,choices=LeaveType.choices)
    start_date=models.DateField()
    end_date=models.DateField()
    half_day=models.BooleanField(default=False)
    comment=models.TextField(blank=True,default="")
    attachment=models.FileField(upload_to="zalaczniki_urlopy/",blank=True,null=True)
    status=models.CharField(max_length=12,choices=LeaveStatus.choices,default=LeaveStatus.SUBMITTED)
    submitted_at=models.DateTimeField(auto_now_add=True)
    decided_at=models.DateTimeField(null=True,blank=True)
    decided_by=models.ForeignKey(User,on_delete=models.SET_NULL,null=True,blank=True,related_name="decided_leaves")
    manager_note=models.TextField(blank=True,default="")
    class Meta:
        ordering=["-submitted_at"]
