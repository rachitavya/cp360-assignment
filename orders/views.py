from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from .models import Order
from .serializers import OrderSerializer
from core.utils import IsAdmin, IsStaff, IsEndUser, IsAdminOrStaff, aes_encrypted

# Create your views here.

class OrderListCreateView(APIView):
    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsEndUser()]
        return [permissions.IsAuthenticated()]

    def get(self, request):
        user = request.user
        if user.role in ['ADMIN', 'STAFF']:
            orders = Order.objects.all()
        else:
            orders = Order.objects.filter(user=user)
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)

    @aes_encrypted
    def post(self, request):
        serializer = OrderSerializer(data=request.data)
        if serializer.is_valid():
            order = serializer.save(user=request.user)
            return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class OrderDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self, pk, user):
        try:
            order = Order.objects.get(pk=pk)
            if user.role in ['ADMIN', 'STAFF'] or order.user == user:
                return order
            return None
        except Order.DoesNotExist:
            return None

    def get(self, request, pk):
        order = self.get_object(pk, request.user)
        if not order:
            return Response({'detail': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)
        serializer = OrderSerializer(order)
        return Response(serializer.data)

    @aes_encrypted
    def put(self, request, pk):
        order = self.get_object(pk, request.user)
        if not order:
            return Response({'detail': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)
        serializer = OrderSerializer(order, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @aes_encrypted
    def patch(self, request, pk):
        order = self.get_object(pk, request.user)
        if not order:
            return Response({'detail': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)
        serializer = OrderSerializer(order, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @aes_encrypted
    def delete(self, request, pk):
        order = self.get_object(pk, request.user)
        if not order:
            return Response({'detail': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)
        order.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
