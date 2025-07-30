from rest_framework import serializers
from .models import Category, Product

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'description']

class ProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all(), source='category', write_only=True)
    video_url = serializers.ReadOnlyField()

    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'category', 'category_id', 'video', 'video_url', 'status', 'uploaded_by', 'created_at', 'updated_at']
        read_only_fields = ['status', 'uploaded_by', 'created_at', 'updated_at', 'video_url']

    def validate_video(self, value):
        if value and value.size > 20 * 1024 * 1024:
            raise serializers.ValidationError('Video file size must be ≤ 20MB.')
        return value 