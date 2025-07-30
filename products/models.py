from django.db import models
from users.models import User
import logging
from storages.backends.s3boto3 import S3Boto3Storage
from django.conf import settings

logger = logging.getLogger(__name__)

# Create your models here.

class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    def __str__(self):
        return self.name

class Product(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
        ('CANCELLED', 'Cancelled'),
    ]
    PROCESSING_STATUS_CHOICES = [
        ('UPLOADING', 'Uploading'),
        ('PROCESSING', 'Processing'),
        ('READY', 'Ready'),
        ('FAILED', 'Failed'),
    ]
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    video = models.FileField(upload_to='videos/', storage=S3Boto3Storage(), blank=True, null=True)
    temporary_video = models.FileField(upload_to='temp_videos/', blank=True, null=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    processing_status = models.CharField(max_length=12, choices=PROCESSING_STATUS_CHOICES, default='UPLOADING')
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='products')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    @property
    def video_url(self):
        if self.video:
            url = self.video.url
            if not url.startswith('http'):
                url = f"https://{settings.AWS_S3_CUSTOM_DOMAIN}/{self.video.name}"
            return url
        return None