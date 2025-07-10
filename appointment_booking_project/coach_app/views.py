from datetime import date as date_today

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils.timezone import now

from .forms import (
    CoachNotesForm,
    CustomUserCreationForm,
    DateSelectionForm,
    SessionForm,          # <- now the new Form, not ModelForm
)
from .models import CustomUser, Session, TimeSlot


# ─────────────────────────────────────────────
# Public pages / auth helpers (unchanged)
# ─────────────────────────────────────────────
def home(request):
    return render(request, "home.html", {"is_home": True})


class CustomLoginView(LoginView):
    template_name = "login.html"


class CustomLogoutView(LogoutView):
    next_page = reverse_lazy("home")


def signup(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            email = form.cleaned_data["email"]

            if CustomUser.objects.filter(username=username).exists():
                messages.error(request, "Username already exists.")
            elif CustomUser.objects.filter(email=email).exists():
                messages.error(request, "Email already exists.")
            else:
                user = form.save()
                login(request, user)
                messages.success(
                    request, f"Account created successfully. Welcome, {user.username}!"
                )
                return redirect("dashboard")
    else:
        form = CustomUserCreationForm()

    return render(request, "signup.html", {"form": form})


# ─────────────────────────────────────────────
# Dashboard (unchanged)
# ─────────────────────────────────────────────
@login_required
def dashboard(request):
    user = request.user
    current_time = now()

    if user.is_coach or user.is_superuser:
        upcoming_sessions = (
            Session.objects.filter(timeslot__date__gt=current_time.date())
            | Session.objects.filter(
                timeslot__date=current_time.date(), timeslot__start_time__gte=current_time.time()
            )
        )
        past_sessions = (
            Session.objects.filter(timeslot__date__lt=current_time.date())
            | Session.objects.filter(
                timeslot__date=current_time.date(), timeslot__start_time__lt=current_time.time()
            )
        )
        template = "dashboard_coach.html"
    else:
        upcoming_sessions = (
            Session.objects.filter(client=user, timeslot__date__gt=current_time.date())
            | Session.objects.filter(
                client=user,
                timeslot__date=current_time.date(),
                timeslot__start_time__gte=current_time.time(),
            )
        )
        past_sessions = (
            Session.objects.filter(client=user, timeslot__date__lt=current_time.date())
            | Session.objects.filter(
                client=user,
                timeslot__date=current_time.date(),
                timeslot__start_time__lt=current_time.time(),
            )
        )
        template = "dashboard_client.html"

    return render(
        request,
        template,
        {
            "upcoming_sessions": upcoming_sessions.order_by(
                "timeslot__date", "timeslot__start_time"
            ),
            "past_sessions": past_sessions.order_by(
                "-timeslot__date", "-timeslot__start_time"
            ),
        },
    )


# ─────────────────────────────────────────────
# BOOKING VIEW  ← updated to use new form
# ─────────────────────────────────────────────
@login_required
def make_appointment(request):
    if request.method == "POST":
        form = SessionForm(request.POST)
        if form.is_valid():
            form.save(client=request.user)
            messages.success(request, "Your session has been booked ✔")
            return redirect("dashboard")
        else:
            messages.error(request, "Please fix the errors below.")
    else:
        form = SessionForm()

    return render(request, "make_appointment.html", {"form": form})


# ─────────────────────────────────────────────
# Calendar & coach notes (unchanged)
# ─────────────────────────────────────────────
def timeslot_calendar_view(request):
    form = DateSelectionForm(request.GET or None)
    timeslots = []

    selected_date = None
    if form.is_valid():
        selected_date = form.cleaned_data["date"]
        timeslots = TimeSlot.objects.filter(date=selected_date).order_by("start_time")

    return render(
        request,
        "calendar/timeslot_list.html",
        {
            "form": form,
            "timeslots": timeslots,
            "selected_date": selected_date or date_today(),
        },
    )


@login_required
def edit_notes(request, session_id):
    session = get_object_or_404(Session, id=session_id)

    if not request.user.is_coach:
        return HttpResponseForbidden("Only coaches can edit notes.")

    if request.method == "POST":
        form = CoachNotesForm(request.POST, instance=session)
        if form.is_valid():
            form.save()
            messages.success(request, "Notes updated.")
            return redirect("dashboard")
    else:
        form = CoachNotesForm(instance=session)

    return render(request, "edit_notes.html", {"form": form, "session": session})
