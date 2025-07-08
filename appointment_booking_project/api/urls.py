from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CustomUserViewSet, TimeSlotViewSet, SessionViewSet

router = DefaultRouter()
router.register(r'users', CustomUserViewSet)
router.register(r'timeslots', TimeSlotViewSet)
router.register(r'sessions', SessionViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
