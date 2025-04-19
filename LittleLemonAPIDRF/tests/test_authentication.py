from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse

class TestUserRegistration(APITestCase):

    def test_user_registration(self):
        print("Testing user registration...")
        
        url = '/api/users/'
        data = {
            'username': 'testuser',
            'email': 'testuser@example.com',
            'password': 'pass12345'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
