import cloudinary
import cloudinary.uploader
import cloudinary.api
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import os

class CloudinaryService:
    """Service class for handling Cloudinary operations"""
    
    def __init__(self):
        # Configure Cloudinary
        cloudinary.config(
            cloud_name=settings.CLOUDINARY['cloud_name'],
            api_key=settings.CLOUDINARY['api_key'],
            api_secret=settings.CLOUDINARY['api_secret']
        )
    
    def upload_image(self, image_file, folder="tasty_fingers", public_id=None):
        """
        Upload an image to Cloudinary
        
        Args:
            image_file: File object or path to image
            folder: Cloudinary folder name
            public_id: Custom public ID for the image
            
        Returns:
            dict: Cloudinary upload response with URL and public_id
        """
        try:
            # Prepare upload parameters
            upload_params = {
                'folder': folder,
                'resource_type': 'image',
                'transformation': [
                    {'width': 800, 'height': 600, 'crop': 'fill'},
                    {'quality': 'auto', 'fetch_format': 'auto'}
                ]
            }
            
            if public_id:
                upload_params['public_id'] = public_id
            
            # Upload to Cloudinary
            result = cloudinary.uploader.upload(
                image_file,
                **upload_params
            )
            
            return {
                'success': True,
                'url': result['secure_url'],
                'public_id': result['public_id'],
                'width': result['width'],
                'height': result['height'],
                'format': result['format']
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def delete_image(self, public_id):
        """
        Delete an image from Cloudinary
        
        Args:
            public_id: Cloudinary public ID of the image
            
        Returns:
            dict: Deletion result
        """
        try:
            result = cloudinary.uploader.destroy(public_id)
            return {
                'success': True,
                'result': result
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_image_url(self, public_id, transformation=None):
        """
        Get optimized image URL with transformations
        
        Args:
            public_id: Cloudinary public ID
            transformation: Optional transformation parameters
            
        Returns:
            str: Optimized image URL
        """
        try:
            if transformation:
                url = cloudinary.CloudinaryImage(public_id).build_url(**transformation)
            else:
                url = cloudinary.CloudinaryImage(public_id).build_url()
            
            return url
        except Exception as e:
            return None
    
    def optimize_image_url(self, url, width=800, height=600, quality='auto'):
        """
        Optimize an existing Cloudinary URL with transformations
        
        Args:
            url: Existing Cloudinary URL
            width: Desired width
            height: Desired height
            quality: Image quality
            
        Returns:
            str: Optimized URL
        """
        try:
            # Extract public_id from URL
            if 'cloudinary.com' in url:
                # Parse Cloudinary URL to get public_id
                parts = url.split('/')
                if len(parts) >= 8:
                    public_id = '/'.join(parts[7:-1])  # Remove version and extension
                    return self.get_image_url(public_id, {
                        'width': width,
                        'height': height,
                        'crop': 'fill',
                        'quality': quality,
                        'fetch_format': 'auto'
                    })
            
            return url
        except Exception as e:
            return url
    
    def migrate_local_images(self, model_class, image_field_name):
        """
        Migrate local images to Cloudinary for existing models
        
        Args:
            model_class: Django model class
            image_field_name: Name of the image field
            
        Returns:
            dict: Migration results
        """
        results = {
            'success': 0,
            'failed': 0,
            'errors': []
        }
        
        try:
            # Get all instances with local images
            instances = model_class.objects.filter(
                **{f"{image_field_name}__isnull": False}
            ).exclude(
                **{f"{image_field_name}": ""}
            )
            
            for instance in instances:
                try:
                    image_field = getattr(instance, image_field_name)
                    
                    # Skip if already a Cloudinary URL
                    if image_field and 'cloudinary.com' in str(image_field):
                        continue
                    
                    # Skip if no image file
                    if not image_field or not hasattr(image_field, 'path'):
                        continue
                    
                    # Upload to Cloudinary
                    upload_result = self.upload_image(
                        image_field.path,
                        folder=f"{model_class.__name__.lower()}_images"
                    )
                    
                    if upload_result['success']:
                        # Update model with Cloudinary URL
                        setattr(instance, image_field_name, upload_result['url'])
                        instance.save()
                        results['success'] += 1
                    else:
                        results['failed'] += 1
                        results['errors'].append(f"Failed to upload {image_field.path}")
                        
                except Exception as e:
                    results['failed'] += 1
                    results['errors'].append(str(e))
            
            return results
            
        except Exception as e:
            return {
                'success': 0,
                'failed': 0,
                'errors': [str(e)]
            }

# Global instance
cloudinary_service = CloudinaryService()
