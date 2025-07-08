from rest_framework import viewsets, filters
from coach_app.models import CustomUser, TimeSlot, Session
from .serializers import CustomUserSerializer, TimeSlotSerializer, SessionSerializer



class CustomUserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['username', 'email']  # fields to search on


class TimeSlotViewSet(viewsets.ModelViewSet):
    queryset = TimeSlot.objects.all()
    serializer_class = TimeSlotSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['date']  # you can add more fields here


class SessionViewSet(viewsets.ModelViewSet):
    queryset = Session.objects.all()
    serializer_class = SessionSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['subject', 'client__username']  # search by subject or client's username
