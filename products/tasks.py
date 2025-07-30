from celery import shared_task
from django.core.files.base import ContentFile
from .models import Product
import os

def process_video_file(product):
    # Move file from temporary_video to video (S3)
    if not product.temporary_video:
        return False
    try:
        # Read the file from temporary_video
        temp_file = product.temporary_video
        temp_file.open('rb')
        file_content = temp_file.read()
        temp_file.close()
        # Save to video field (triggers S3 upload)
        filename = os.path.basename(temp_file.name)
        product.video.save(filename, ContentFile(file_content), save=False)
        product.processing_status = 'READY'
        # Remove temporary_video
        product.temporary_video.delete(save=False)
        product.temporary_video = None
        product.save()
        return True
    except Exception as e:
        product.processing_status = 'FAILED'
        product.save()
        return False

@shared_task
def process_product_video(product_id):
    try:
        product = Product.objects.get(id=product_id)
        product.processing_status = 'PROCESSING'
        product.save()
        process_video_file(product)
    except Product.DoesNotExist:
        pass