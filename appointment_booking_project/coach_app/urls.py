from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.home, name='home'),

    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', views.CustomLogoutView.as_view(), name='logout'),


    
    path('signup/', views.signup, name='signup'),

    path('dashboard/', views.dashboard, name='dashboard'),
    path('appointment/', views.make_appointment, name='make_appointment'),
    
    path('session/<int:session_id>/edit-notes/', views.edit_notes, name='edit_notes')


    
]
