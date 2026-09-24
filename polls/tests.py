from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from .models import Poll, Option, Vote

class PollsTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='Password123!'
        )
        self.poll = Poll.objects.create(
            user=self.user,
            question='Hangi telefonu almalıyım?',
            description='Fotoğraf kalitesi ve pil ömrü önemli.',
            category='teknoloji'
        )
        self.opt1 = Option.objects.create(poll=self.poll, text='iPhone 15', order=1)
        self.opt2 = Option.objects.create(poll=self.poll, text='Samsung Galaxy S24', order=2)

    def test_poll_creation_and_options(self):
        self.assertEqual(self.poll.options.count(), 2)
        self.assertEqual(self.poll.total_votes, 0)
        self.assertEqual(self.opt1.vote_percentage, 0)

    def test_anonymous_vote_api_success_and_duplicate_rejection(self):
        # First vote
        response = self.client.post(
            reverse('vote_api', kwargs={'pk': self.poll.pk}),
            {'option_id': self.opt1.pk}
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertEqual(data['total_votes'], 1)

        # Duplicate vote attempt with same session
        response2 = self.client.post(
            reverse('vote_api', kwargs={'pk': self.poll.pk}),
            {'option_id': self.opt2.pk}
        )
        self.assertEqual(response2.status_code, 400)
        data2 = response2.json()
        self.assertFalse(data2['success'])
        self.assertIn('daha önce oy verdiniz', data2['message'])

    def test_authenticated_vote(self):
        self.client.login(username='testuser', password='Password123!')
        response = self.client.post(
            reverse('vote_api', kwargs={'pk': self.poll.pk}),
            {'option_id': self.opt2.pk}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.poll.total_votes, 1)
        self.assertEqual(self.opt2.vote_percentage, 100.0)

    def test_poll_list_feed(self):
        response = self.client.get(reverse('poll_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Hangi telefonu almalıyım?')
        self.assertContains(response, 'iPhone 15')
        self.assertContains(response, 'Samsung Galaxy S24')
        # Ensure email is NEVER exposed in the HTML output
        self.assertNotContains(response, 'test@example.com')
