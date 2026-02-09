from django.db import models
from django.contrib.auth.models import User

class Role(models.TextChoices):
    PRACOWNIK="PRACOWNIK","Pracownik"
    PRZELOZONY="PRZELOZONY","Przełożony"
    ADMIN="ADMIN","Admin"

class Profile(models.Model):
    user=models.OneToOneField(User,on_delete=models.CASCADE,related_name="profile")
    role=models.CharField(max_length=20,choices=Role.choices,default=Role.PRACOWNIK)
    supervisor=models.ForeignKey(User,on_delete=models.SET_NULL,null=True,blank=True,related_name="team_members")
    hourly_rate_pln=models.DecimalField(max_digits=8,decimal_places=2,default=0)
    overtime_multiplier=models.DecimalField(max_digits=4,decimal_places=2,default=1.50)
    def __str__(self):
        return f"{self.user.username} ({self.get_role_display()})"
