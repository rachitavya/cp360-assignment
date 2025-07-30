from celery import shared_task
from django.core.files.base import ContentFile
from .models import Product
import os
import logging
from django.conf import settings
import boto3

logger = logging.getLogger(__name__)

def verify_aws_credentials():
    """Verify AWS credentials are working"""
    try:
        s3 = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_S3_REGION_NAME
        )
        s3.list_objects_v2(Bucket=settings.AWS_STORAGE_BUCKET_NAME, MaxKeys=1)
        return True
    except Exception as e:
        logger.error(f"AWS Credential verification failed: {str(e)}")
        return False

def process_video_file(product):
    if not product.temporary_video:
        logger.error(f"No temporary video found for product {product.id}")
        return False
    try:
        if not verify_aws_credentials():
            raise Exception("AWS credentials verification failed")
            
        temp_file = product.temporary_video
        temp_file.open('rb')
        file_content = temp_file.read()
        temp_file.close()
        
        filename = os.path.basename(temp_file.name)
        product.video.save(filename, ContentFile(file_content), save=False)
        
        # Verify the file exists in S3
        s3 = boto3.client('s3')
        try:
            s3.head_object(Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=product.video.name)
        except Exception as e:
            logger.error(f"File not found in S3: {str(e)}")
            raise Exception("File upload verification failed")
        
        product.processing_status = 'READY'
        product.temporary_video.delete(save=False)
        product.temporary_video = None
        product.save()
        return True
    except Exception as e:
        logger.error(f"Error processing video for product {product.id}: {str(e)}")
        product.processing_status = 'FAILED'
        product.save()
        return False

@shared_task
def process_product_video(product_id):
    try:
        product = Product.objects.get(id=product_id)
        product.processing_status = 'PROCESSING'
        product.save()
        
        success = process_video_file(product)
        if not success:
            logger.error(f"Video processing failed for product {product_id}")
    except Product.DoesNotExist:
        logger.error(f"Product {product_id} not found")
    except Exception as e:
        logger.error(f"Unexpected error in Celery task for product {product_id}: {str(e)}")