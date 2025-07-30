from rest_framework.permissions import BasePermission
from functools import wraps
from rest_framework.response import Response
from .aes_utils import encrypt_data, decrypt_data

class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'ADMIN'

class IsStaff(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'STAFF'

class IsEndUser(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'END_USER'

class IsAdminOrStaff(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in ['ADMIN', 'STAFF']

class IsAdminStaffOrEndUser(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role in ['ADMIN', 'STAFF', 'ENDUSER']
        )

def aes_encrypted(view_func):
    @wraps(view_func)
    def _wrapped_view(self, request, *args, **kwargs):
        if hasattr(request, 'data') and isinstance(request.data, dict) and 'data' in request.data:
            try:
                request._full_data = decrypt_data(request.data['data'])
            except Exception:
                return Response({'detail': 'Invalid encrypted data.'}, status=400)
        response = view_func(self, request, *args, **kwargs)
        if isinstance(response, Response) and response.data is not None:
            response.data = {'data': encrypt_data(response.data)}
        return response
    return _wrapped_view 