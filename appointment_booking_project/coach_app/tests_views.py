from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from datetime import time
from coach_app.models import CustomUser, TimeSlot, Session


class ViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.client_user = CustomUser.objects.create_user(
            username='clientuser', password='testpass123', is_coach=False
        )
        self.coach_user = CustomUser.objects.create_user(
            username='coachuser', password='testpass123', is_coach=True
        )
        self.timeslot = TimeSlot.objects.create(
            date=timezone.now().date(),
            start_time=time(10, 0),
            is_available=True
        )
        self.login_url = reverse('login')
        self.logout_url = reverse('logout')
        self.signup_url = reverse('signup')
        self.dashboard_url = reverse('dashboard')
        self.make_appointment_url = reverse('make_appointment')
        self.home_url = reverse('home')

    def test_home_view(self):
        response = self.client.get(self.home_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'home.html')

    def test_signup_view_get(self):
        response = self.client.get(self.signup_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'signup.html')

    def test_signup_view_post(self):
        response = self.client.post(self.signup_url, {
            'username': 'newuser',
            'password1': 'StrongPassword123!',
            'password2': 'StrongPassword123!'
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(CustomUser.objects.filter(username='newuser').exists())

    def test_login_view(self):
        response = self.client.post(self.login_url, {
            'username': 'clientuser',
            'password': 'testpass123'
        })
        self.assertEqual(response.status_code, 302)

    def test_logout_view(self):
        self.client.login(username='clientuser', password='testpass123')
        response = self.client.get(self.logout_url)
        self.assertEqual(response.status_code, 302)

    def test_dashboard_view_client(self):
        self.client.login(username='clientuser', password='testpass123')
        response = self.client.get(self.dashboard_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'dashboard_client.html')

    def test_dashboard_view_coach(self):
        self.client.login(username='coachuser', password='testpass123')
        response = self.client.get(self.dashboard_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'dashboard_coach.html')

    def test_make_appointment_get(self):
        self.client.login(username='clientuser', password='testpass123')
        response = self.client.get(self.make_appointment_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'make_appointment.html')

    def test_make_appointment_post_success(self):
        self.client.login(username='clientuser', password='testpass123')
        response = self.client.post(self.make_appointment_url, {
            'timeslot': self.timeslot.id,
            'subject': 'Test Subject'
        })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, self.dashboard_url)
        self.assertEqual(Session.objects.count(), 1)
        session = Session.objects.first()
        self.assertEqual(session.client, self.client_user)
        self.assertEqual(session.subject, 'Test Subject')
        self.timeslot.refresh_from_db()
        self.assertFalse(self.timeslot.is_available)

    def test_make_appointment_post_unavailable(self):
        self.timeslot.is_available = False
        self.timeslot.save()

        self.client.login(username='clientuser', password='testpass123')
        response = self.client.post(self.make_appointment_url, {
            'timeslot': self.timeslot.id,
            'subject': 'Test Fail Subject'
        })

        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, 'form', 'timeslot', 'Ce créneau est déjà réservé.')
        self.assertEqual(Session.objects.count(), 0)
