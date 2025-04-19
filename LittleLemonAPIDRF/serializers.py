from rest_framework import serializers
from django.contrib.auth.models import User
from .models import MenuItem, Cart, Order, OrderItem

class MenuItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = MenuItem
        fields = '__all__'


class CartSerializer(serializers.ModelSerializer):
    unit_price = serializers.DecimalField(max_digits=6, decimal_places=2, read_only=True)
    price = serializers.DecimalField(max_digits=6, decimal_places=2, read_only=True)
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    
    class Meta:
        model = Cart
        fields = '__all__'

    def create(self, validated_data):
        menuitem = validated_data['menuitem']
        quantity = validated_data['quantity']
        validated_data['unit_price'] = menuitem.price
        validated_data['price'] = menuitem.price * quantity
        validated_data['user'] = self.context['request'].user  # Important for automatic user
        return super().create(validated_data)

class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = '__all__'

class OrderSerializer(serializers.ModelSerializer):
    order_items = OrderItemSerializer(many=True, read_only=True)
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    delivery_crew = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), required=False)

    class Meta:
        model = Order
        fields = ['id', 'user', 'delivery_crew', 'status', 'total', 'date', 'order_items']

class SimpleUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']

class GroupUserSerializer(serializers.Serializer):
    user = serializers.IntegerField()
