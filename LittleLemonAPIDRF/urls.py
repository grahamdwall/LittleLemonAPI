from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    MenuItemViewSet, CartView, CartDeleteView, CartMenuItemsView,
    OrderListCreateView, OrderDetailView,
    ManagerUsersView, ManagerUserDeleteView,
    DeliveryCrewUsersView, DeliveryCrewUserDeleteView
)

router = DefaultRouter()
router.register(r'menu-items', MenuItemViewSet, basename='menuitem')

urlpatterns = [
    path('', include(router.urls)),
    path('cart/menu-items/', CartMenuItemsView.as_view()),
    path('cart/menu-items/delete/', CartDeleteView.as_view()),
    path('orders/', OrderListCreateView.as_view()),
    path('orders/<int:pk>/', OrderDetailView.as_view()),
    path('groups/manager/users/', ManagerUsersView.as_view()),
    path('groups/manager/users/<int:user_id>/', ManagerUserDeleteView.as_view()),
    path('groups/delivery-crew/users/', DeliveryCrewUsersView.as_view()),
    path('groups/delivery-crew/users/<int:user_id>/', DeliveryCrewUserDeleteView.as_view()),
]
