'''
from django.test import TestCase, Client

from django.urls import reverse

from django.contrib.auth.models import User




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

'''