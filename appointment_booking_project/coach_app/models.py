from django.contrib.auth.models import AbstractUser
from django.db import models
from datetime import datetime, timedelta


class CustomUser(AbstractUser):
    """
    Custom user model extending Django's default User.
    """
    is_coach = models.BooleanField(default=False)  # Distinguishes coaches from clients

    def __str__(self):
        return self.username


class TimeSlot(models.Model):
    """
    Represents a predefined time slot that can be booked.
    """
    date = models.DateField()
    start_time = models.TimeField()
     
    is_available = models.BooleanField(default=True)

    @property
    def end_time(self):
        """Returns end time 30 minutes after start_time"""
        start_dt = datetime.combine(self.date, self.start_time)
        end_dt = start_dt + timedelta(minutes=30)
        return end_dt.time()
    
    class Meta:
        unique_together = ['date', 'start_time']
        ordering = ['date', 'start_time']

    def __str__(self):
        status = "Available" if self.is_available else "Booked"
        return f"{self.date} at {self.start_time} ({status})"


class Session(models.Model):
    """
    Represents a coaching session.
    """
    client = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='sessions')
    timeslot = models.OneToOneField(TimeSlot, on_delete=models.CASCADE, related_name='session')
    subject = models.CharField(max_length=255)
    notes_coach = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    

    class Meta:
        ordering = ['timeslot__date', 'timeslot__start_time']

    def __str__(self):
        return f"Session '{self.subject}' on {self.timeslot.date} at {self.timeslot.start_time} with {self.client.username}"
