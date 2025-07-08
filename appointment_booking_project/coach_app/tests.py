from django.test import TestCase
from django.utils import timezone
from datetime import date, time, timedelta, datetime
from .models import CustomUser, TimeSlot, Session


class CustomUserModelTest(TestCase):
    def test_user_creation_and_str(self):
        user = CustomUser.objects.create_user(username='testuser', password='password123')
        user.is_coach = True
        user.save()
        self.assertEqual(str(user), 'testuser')
        self.assertTrue(user.is_coach)


class TimeSlotModelTest(TestCase):
    def setUp(self):
        self.timeslot = TimeSlot.objects.create(
            date=date.today(),
            start_time=time(9, 0),
            is_available=True
        )

    def test_end_time_property(self):
        expected_end_time = (datetime.combine(self.timeslot.date, self.timeslot.start_time) + timedelta(minutes=30)).time()
        self.assertEqual(self.timeslot.end_time, expected_end_time)

    def test_str_method_available(self):
        expected_str = f"{self.timeslot.date} at {self.timeslot.start_time} (Available)"
        self.assertEqual(str(self.timeslot), expected_str)

    def test_str_method_booked(self):
        self.timeslot.is_available = False
        self.timeslot.save()
        expected_str = f"{self.timeslot.date} at {self.timeslot.start_time} (Booked)"
        self.assertEqual(str(self.timeslot), expected_str)

    def test_unique_together_constraint(self):
        # Trying to create a duplicate timeslot should raise an IntegrityError
        with self.assertRaises(Exception):
            TimeSlot.objects.create(date=self.timeslot.date, start_time=self.timeslot.start_time)


class SessionModelTest(TestCase):
    def setUp(self):
        self.client_user = CustomUser.objects.create_user(username='client1', password='password123')
        self.timeslot = TimeSlot.objects.create(date=date.today(), start_time=time(10, 0))
        self.session = Session.objects.create(
            client=self.client_user,
            timeslot=self.timeslot,
            subject='Math Tutoring',
            notes_coach='Focus on calculus',
        )

    def test_str_method(self):
        expected_str = f"Session 'Math Tutoring' on {self.timeslot.date} at {self.timeslot.start_time} with {self.client_user.username}"
        self.assertEqual(str(self.session), expected_str)

    def test_session_ordering(self):
        # Create another session at an earlier time to check ordering
        earlier_timeslot = TimeSlot.objects.create(date=date.today(), start_time=time(9, 0))
        earlier_session = Session.objects.create(
            client=self.client_user,
            timeslot=earlier_timeslot,
            subject='English Tutoring',
        )
        sessions = list(Session.objects.all())
        self.assertEqual(sessions[0], earlier_session)
        self.assertEqual(sessions[1], self.session)
