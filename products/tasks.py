from celery import shared_task
import time

def process_video_file(video_path):
    # Placeholder for actual video processing logic
    print(f"Processing video: {video_path}")
    time.sleep(5)
    print(f"Finished processing video: {video_path}")

@shared_task
def process_product_video(product_id, video_path):
    process_video_file(video_path)
    return f"Processed video for product {product_id}" 