# views.py
from rest_framework import generics, viewsets, status, permissions, filters, serializers
from rest_framework.response import Response
from django.contrib.auth.models import User, Group
from django.shortcuts import get_object_or_404, render
from .models import MenuItem, Cart, Order, OrderItem
from .serializers import MenuItemSerializer, CartSerializer, OrderSerializer, OrderItemSerializer
from .permissions import IsManager, IsCustomer, IsDeliveryCrew, IsManagerOrReadOnly
from LittleLemonAPIDRF.models import Cart
from LittleLemonAPIDRF.serializers import CartSerializer
from .serializers import SimpleUserSerializer, GroupUserSerializer

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']

# Menu Item Views
class MenuItemViewSet(viewsets.ModelViewSet):
    queryset = MenuItem.objects.all().order_by('id')
    serializer_class = MenuItemSerializer
    filter_backends = [filters.OrderingFilter, filters.SearchFilter]
    ordering_fields = ['title', 'price']
    search_fields = ['title']
    permission_classes = [IsManagerOrReadOnly]

# Cart Views
class CartView(generics.ListCreateAPIView):
    serializer_class = CartSerializer
    permission_classes = [permissions.IsAuthenticated, IsCustomer]

    def get_queryset(self):
        return Cart.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        menuitem = serializer.validated_data['menuitem']
        quantity = serializer.validated_data['quantity']
        serializer.save(
            user=self.request.user,
            unit_price=menuitem.price,
            price=menuitem.price * quantity
        )

class CartDeleteView(generics.DestroyAPIView):
    permission_classes = [permissions.IsAuthenticated, IsCustomer]

    def delete(self, request, *args, **kwargs):
        Cart.objects.filter(user=request.user).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class CartMenuItemsView(generics.ListCreateAPIView):
    serializer_class = CartSerializer
    permission_classes = [permissions.IsAuthenticated, IsCustomer]

    def get_queryset(self):
        return Cart.objects.filter(user=self.request.user)

    #def get_serializer(self, *args, **kwargs):
    #    kwargs['context'] = self.get_serializer_context()
    #    return super().get_serializer(*args, **kwargs)

    def perform_create(self, serializer):
        menuitem = serializer.validated_data['menuitem']
        quantity = serializer.validated_data['quantity']
        serializer.save(
            user=self.request.user,
            unit_price=menuitem.price,
            price=menuitem.price * quantity
        )

    def delete(self, request, *args, **kwargs):
        Cart.objects.filter(user=request.user).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

# Order Views
class OrderListCreateView(generics.ListCreateAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.groups.filter(name='Manager').exists():
            return Order.objects.all()
        elif user.groups.filter(name='Delivery crew').exists():
            return Order.objects.filter(delivery_crew=user)
        return Order.objects.filter(user=user)

    def create(self, request, *args, **kwargs):
        user = self.request.user
        cart_items = Cart.objects.filter(user=user)

        if not cart_items.exists():
            return Response({'error': 'Cart is empty.'}, status=status.HTTP_400_BAD_REQUEST)

        total = sum(item.price for item in cart_items)

        order = Order.objects.create(user=user, total=total)

        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                menuitem=item.menuitem,
                quantity=item.quantity,
                unit_price=item.unit_price,
                price=item.price,
            )

        cart_items.delete()

        return Response({'id': order.id}, status=status.HTTP_201_CREATED)


class OrderDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = Order.objects.all()

    def patch(self, request, *args, **kwargs):
        order = self.get_object()
        user = request.user
        if user.groups.filter(name='Manager').exists():
            return self.partial_update(request, *args, **kwargs)
        elif user.groups.filter(name='Delivery crew').exists():
            status_val = request.data.get('status')
            if status_val in [0, 1]:
                order.status = status_val
                order.save()
                return Response({'status': 'Updated'}, status=200)
            return Response({'error': 'Invalid status'}, status=400)
        return Response({'error': 'Permission denied'}, status=403)

# Group Management Views
class ManagerUsersView(generics.ListCreateAPIView):
    queryset = User.objects.filter(groups__name='Manager')
    serializer_class = SimpleUserSerializer
    permission_classes = [permissions.IsAuthenticated, IsManager]

    #def get_queryset(self):
    #    return User.objects.filter(groups__name='Manager')

    #def post(self, request, *args, **kwargs):
    #    user_id = request.data.get('user_id')
    #    try:
    #        user = User.objects.get(id=user_id)
    #        manager_group, _ = Group.objects.get_or_create(name='Manager')
    #        manager_group.user_set.add(user)
    #        return Response({'message': 'User added to Manager group'}, status=status.HTTP_201_CREATED)
    #    except User.DoesNotExist:
    #        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

class ManagerUserDeleteView(generics.DestroyAPIView):
    permission_classes = [permissions.IsAuthenticated, IsManager]

    def delete(self, request, user_id):
        try:
            user = User.objects.get(id=user_id)
            manager_group = Group.objects.get(name='Manager')
            manager_group.user_set.remove(user)
            return Response({'message': 'User removed from Manager group'}, status=status.HTTP_200_OK)
        except (User.DoesNotExist, Group.DoesNotExist):
            return Response({'error': 'User or Group not found'}, status=status.HTTP_404_NOT_FOUND)

class DeliveryCrewUsersView(generics.ListCreateAPIView):
    queryset = User.objects.filter(groups__name='Delivery crew')
    serializer_class = SimpleUserSerializer
    permission_classes = [permissions.IsAuthenticated]

    #def get_queryset(self):
    #    return User.objects.filter(groups__name='Delivery crew')

    #queryset = User.objects.filter(groups__name='Delivery crew')
    #serializer_class = UserSerializer
    #permission_classes = [permissions.IsAuthenticated, IsManager]

    #def post(self, request, *args, **kwargs):
    #    user_id = request.data.get('user_id')
    #    try:
    #        user = User.objects.get(id=user_id)
    #        delivery_group, _ = Group.objects.get_or_create(name='Delivery crew')
    #        delivery_group.user_set.add(user)
    #        return Response({'message': 'User added to Delivery Crew group'}, status=status.HTTP_201_CREATED)
    #    except User.DoesNotExist:
    #        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

class DeliveryCrewUserDeleteView(generics.DestroyAPIView):
    serializer_class = SimpleUserSerializer
    permission_classes = [permissions.IsAuthenticated, IsManager]

    def delete(self, request, user_id):
        try:
            user = User.objects.get(id=user_id)
            delivery_group = Group.objects.get(name='Delivery crew')
            delivery_group.user_set.remove(user)
            return Response({'message': 'User removed from Delivery Crew group'}, status=status.HTTP_200_OK)
        except (User.DoesNotExist, Group.DoesNotExist):
            return Response({'error': 'User or Group not found'}, status=status.HTTP_404_NOT_FOUND)

class GroupUserListCreate(generics.ListCreateAPIView):
    serializer_class = GroupUserSerializer

    def get_queryset(self):
        group = Group.objects.get(name=self.kwargs['group'])
        return group.user_set.all()

    def perform_create(self, serializer):
        group = Group.objects.get(name=self.kwargs['group'])
        user_id = serializer.validated_data['user']
        user = User.objects.get(id=user_id)
        group.user_set.add(user)
