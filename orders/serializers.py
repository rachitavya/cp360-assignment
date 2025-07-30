from rest_framework import serializers
from .models import Order
from products.models import Product

class OrderSerializer(serializers.ModelSerializer):
    products = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all(), many=True)
    user = serializers.ReadOnlyField(source='user.id')

    class Meta:
        model = Order
        fields = ['id', 'user', 'products', 'status', 'created_at', 'updated_at']
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']

    def validate_products(self, value):
        if not value:
            raise serializers.ValidationError('At least one product must be selected.')
        return value 