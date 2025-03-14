from django.urls import path
from .views import book_list, book_create, book_update, book_delete, signup, login, logout, check_username, profile, add_to_cart, view_cart, checkout, view_orders, remove_from_cart

urlpatterns = [
    path('', book_list, name='book_list'),
    path('admin/', book_list, name='book_list'),
    path('add/', book_create, name='book_create'),
    path('edit/<int:pk>/', book_update, name='book_update'),
    path('delete/<int:pk>/', book_delete, name='book_delete'),
    path('signup/', signup, name='signup'),
    path('login/', login, name='login'),
    path('logout/', logout, name='logout'),
    path('check_username/', check_username, name='check_username'),
    path('profile/', profile, name='profile'),
    path('add_to_cart/<int:pk>/', add_to_cart, name='add_to_cart'),
    path('cart/', view_cart, name='view_cart'),
    path('checkout/', checkout, name='checkout'),
    path('orders/', view_orders, name='view_orders'),
    path('remove_from_cart/<int:pk>/', remove_from_cart, name='remove_from_cart'),
]
