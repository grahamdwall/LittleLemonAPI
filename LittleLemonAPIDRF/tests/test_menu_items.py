# LittleLemonAPIDRF/tests/test_menu_items.py

from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth.models import User, Group
from LittleLemonAPIDRF.models import MenuItem
from rest_framework.authtoken.models import Token

class TestMenuItemEndpoints(APITestCase):

    def setUp(self):
        # Create Manager user
        self.manager = User.objects.create_user(username='manager', password='testpass')
        manager_group = Group.objects.get_or_create(name='Manager')[0]
        self.manager.groups.add(manager_group)
        self.manager_token = Token.objects.create(user=self.manager)

        # Create Delivery Crew user
        self.delivery_user = User.objects.create_user(username='delivery', password='testpass')
        delivery_group = Group.objects.get_or_create(name='Delivery crew')[0]
        self.delivery_user.groups.add(delivery_group)
        self.delivery_token = Token.objects.create(user=self.delivery_user)

        # Create Customer user
        self.customer = User.objects.create_user(username='customer', password='testpass')
        self.customer_token = Token.objects.create(user=self.customer)

        # Create sample MenuItem
        self.menu_item = MenuItem.objects.create(title="Pizza", price=10.00, inventory=10)

    def authenticate(self, token):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)

    def test_customer_get_menu_items(self):
        print("Test customer get menu items")

        self.authenticate(self.customer_token)
        response = self.client.get('/api/menu-items/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_customer_cannot_modify_menu_items(self):
        print("Test customer cannot modify menu items")

        self.authenticate(self.customer_token)
        response = self.client.post('/api/menu-items/', {"title": "Burger", "price": 12, "inventory": 5})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        response = self.client.put(f'/api/menu-items/{self.menu_item.id}/', {"title": "Burger", "price": 12, "inventory": 5})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        response = self.client.patch(f'/api/menu-items/{self.menu_item.id}/', {"price": 15})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        response = self.client.delete(f'/api/menu-items/{self.menu_item.id}/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delivery_crew_get_menu_items(self):
        print("Test delivery crew get menu items")

        self.authenticate(self.delivery_token)
        response = self.client.get('/api/menu-items/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delivery_crew_cannot_modify_menu_items(self):
        print("Test delivery crew cannot modify menu items")

        self.authenticate(self.delivery_token)
        response = self.client.post('/api/menu-items/', {"title": "Pasta", "price": 15, "inventory": 7})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        response = self.client.put(f'/api/menu-items/{self.menu_item.id}/', {"title": "Pasta", "price": 15, "inventory": 7})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        response = self.client.patch(f'/api/menu-items/{self.menu_item.id}/', {"price": 17})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        response = self.client.delete(f'/api/menu-items/{self.menu_item.id}/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_manager_can_manage_menu_items(self):
        print("Test manager can manage menu items")
        
        self.authenticate(self.manager_token)
        
        # List menu items
        response = self.client.get('/api/menu-items/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Create new menu item
        response = self.client.post('/api/menu-items/', {"title": "Steak", "price": 20, "inventory": 4})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        new_item_id = response.data['id']

        # Get single menu item
        response = self.client.get(f'/api/menu-items/{new_item_id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Update menu item
        response = self.client.put(f'/api/menu-items/{new_item_id}/', {"title": "Steak", "price": 22, "inventory": 3})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Partial update
        response = self.client.patch(f'/api/menu-items/{new_item_id}/', {"price": 25})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Delete menu item
        response = self.client.delete(f'/api/menu-items/{new_item_id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def tearDown(self):
        self.client.credentials()  # Clear token
