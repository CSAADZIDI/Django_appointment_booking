from django import forms
from django.contrib.auth.forms import UserCreationForm
from datetime import datetime, timedelta, time as time_obj
from django.forms.widgets import DateTimeInput

from .models import Session, TimeSlot, CustomUser


# ─────────────────────────────────────────────
# User sign‑up form (unchanged)
# ─────────────────────────────────────────────
class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ("username", "email")


# ─────────────────────────────────────────────
# New Session booking form  ← key change
# ─────────────────────────────────────────────
class SessionForm(forms.Form):
    """
    Users type / pick a free‑text datetime (Flatpickr); we validate it
    and map it to a TimeSlot instance. No changes to models.py needed.
    """
    timeslot = forms.DateTimeField(
        label="Date & time",
        widget=DateTimeInput(
            attrs={
                "id": "id_timeslot_picker",   # Flatpickr hooks here
                "class": "form-input",
                "placeholder": "Select date and time",
            }
        ),
    )
    subject = forms.CharField(
        label="Subject",
        max_length=120,
        widget=forms.TextInput(attrs={"class": "form-input"}),
    )

    # ── validation ───────────────────────────
    def clean_timeslot(self):
        picked_dt = self.cleaned_data["timeslot"]

        # 1) must be within working hours
        start_ok, end_ok = time_obj(9, 0), time_obj(18, 0)
        if picked_dt.time() < start_ok or picked_dt.time() >= end_ok:
            raise forms.ValidationError(
                "Appointments must be between 09:00 and 18:00."
            )

        # 2) must match an existing TimeSlot row
        try:
            slot = TimeSlot.objects.get(
                date=picked_dt.date(), start_time=picked_dt.time()
            )
        except TimeSlot.DoesNotExist:
            raise forms.ValidationError("This time is not offered by the coach.")

        # 3) must still be free
        if not slot.is_available:
            raise forms.ValidationError("That slot was just booked. Please pick another.")

        # 4) 10‑minute buffer around other sessions
        buffer_before = picked_dt - timedelta(minutes=10)
        buffer_after = picked_dt + timedelta(minutes=10)
        overlapping = (
            Session.objects.filter(timeslot__date=picked_dt.date())
            .exclude(timeslot__start_time=picked_dt.time())
        )
        for sess in overlapping:
            sess_dt = datetime.combine(sess.timeslot.date, sess.timeslot.start_time)
            if buffer_before <= sess_dt <= buffer_after:
                raise forms.ValidationError(
                    "There must be at least 10 minutes between sessions."
                )

        # stash for use in save()
        self._validated_slot = slot
        return picked_dt

    # ── creator ──────────────────────────────
    def save(self, *, client):
        """
        Creates Session and flips TimeSlot.is_available → False.
        Call only after is_valid().
        """
        slot = self._validated_slot
        session = Session.objects.create(
            client=client,
            timeslot=slot,
            subject=self.cleaned_data["subject"],
        )
        slot.is_available = False
        slot.save()
        return session


# ─────────────────────────────────────────────
# Other helper forms (unchanged)
# ─────────────────────────────────────────────
class DateSelectionForm(forms.Form):
    date = forms.DateField(
        widget=forms.DateInput(attrs={"type": "date", "class": "form-control"}),
        label="Choisir une date",
    )


class CoachNotesForm(forms.ModelForm):
    class Meta:
        model = Session
        fields = ["notes_coach"]
        widgets = {"notes_coach": forms.Textarea(attrs={"rows": 4, "cols": 40})}
