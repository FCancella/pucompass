#py manage.py test reviews.tests.test_view.LoginPageTests
from django.test import TestCase, Client

from django.urls import reverse

from django.contrib.auth.models import User

from reviews.models import Feedback, Messages


class LoginPageTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.login_url = reverse('login')
        self.home_url = reverse('home')
        self.user = User.objects.create_user(username='testuser', password='testpassword')

    def test_login_page_renders_correct_template(self):
        response = self.client.get(self.login_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'reviews/login_register.html')

    def test_login_success(self):
        response = self.client.post(self.login_url, {'username': 'testuser', 'password': 'testpassword'})
        self.assertRedirects(response, self.home_url)

    def test_login_failure_wrong_password(self):
        response = self.client.post(self.login_url, {'username': 'testuser', 'password': 'wrongpassword'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Username or password does not exist")

    def test_login_failure_nonexistent_user(self):
        response = self.client.post(self.login_url, {'username': 'nonexistent', 'password': 'password'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "User does not exist")

    def test_authenticated_user_redirect(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(self.login_url)
        self.assertRedirects(response, self.home_url)


class FeedbackViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.feedback = Feedback.objects.create(title='Test Feedback', body='This is a test feedback.')
        self.feedback_url = reverse('feedback', args=[self.feedback.id])
    
    def test_feedback_page_renders_correct_template(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(self.feedback_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'reviews/forum_form.html')
    
    def test_feedback_post_message_success(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.post(self.feedback_url, {'message': 'This is a test message.'})
        self.assertRedirects(response, self.feedback_url)
        self.assertEqual(Messages.objects.count(), 1)
        self.assertEqual(Messages.objects.first().message, 'This is a test message.')
    
    def test_feedback_post_empty_message(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.post(self.feedback_url, {'message': ''})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(Messages.objects.count(), 0)
    
    def test_feedback_page_shows_messages(self):
        self.client.login(username='testuser', password='testpassword')
        Messages.objects.create(author=self.user, feedback=self.feedback, message='This is a test message.')
        response = self.client.get(self.feedback_url)
        self.assertContains(response, 'This is a test message.')

    def test_feedback_page_shows_participants(self):
        self.client.login(username='testuser', password='testpassword')
        self.feedback.participants.add(self.user)
        response = self.client.get(self.feedback_url)
        self.assertContains(response, 'testuser')