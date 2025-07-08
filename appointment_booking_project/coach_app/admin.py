from django.contrib import admin
from .models import CustomUser, TimeSlot, Session
from datetime import datetime, timedelta, time
from django import forms
from django.forms.widgets import Select


class LimitedTimeSelect(Select):
    def __init__(self, *args, **kwargs):
        # Generate choices from 09:00 to 18:00 with 30-minute steps
        choices = []
        start = datetime.strptime('09:00', '%H:%M')
        end = datetime.strptime('18:00', '%H:%M')
        delta = timedelta(minutes=30)
        current = start
        while current < end:
            t = current.time()
            choices.append((t.strftime('%H:%M:%S'), t.strftime('%H:%M')))
            current += delta
        kwargs['choices'] = choices
        super().__init__(*args, **kwargs)



# 🔹 Custom form to validate time range in admin manually added TimeSlots
class TimeSlotAdminForm(forms.ModelForm):
    class Meta:
        model = TimeSlot
        fields = '__all__'
        widgets = {
            'start_time': LimitedTimeSelect(),
        }

    def clean_start_time(self):
        start_time = self.cleaned_data['start_time']
        if start_time < time(9, 0) or start_time >= time(18, 0):
            raise forms.ValidationError("Start time must be between 09:00 and 18:00.")
        return start_time

@admin.action(description="Generate 30-minute slots from 09:00 to 18:00")
def generate_timeslots(modeladmin, request, queryset):
    for obj in queryset:
        selected_date = obj.date
        start = time(9, 0)
        end = time(18, 0)

        current_time = datetime.combine(selected_date, start)
        end_datetime = datetime.combine(selected_date, end)

        while current_time < end_datetime:
            start_time = current_time.time()

            # Check if this slot already exists
            if not TimeSlot.objects.filter(date=selected_date, start_time=start_time).exists():
                TimeSlot.objects.create(date=selected_date, start_time=start_time)
            
            current_time += timedelta(minutes=30)

@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'is_coach', 'is_staff')
    list_filter = ('is_coach', 'is_staff', 'is_superuser')
    search_fields = ('username', 'email')

# 🔹 Register with custom form + action
@admin.register(TimeSlot)
class TimeSlotAdmin(admin.ModelAdmin):
    form = TimeSlotAdminForm
    search_fields = ['date', 'start_time']
    list_display = ('date', 'start_time', 'is_available')
    list_filter = ('date', 'is_available')
    actions = [generate_timeslots]

@admin.register(Session)
class SessionAdmin(admin.ModelAdmin):
    list_display = ['subject', 'client', 'timeslot']
    search_fields = ['subject', 'client__username']
    autocomplete_fields = ['client', 'timeslot']
    list_filter = ['timeslot__date']

