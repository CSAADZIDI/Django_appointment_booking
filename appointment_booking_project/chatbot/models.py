from django.db import models
from django.utils import timezone


class ChatMessage(models.Model):
    session_id = models.CharField(max_length=100)
    sender = models.CharField(max_length=10)
    message = models.TextField()
    timestamp = models.DateTimeField(default=timezone.now)
    
    
    def __str__(self):
        return f"[{self.sender}] {self.message[:50]}"
    


