from django.contrib import admin
from .models import ChatMessage

@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ('session_id', 'sender', 'message','timestamp')
    list_filter = ('sender', 'timestamp')
    search_fields = ('message', 'session_id')
