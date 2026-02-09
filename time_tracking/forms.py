from django import forms
from .models import TimeEntry

class ManualEntryForm(forms.ModelForm):
    class Meta:
        model=TimeEntry
        fields=["date","start_time","end_time","break_minutes","project","comment","manual_reason"]
        widgets={
            "date":forms.DateInput(attrs={"type":"date","class":"form-control"}),
            "start_time":forms.TimeInput(attrs={"type":"time","class":"form-control"}),
            "end_time":forms.TimeInput(attrs={"type":"time","class":"form-control"}),
            "break_minutes":forms.NumberInput(attrs={"class":"form-control","min":0}),
            "project":forms.Select(attrs={"class":"form-select"}),
            "comment":forms.Textarea(attrs={"class":"form-control","rows":3,"placeholder":"Nad czym dziś pracowałeś/aś?"}),
            "manual_reason":forms.TextInput(attrs={"class":"form-control","placeholder":"Powód wpisu ręcznego (wymagany)"}),
        }
    def clean(self):
        c=super().clean()
        st,et=c.get("start_time"),c.get("end_time")
        if not (c.get("manual_reason") or "").strip():
            self.add_error("manual_reason","Podaj powód wpisu ręcznego.")
        if st and et and et<=st:
            self.add_error("end_time","Godzina zakończenia musi być po rozpoczęciu.")
        return c
