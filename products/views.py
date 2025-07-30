from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.parsers import MultiPartParser, FormParser
from .models import Category, Product
from .serializers import CategorySerializer, ProductSerializer
from core.utils import IsAdmin, IsStaff, IsEndUser, IsAdminOrStaff, aes_encrypted
from .tasks import process_product_video

class CategoryListCreateView(APIView):
    permission_classes = [IsAdminOrStaff]

    def get(self, request):
        categories = Category.objects.all()
        serializer = CategorySerializer(categories, many=True)
        return Response(serializer.data)

    @aes_encrypted
    def post(self, request):
        serializer = CategorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CategoryDetailView(APIView):
    permission_classes = [IsAdminOrStaff]

    def get_object(self, pk):
        try:
            return Category.objects.get(pk=pk)
        except Category.DoesNotExist:
            return None

    def get(self, request, pk):
        category = self.get_object(pk)
        if not category:
            return Response({'detail': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)
        serializer = CategorySerializer(category)
        return Response(serializer.data)

    @aes_encrypted
    def put(self, request, pk):
        category = self.get_object(pk)
        if not category:
            return Response({'detail': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)
        serializer = CategorySerializer(category, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @aes_encrypted
    def patch(self, request, pk):
        category = self.get_object(pk)
        if not category:
            return Response({'detail': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)
        serializer = CategorySerializer(category, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @aes_encrypted
    def delete(self, request, pk):
        category = self.get_object(pk)
        if not category:
            return Response({'detail': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)
        category.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class ProductListCreateView(APIView):
    parser_classes = [MultiPartParser, FormParser]

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsEndUser()]
        return [permissions.IsAuthenticated()]

    def get(self, request):
        user = request.user
        if user.role in ['ADMIN', 'STAFF']:
            products = Product.objects.all()
        else:
            products = Product.objects.filter(uploaded_by=user)
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)

    @aes_encrypted
    def post(self, request):
        # Save uploaded file to temporary_video, not video
        data = request.data.copy()
        video_file = data.pop('video', None)
        serializer = ProductSerializer(data=data)
        if serializer.is_valid():
            product = serializer.save(uploaded_by=request.user, processing_status='UPLOADING')
            if video_file:
                product.temporary_video = video_file
                product.save()
                process_product_video.delay(product.id)
            return Response(ProductSerializer(product).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ProductDetailView(APIView):
    parser_classes = [MultiPartParser, FormParser]
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self, pk, user):
        try:
            product = Product.objects.get(pk=pk)
            if user.role in ['ADMIN', 'STAFF'] or product.uploaded_by == user:
                return product
            return None
        except Product.DoesNotExist:
            return None

    def get(self, request, pk):
        product = self.get_object(pk, request.user)
        if not product:
            return Response({'detail': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)
        serializer = ProductSerializer(product)
        return Response(serializer.data)

    @aes_encrypted
    def put(self, request, pk):
        product = self.get_object(pk, request.user)
        if not product:
            return Response({'detail': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)
        serializer = ProductSerializer(product, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @aes_encrypted
    def patch(self, request, pk):
        product = self.get_object(pk, request.user)
        if not product:
            return Response({'detail': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)
        serializer = ProductSerializer(product, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @aes_encrypted
    def delete(self, request, pk):
        product = self.get_object(pk, request.user)
        if not product:
            return Response({'detail': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)
        product.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class ProductApproveView(APIView):
    permission_classes = [IsAdminOrStaff]
    @aes_encrypted
    def post(self, request, pk):
        try:
            product = Product.objects.get(pk=pk)
        except Product.DoesNotExist:
            return Response({'detail': 'Product not found.'}, status=status.HTTP_404_NOT_FOUND)
        product.status = 'APPROVED'
        product.save()
        return Response({'detail': 'Product approved.'})

class ProductRejectView(APIView):
    permission_classes = [IsAdminOrStaff]
    @aes_encrypted
    def post(self, request, pk):
        try:
            product = Product.objects.get(pk=pk)
        except Product.DoesNotExist:
            return Response({'detail': 'Product not found.'}, status=status.HTTP_404_NOT_FOUND)
        product.status = 'REJECTED'
        product.save()
        return Response({'detail': 'Product rejected.'})

class UserProductHistoryView(APIView):
    permission_classes = [IsEndUser]
    def get(self, request):
        user = request.user
        products = Product.objects.filter(uploaded_by=user)
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data) 