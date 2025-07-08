from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Session, TimeSlot, CustomUser
from datetime import datetime, timedelta, time

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ('username','email')  # add other fields if you want


class SessionForm(forms.ModelForm):
    class Meta:
        model = Session
        fields = ['timeslot', 'subject']
        widgets = {
            'timeslot': forms.Select(),
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    # Filter TimeSlots to only show available ones in the future
        self.fields['timeslot'].queryset = TimeSlot.objects.filter(
        is_available=True,
        date__gte=datetime.today().date()
    )
    def clean_timeslot(self):
        timeslot = self.cleaned_data.get('timeslot')

        # Validate time range
        start_allowed = time(9, 0)
        end_allowed = time(18, 0)
        if timeslot.start_time < start_allowed or timeslot.start_time >= end_allowed:
            raise forms.ValidationError("Appointments must be between 09:00 and 18:00.")

        if not timeslot.is_available:
            raise forms.ValidationError("This time slot is already booked.")

        # Check 10 minutes gap rule
        # Compute datetime for this timeslot start and end
        timeslot_start_dt = datetime.combine(timeslot.date, timeslot.start_time)
        buffer_before = timeslot_start_dt - timedelta(minutes=10)
        buffer_after = timeslot_start_dt + timedelta(minutes=10)

        # Fetch all sessions on the same day (excluding current timeslot)
        overlapping_sessions = Session.objects.filter(
            timeslot__date=timeslot.date
        ).exclude(
            timeslot=timeslot
        )

        for session in overlapping_sessions:
            session_start_dt = datetime.combine(session.timeslot.date, session.timeslot.start_time)

            # If session is within 10 minutes before or after the requested timeslot, raise error
            if (buffer_before <= session_start_dt <= buffer_after):
                raise forms.ValidationError(
                    "There must be at least 10 minutes between sessions."
                )

        return timeslot


    def save(self, commit=True):
        session = super().save(commit=False)
        # Mark the timeslot as no longer available
        session.timeslot.is_available = False
        session.timeslot.save()
        if commit:
            session.save()
        return session


class DateSelectionForm(forms.Form):
    date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        label="Choisir une date"
    )
    
    
class CoachNotesForm(forms.ModelForm):
    class Meta:
        model = Session
        fields = ['notes_coach']
        widgets = {
            'notes_coach': forms.Textarea(attrs={'rows': 4, 'cols': 40}),
        }