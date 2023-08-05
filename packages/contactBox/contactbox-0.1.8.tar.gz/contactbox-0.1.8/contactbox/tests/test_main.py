from django.test import TestCase
from django.core.management import call_command
from django.core import mail
from django.core.urlresolvers import reverse

from contactbox.models import Message, Receiver


class MainTestCase(TestCase):
    def setUp(self):
        Receiver.objects.create(
            name='test',
            email='foo@bar.com',
            active=True)
        Receiver.objects.create(
            name='test',
            email='foo1@bar.com',
            active=True)
        Receiver.objects.create(
            name='test',
            email='foo2@bar.com',
            active=False)

    def test_sending(self):
        message = Message.objects.create(
            email='a@a.com',
            message='message',
        )
        self.assertEqual(mail.outbox, [])
        self.assertIsNone(message.notification_date)
        call_command('remind_contact')
        message = Message.objects.get(pk=message.pk)
        self.assertIsNotNone(message.notification_date)
        self.assertEqual(len(mail.outbox), 1)

    def test_www_form(self):
        self.assertEqual(mail.outbox, [])
        self.assertEqual(Message.objects.count(), 0)
        url = reverse('contact-box-form-test')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        response = self.client.post(url, {})
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, 'form', 'name', 'This field is required.')
        self.assertFormError(response, 'form', 'email', 'This field is required.')
        self.assertFormError(response, 'form', 'message', 'This field is required.')
        self.assertEqual(mail.outbox, [])
        self.assertEqual(Message.objects.count(), 0)

        data = {
            'email': 'a',
            'name': 'some name',
            'message': 'm'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, 'form', 'email', 'Enter a valid email address.')
        self.assertEqual(mail.outbox, [])
        self.assertEqual(Message.objects.count(), 0)

        data['email'] = 'a@a.com'
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)
        self.assertIsNone(Message.objects.first().notification_date)
        call_command('remind_contact')
        self.assertEqual(len(mail.outbox), 1)
        self.assertIsNotNone(Message.objects.first().notification_date)
