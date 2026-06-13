from django.test import TestCase
from django.urls import reverse
from accounts.models import User
from reservations.models import Reservation
import datetime


class ReservationsTestCase(TestCase):
    def setUp(self):
        # Create user
        self.user = User.objects.create_user(
            username='reserveuser',
            password='reservepassword123',
            email='reserve@example.com'
        )
        
        # Create a past/future reservation
        self.reservation = Reservation.objects.create(
            customer=self.user,
            date=datetime.date.today() + datetime.timedelta(days=2),
            time=datetime.time(19, 0),
            number_of_guests=4,
            special_request='Window seat please'
        )

    def test_reservation_login_required(self):
        """Verify list and book views redirect anonymous users to login."""
        response = self.client.get(reverse('reservations:list'))
        self.assertRedirects(response, f"{reverse('accounts:login')}?next={reverse('reservations:list')}")
        
        response = self.client.get(reverse('reservations:create'))
        self.assertRedirects(response, f"{reverse('accounts:login')}?next={reverse('reservations:create')}")

    def test_reservation_list_view(self):
        """Verify list view displays user reservations."""
        self.client.login(username='reserveuser', password='reservepassword123')
        response = self.client.get(reverse('reservations:list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'reservations/reservation_list.html')
        self.assertContains(response, 'Window seat please')
        self.assertContains(response, '4 Guests')

    def test_book_reservation_success(self):
        """Verify successful reservation booking."""
        self.client.login(username='reserveuser', password='reservepassword123')
        form_data = {
            'date': (datetime.date.today() + datetime.timedelta(days=5)).isoformat(),
            'time': '18:30',
            'number_of_guests': 6,
            'special_request': 'Birthday celebration'
        }
        response = self.client.post(reverse('reservations:create'), form_data)
        
        # Check database
        new_reservation = Reservation.objects.filter(special_request='Birthday celebration').first()
        self.assertIsNotNone(new_reservation)
        self.assertEqual(new_reservation.number_of_guests, 6)
        self.assertEqual(new_reservation.reservation_status, Reservation.Status.PENDING)
        
        # Check redirect
        self.assertRedirects(response, reverse('reservations:list'))

    def test_book_reservation_invalid_date_past(self):
        """Verify booking fails for a past date."""
        self.client.login(username='reserveuser', password='reservepassword123')
        form_data = {
            'date': (datetime.date.today() - datetime.timedelta(days=1)).isoformat(),
            'time': '18:30',
            'number_of_guests': 2,
            'special_request': ''
        }
        response = self.client.post(reverse('reservations:create'), form_data)
        self.assertEqual(response.status_code, 200) # stays on page to show form errors
        self.assertFalse(Reservation.objects.filter(special_request='Invalid Date').exists())

    def test_cancel_reservation(self):
        """Verify user can cancel a pending reservation."""
        self.client.login(username='reserveuser', password='reservepassword123')
        response = self.client.get(reverse('reservations:cancel', kwargs={'pk': self.reservation.pk}))
        
        # Check database status
        self.reservation.refresh_from_db()
        self.assertEqual(self.reservation.reservation_status, Reservation.Status.CANCELLED)
        
        # Check redirect
        self.assertRedirects(response, reverse('reservations:list'))
