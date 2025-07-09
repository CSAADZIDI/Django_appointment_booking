from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Session, TimeSlot, CustomUser
from datetime import datetime, timedelta, time
from django.forms.widgets import DateTimeInput

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ('username','email')  # add other fields if you want


class SessionForm(forms.ModelForm):
    class Meta:
        model = Session
        fields = ['timeslot', 'subject']
        widgets = {
            'timeslot': DateTimeInput(
                attrs={
                    'id': 'id_timeslot_picker',
                    'class': 'form-input',
                    'placeholder': 'Select date and time'
                }
            ),
            'subject': forms.TextInput(attrs={'class': 'form-input'})
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Let the user manually pick any future datetime;
        # availability logic is handled in `clean_timeslot`
        self.fields['timeslot'].required = True

    def clean_timeslot(self):
        timeslot = self.cleaned_data.get('timeslot')
        if not timeslot:
            raise forms.ValidationError("You must select a valid timeslot.")

        # Validate it's within working hours
        start_allowed = time(9, 0)
        end_allowed = time(18, 0)
        if timeslot.time() < start_allowed or timeslot.time() >= end_allowed:
            raise forms.ValidationError("Appointments must be between 09:00 and 18:00.")

        # Prevent using unavailable times
        # You match this datetime to a Timeslot object
        try:
            slot = TimeSlot.objects.get(date=timeslot.date(), start_time=timeslot.time())
        except TimeSlot.DoesNotExist:
            raise forms.ValidationError("Selected time is not available.")

        if not slot.is_available:
            raise forms.ValidationError("This timeslot is already booked.")

        # Enforce a 10-minute gap with other sessions
        requested_start = timeslot
        buffer_before = requested_start - timedelta(minutes=10)
        buffer_after = requested_start + timedelta(minutes=10)

        overlapping = Session.objects.filter(
            timeslot__date=timeslot.date()
        ).exclude(
            timeslot__start_time=timeslot.time()
        )

        for session in overlapping:
            start_dt = datetime.combine(session.timeslot.date, session.timeslot.start_time)
            if buffer_before <= start_dt <= buffer_after:
                raise forms.ValidationError("There must be at least 10 minutes between sessions.")

        return timeslot

    def save(self, commit=True):
        session = super().save(commit=False)
        # Match the datetime with the actual TimeSlot object
        timeslot = TimeSlot.objects.get(date=session.timeslot.date(), start_time=session.timeslot.time())
        timeslot.is_available = False
        timeslot.save()
        session.timeslot = timeslot
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