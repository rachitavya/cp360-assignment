from django.urls import path
from .views import (
    CategoryListCreateView, CategoryDetailView,
    ProductListCreateView, ProductDetailView,
    ProductApproveView, ProductRejectView, UserProductHistoryView
)

urlpatterns = [
    path('categories/', CategoryListCreateView.as_view(), name='category-list-create'),
    path('categories/<int:pk>/', CategoryDetailView.as_view(), name='category-detail'),
    path('products/', ProductListCreateView.as_view(), name='product-list-create'),
    path('products/<int:pk>/', ProductDetailView.as_view(), name='product-detail'),
    path('products/<int:pk>/approve/', ProductApproveView.as_view(), name='product-approve'),
    path('products/<int:pk>/reject/', ProductRejectView.as_view(), name='product-reject'),
    path('products/history/', UserProductHistoryView.as_view(), name='user-product-history'),
] 