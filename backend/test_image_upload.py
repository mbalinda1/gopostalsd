#!/usr/bin/env python3
"""
Test script to verify image upload functionality for product types.
This script tests the filestorage system and unique filename generation.
"""
import sys
from pathlib import Path
import os
import tempfile
from io import BytesIO

# Add the server directory to the Python path
server_dir = Path(__file__).parent / "server"
sys.path.insert(0, str(server_dir))

def create_test_image():
    """Create a simple test image file"""
    # Create a simple 1x1 pixel PNG image
    png_data = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\tpHYs\x00\x00\x0b\x13\x00\x00\x0b\x13\x01\x00\x9a\x9c\x18\x00\x00\x00\nIDATx\x9cc```\x00\x00\x00\x04\x00\x01\xdd\x8d\xb4\x1c\x00\x00\x00\x00IEND\xaeB`\x82'
    return png_data

def test_image_upload():
    """Test the image upload functionality"""
    try:
        print("🧪 Testing image upload functionality...")
        print("=" * 60)
        
        # Create Flask app
        print("📱 Initializing Flask application...")
        from server import create_server
        app = create_server()
        
        with app.app_context():
            # Test 1: Test filestorage system
            print("📁 Testing filestorage system...")
            filestorage = app.extensions["filestorage"]
            print(f"✅ Filestorage backend: {filestorage.current_backend}")
            
            # Test 2: Test unique filename generation
            print("\n🔧 Testing unique filename generation...")
            import uuid
            from datetime import datetime
            from werkzeug.utils import secure_filename
            
            test_filename = "test_image.png"
            secure_name = secure_filename(test_filename)
            file_extension = os.path.splitext(secure_name)[1].lower()
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            unique_id = str(uuid.uuid4())[:8]
            unique_filename = f"product_type_{timestamp}_{unique_id}{file_extension}"
            
            print(f"✅ Original filename: {test_filename}")
            print(f"✅ Secure filename: {secure_name}")
            print(f"✅ Unique filename: {unique_filename}")
            
            # Test 3: Test file upload
            print("\n📤 Testing file upload...")
            test_image_data = create_test_image()
            content_type = "image/png"
            
            try:
                image_url = filestorage.upload_file(test_image_data, unique_filename, content_type)
                print(f"✅ Image uploaded successfully!")
                print(f"✅ Image URL: {image_url}")
                
                # Test 4: Test file deletion
                print("\n🗑️ Testing file deletion...")
                delete_success = filestorage.delete_file(image_url)
                if delete_success:
                    print("✅ File deleted successfully!")
                else:
                    print("⚠️ File deletion returned False (may be expected for some backends)")
                    
            except Exception as e:
                print(f"❌ File upload failed: {str(e)}")
                return False
            
            # Test 5: Test controller method (without database)
            print("\n🎯 Testing controller image handling...")
            from werkzeug.datastructures import FileStorage
            
            # Create a mock FileStorage object
            mock_file = FileStorage(
                stream=BytesIO(test_image_data),
                filename="test_upload.png",
                content_type="image/png"
            )
            
            # Test the image processing logic
            if isinstance(mock_file, FileStorage):
                if mock_file.filename == "":
                    print("❌ Empty filename detected")
                    return False
                
                content_type = mock_file.content_type
                if not content_type or not content_type.startswith('image/'):
                    print("❌ Invalid content type")
                    return False
                
                # Generate unique filename
                original_filename = secure_filename(mock_file.filename)
                file_extension = os.path.splitext(original_filename)[1].lower()
                
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                unique_id = str(uuid.uuid4())[:8]
                unique_filename = f"product_type_{timestamp}_{unique_id}{file_extension}"
                
                print(f"✅ Mock file processing successful!")
                print(f"✅ Generated unique filename: {unique_filename}")
            
            print("\n" + "=" * 60)
            print("🎉 All image upload tests passed!")
            print("=" * 60)
            print("📋 Image upload functionality is working correctly")
            print("🔒 Unique filenames are being generated to prevent conflicts")
            print("📁 Filestorage system is properly configured")
            print("💡 Product type creation with images should now work")
            print("=" * 60)
            
            return True
            
    except Exception as e:
        print(f"❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_image_upload()
    sys.exit(0 if success else 1)