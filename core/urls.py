from django.urls import path
from .template_views import (
    template_register, template_login, template_logout,
    dashboard, add_product, edit_product, delete_product, generate_dummy,
    categories, add_category, edit_category, delete_category,
    orders, place_order, order_detail, edit_order,
    approve_product, reject_product
)

urlpatterns = [
    path('', dashboard, name='dashboard'),
    path('register/', template_register, name='template_register'),
    path('login/', template_login, name='template_login'),
    path('logout/', template_logout, name='template_logout'),
    path('products/add/', add_product, name='add_product'),
    path('products/<int:product_id>/edit/', edit_product, name='edit_product'),
    path('products/<int:product_id>/delete/', delete_product, name='delete_product'),
    path('products/<int:product_id>/approve/', approve_product, name='approve_product'),
    path('products/<int:product_id>/reject/', reject_product, name='reject_product'),
    path('generate-dummy/', generate_dummy, name='generate_dummy'),
    path('categories/', categories, name='categories'),
    path('categories/add/', add_category, name='add_category'),
    path('categories/<int:category_id>/edit/', edit_category, name='edit_category'),
    path('categories/<int:category_id>/delete/', delete_category, name='delete_category'),
    path('orders/', orders, name='orders'),
    path('orders/place/', place_order, name='place_order'),
    path('orders/<int:order_id>/', order_detail, name='order_detail'),
    path('orders/<int:order_id>/edit/', edit_order, name='edit_order'),
] 