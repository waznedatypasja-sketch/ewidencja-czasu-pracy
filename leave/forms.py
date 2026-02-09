from django import forms
from .models import LeaveRequest

class LeaveRequestForm(forms.ModelForm):
    class Meta:
        model=LeaveRequest
        fields=["leave_type","start_date","end_date","half_day","comment","attachment"]
        widgets={
            "leave_type":forms.Select(attrs={"class":"form-select"}),
            "start_date":forms.DateInput(attrs={"type":"date","class":"form-control"}),
            "end_date":forms.DateInput(attrs={"type":"date","class":"form-control"}),
            "half_day":forms.CheckboxInput(attrs={"class":"form-check-input"}),
            "comment":forms.Textarea(attrs={"class":"form-control","rows":3}),
        }
    def clean(self):
        c=super().clean()
        sd,ed=c.get("start_date"),c.get("end_date")
        if sd and ed and ed<sd:
            self.add_error("end_date","Data końcowa nie może być wcześniejsza niż początkowa.")
        return c
