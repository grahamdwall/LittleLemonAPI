# LittleLemonAPIDRF/tests/test_users_cart_orders.py

from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth.models import User, Group
from rest_framework.authtoken.models import Token
from LittleLemonAPIDRF.models import MenuItem, Cart, Order, OrderItem
import uuid

class TestUsersCartOrdersEndpoints(APITestCase):

    def setUp(self):
        Cart.objects.all().delete()

        # Create Manager
        self.manager_user = User.objects.create_user(username='manager', password='testpass')
        self.manager_group, _ = Group.objects.get_or_create(name="Manager")  # <-- UNPACK!
        self.manager_user.groups.add(self.manager_group)  # now manager_group is a Group
        self.manager_user.refresh_from_db()        
        self.manager_token = Token.objects.create(user=self.manager_user)
        self.manager_auth = {"HTTP_AUTHORIZATION": f"Token {self.manager_token.key}"}

        # Create Delivery Crew
        self.delivery_crew_user = User.objects.create_user(username='deliveryuser', password='testpass')
        self.delivery_group, _ = Group.objects.get_or_create(name="Delivery crew")
        self.delivery_crew_user.groups.add(self.delivery_group)
        self.delivery_crew_user.refresh_from_db()
        self.delivery_token = Token.objects.create(user=self.delivery_crew_user)
        self.delivery_auth = {"HTTP_AUTHORIZATION": f"Token {self.delivery_token.key}"}

        # Create Customer
        self.customer_user = User.objects.create_user(username='customer', password='testpass')
        self.customer_token = Token.objects.create(user=self.customer_user)
        self.customer_auth = {"HTTP_AUTHORIZATION": f"Token {self.customer_token.key}"}

        self.client.force_authenticate(user=self.customer_user)

        # Create menu item
        self.menu_item = MenuItem.objects.create(title="Salad", price=5.00, inventory=100)
        self.client.post('/api/cart/menu-items/', {"menuitem": self.menu_item.id, "quantity": 2}, format='json')
        self.client.post('/api/orders/', format='json')

    def authenticate(self, token):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)

    # User Group Management Tests

    def test_manager_can_get_manager_users(self):
        print("Test manager can get manager users")

        self.client.force_authenticate(user=self.manager_user)
        response = self.client.get('/api/groups/manager/users/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_manager_can_assign_manager_group(self):
        print("Test manager can assign manager group")

        self.client.force_authenticate(user=self.manager_user)

        self.test_manager_name = f'manager_{uuid.uuid4().hex[:6]}'
        User.objects.filter(username=self.test_manager_name).delete()
        self.testmanager_user = User.objects.create_user(username=self.test_manager_name, password='password')
        payload = {"username": self.testmanager_user.username}  # Use the username of the new user
        response = self.client.post('/api/groups/manager/users/', payload, format='json', **self.manager_auth)
        print("RESPONSE STATUS:", response.status_code)
        print("RESPONSE DATA:", response.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_manager_can_remove_manager_group(self):
        print("Test manager can remove manager group")

        self.manager_user.groups.add(Group.objects.get(name='Manager'))
        self.client.force_authenticate(user=self.manager_user)
        response = self.client.delete(f'/api/groups/manager/users/{self.manager_user.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_manager_can_get_delivery_crew_users(self):
        print("Test manager can get delivery crew users")

        self.client.force_authenticate(user=self.manager_user)
        response = self.client.get('/api/groups/delivery-crew/users/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_manager_can_assign_delivery_crew_group(self):
        print("Test manager can assign delivery crew group")

        self.client.force_authenticate(user=self.manager_user)

        self.test_deliverycrew_name = f'testdeliverycrew_{uuid.uuid4().hex[:6]}'
        User.objects.filter(username=self.test_deliverycrew_name).delete()
        self.testdeliverycrew_user = User.objects.create_user(username=self.test_deliverycrew_name, password='password')
        payload = {"username": self.testdeliverycrew_user.username}  # Use the username of the new user
        response = self.client.post('/api/groups/delivery-crew/users/', payload, format='json', **self.manager_auth)
        print("RESPONSE STATUS:", response.status_code)
        print("RESPONSE DATA:", response.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_manager_can_remove_delivery_crew_user(self):
        print("Test manager can remove delivery crew user")

        self.client.force_authenticate(user=self.manager_user)
        response = self.client.delete(f'/api/groups/delivery-crew/users/{self.delivery_crew_user.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    # Cart Management Tests

    def test_customer_can_add_to_cart_and_view_cart(self):
        print("Test customer can add to cart and view cart")

        self.client.force_authenticate(user=self.customer_user)
        Cart.objects.filter(user=self.customer_user).delete()  # 🛑 clean cart

        menuitem = MenuItem.objects.create(title="Pizza", price=10.00, inventory=10)
        payload = {
            "menuitem": menuitem.id,
            "quantity": 2,
        }
        response = self.client.post('/api/cart/menu-items/', payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        response = self.client.get('/api/cart/menu-items/')
        print("RESPONSE DATA:", response.data)

        self.assertEqual(len(response.data['results']), 1)
        
    def test_customer_can_clear_cart(self):
        print("Test customer can clear cart")

        self.client.force_authenticate(user=self.customer_user)

        # Add item first
        self.client.post('/api/cart/menu-items/', {"menuitem": self.menu_item.id, "quantity": 2}, format='json')

        # Clear cart
        response = self.client.delete('/api/cart/menu-items/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    # Order Management Tests

    def test_customer_can_place_order(self):
        print("Test customer can place order")

        self.client.force_authenticate(user=self.customer_user)

        # Add item to cart first
        self.client.post('/api/cart/menu-items/', {"menuitem": self.menu_item.id, "quantity": 2}, format='json')

        # Place order
        response = self.client.post('/api/orders/')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_customer_can_view_own_orders(self):
        print("Test customer can view own orders")

        self.client.force_authenticate(user=self.customer_user)

        # Add item and create order
        self.client.post('/api/cart/menu-items/', {"menuitem": self.menu_item.id, "quantity": 2}, format='json')
        #order_response = self.client.post('/api/orders/')

        # Get orders
        response = self.client.get('/api/orders/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_manager_can_view_all_orders(self):
        print("Test manager can view all orders")

        self.client.force_authenticate(user=self.manager_user)
        response = self.client.get('/api/orders/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_manager_can_assign_delivery_and_update_order(self):
        print("Test manager can assign delivery and update order")

        self.client.force_authenticate(user=self.customer_user)

        # Add item and create order as customer
        self.client.post('/api/cart/menu-items/', {"menuitem": self.menu_item.id, "quantity": 2}, format='json')
        #order_response = self.client.post('/api/orders/')
        #order_id = order_response.data['id']
        order_id = Order.objects.first().id  # instead of order_response.data['id']

        # Manager assigns delivery crew
        self.client.force_authenticate(user=self.manager_user)
        response = self.client.patch(f'/api/orders/{order_id}/', {"delivery_crew": self.delivery_crew_user.id, "status": 0}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_manager_can_delete_order(self):
        print("Test manager can delete order")

        self.client.force_authenticate(user=self.customer_user)

        # Customer creates order
        self.client.post('/api/cart/menu-items/', {"menuitem": self.menu_item.id, "quantity": 2}, format='json')
        #order_response = self.client.post('/api/orders/')
        order_id = Order.objects.first().id  # instead of order_response.data['id']
        #order_id = order_response.data['id']

        # Manager deletes order
        self.client.force_authenticate(user=self.manager_user)
        response = self.client.delete(f'/api/orders/{order_id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delivery_crew_can_update_order_status(self):
        print("Test delivery crew can update order status")

        #menuitem = MenuItem.objects.create(title="Burger", price=12.00, inventory=50)

        self.client.force_authenticate(user=self.customer_user)

        # Customer creates order
        self.client.post('/api/cart/menu-items', {"menuitem": self.menu_item.id, "quantity": 2})
        #order_response = self.client.post('/api/orders/')
        #order_id = order_response.data['id']
        order_id = Order.objects.first().id  # instead of order_response.data['id']

        # Manager assigns delivery crew
        self.client.force_authenticate(user=self.manager_user)
        response = self.client.patch(f'/api/orders/{order_id}/', {"status": True}, format='json')        
        #self.client.patch(f'/api/orders/{order_id}/', {"delivery_crew": self.delivery_crew_user.id, "status": 1}, format='json')
        print("RESPONSE DATA:", response.data)

        # Delivery crew updates order status
        self.client.force_authenticate(user=self.delivery_crew_user)
        response = self.client.patch(f'/api/orders/{order_id}/', {"status": True}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def tearDown(self):
        self.client.credentials()
