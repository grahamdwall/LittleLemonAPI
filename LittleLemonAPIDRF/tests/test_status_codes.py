# tests/test_status_codes.py
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth.models import User, Group
from LittleLemonAPIDRF.models import MenuItem
from django.urls import reverse
from rest_framework.authtoken.models import Token

class TestStatusCodes(APITestCase):
    def setUp(self):
        self.client = APIClient()

        # Create users
        self.manager = User.objects.create_user(username="manager", password="testpass")
        self.customer = User.objects.create_user(username="customer", password="testpass")
        self.anon_client = APIClient()  # Not logged in

        # Create groups
        self.manager_group = Group.objects.get_or_create(name="Manager")[0]
        self.manager.groups.add(self.manager_group)

        # Create token for manager
        self.token = Token.objects.create(user=self.manager)

        # Authenticate as manager
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        
        # Auth tokens
        #self.client.login(username="manager", password="testpass")

        # Create a menu item
        self.menuitem = MenuItem.objects.create(title="Pasta", price=9.99, inventory=10)

    def test_get_menu_item_success(self):
        print("Testing GET menu item success...")

        url = reverse('menuitem-detail', args=[self.menuitem.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_menu_item_success(self):
        print("Testing POST menu item success...")

        url = reverse('menuitem-list')
        data = {"title": "Pizza", "price": 12.99, "inventory": 5}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_unauthorized_post_menu_item(self):
        print("Testing unauthorized POST menu item...")

        self.client.logout()
        self.client.login(username="customer", password="testpass")
        url = reverse('menuitem-list')
        data = {"title": "Salad", "price": 5.00, "inventory": 3}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_forbidden_get_without_auth(self):
        print("Testing forbidden GET without auth...")

        url = reverse('menuitem-list')
        response = self.anon_client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)  # Anonymous users can access the list of menu items

    def test_unauthenticated_post_menu_item(self):
        print("Testing unauthenticated POST menu item...")

        url = reverse('menuitem-list')
        data = {"title": "Sushi", "price": 15.00, "inventory": 3}
        response = self.anon_client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED) # Anonymous users cannot create menu items

    def test_bad_request_invalid_data(self):
        print("Testing bad request with invalid data...")

        url = reverse('menuitem-list')
        invalid_data = {"title": "", "price": "invalid", "inventory": -1}
        response = self.client.post(url, invalid_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_not_found_menu_item(self):
        print("Testing not found menu item...")
        
        url = reverse('menuitem-detail', args=[9999])  # Non-existing ID
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def tearDown(self):
        self.client.logout()
        self.manager.delete()
        self.customer.delete()
        self.menuitem.delete()
