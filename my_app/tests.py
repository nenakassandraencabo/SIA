from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import Appointment

User = get_user_model()


class AuthenticationAndAppointmentTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='scheduler', password='Strong-password-123!')

    def test_dashboard_and_crud_require_authentication(self):
        response = self.client.get(reverse('appointment_list'))
        self.assertRedirects(response, f"{reverse('login')}?next=/")
        response = self.client.post(reverse('appointment_create'), {})
        self.assertEqual(response.status_code, 302)

    def test_dashboard_statistics_and_filters_are_database_backed(self):
        Appointment.objects.create(
            patient_name='Alex Pending',
            contact_number='555-0101',
            appointment_date='2026-11-02',
            appointment_time='09:30',
            purpose='Consultation',
            status='Pending',
        )
        Appointment.objects.create(
            patient_name='Jordan Confirmed',
            contact_number='555-0102',
            appointment_date='2026-11-03',
            appointment_time='10:00',
            purpose='Checkup',
            status='Confirmed',
        )
        Appointment.objects.create(
            patient_name='Sam Cancelled',
            contact_number='555-0103',
            appointment_date='2026-11-04',
            appointment_time='11:00',
            purpose='Follow up',
            status='Cancelled',
        )
        self.client.force_login(self.user)

        response = self.client.get(reverse('appointment_list'))

        self.assertEqual(response.context['total'], 3)
        self.assertEqual(response.context['pending'], 1)
        self.assertEqual(response.context['approved'], 1)
        self.assertEqual(response.context['cancelled'], 1)
        self.assertContains(response, 'Jordan Confirmed')

        response = self.client.get(reverse('appointment_list'), {'q': '555-0101', 'status': 'Pending'})
        self.assertEqual(len(response.context['appointments']), 1)
        self.assertEqual(response.context['appointments'][0].patient_name, 'Alex Pending')

    def test_create_update_and_post_delete_use_correct_appointment_id(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse('appointment_create'), {
            'patient_name': 'Taylor Patient',
            'contact_number': '555-0199',
            'appointment_date': '2026-11-12',
            'appointment_time': '13:15',
            'purpose': 'Annual visit',
            'status': 'Pending',
        })
        self.assertRedirects(response, reverse('appointment_list'))
        appointment = Appointment.objects.get(patient_name='Taylor Patient')

        response = self.client.post(reverse('appointment_update', kwargs={'id': appointment.pk}), {
            'patient_name': 'Taylor Updated',
            'contact_number': '555-0199',
            'appointment_date': '2026-11-12',
            'appointment_time': '13:15',
            'purpose': 'Annual visit',
            'status': 'Confirmed',
        })
        self.assertRedirects(response, reverse('appointment_list'))
        appointment.refresh_from_db()
        self.assertEqual(appointment.patient_name, 'Taylor Updated')
        self.assertEqual(appointment.status, 'Confirmed')

        self.assertEqual(
            self.client.get(reverse('appointment_delete', kwargs={'id': appointment.pk})).status_code,
            200,
        )
        response = self.client.post(reverse('appointment_delete', kwargs={'id': appointment.pk}))
        self.assertRedirects(response, reverse('appointment_list'))
        self.assertFalse(Appointment.objects.filter(pk=appointment.pk).exists())

    def test_registration_hashes_password_and_rejects_duplicate_email(self):
        valid_data = {
            'full_name': 'Morgan Lee',
            'username': 'morgan',
            'email': 'morgan@example.com',
            'password1': 'A-very-strong-Password-947!',
            'password2': 'A-very-strong-Password-947!',
        }
        response = self.client.post(reverse('register'), valid_data)
        self.assertRedirects(response, reverse('login'))
        user = User.objects.get(username='morgan')
        self.assertTrue(user.check_password(valid_data['password1']))
        self.assertNotEqual(user.password, valid_data['password1'])
        self.assertEqual(user.get_full_name(), 'Morgan Lee')

        duplicate_data = {**valid_data, 'username': 'another-user', 'email': 'MORGAN@example.com'}
        response = self.client.post(reverse('register'), duplicate_data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(User.objects.filter(email__iexact='morgan@example.com').count(), 1)

    def test_login_and_post_only_logout(self):
        response = self.client.post(reverse('login'), {
            'username': 'scheduler',
            'password': 'Strong-password-123!',
        })
        self.assertRedirects(response, reverse('appointment_list'))
        self.assertTrue(response.wsgi_request.user.is_authenticated)
        self.assertEqual(self.client.get(reverse('logout')).status_code, 405)

        response = self.client.post(reverse('logout'))
        self.assertRedirects(response, reverse('login'))
        self.assertFalse(response.wsgi_request.user.is_authenticated)
