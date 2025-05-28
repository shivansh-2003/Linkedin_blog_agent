#!/usr/bin/env python3
"""
Example client for LinkedIn Blog AI Assistant API
Demonstrates how to use the API endpoints
"""

import requests
import json
from pathlib import Path

# API base URL
API_BASE = "http://localhost:8000"

def test_health():
    """Test API health endpoint"""
    print("🔍 Testing API health...")
    response = requests.get(f"{API_BASE}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    return response.status_code == 200

def process_text_example():
    """Example: Process text input"""
    print("\n📝 Testing text processing...")
    
    text_data = {
        "text": """
        I just implemented a new machine learning algorithm that improved our model accuracy by 15%. 
        The key insight was using ensemble methods combined with feature engineering. 
        This breakthrough could help many data scientists in their projects.
        """
    }
    
    response = requests.post(f"{API_BASE}/process/text", json=text_data)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print("✅ Text processed successfully!")
        print(f"Source type: {result['source_type']}")
        print(f"Extracted info: {result['extracted_info'][:200]}...")
        return result
    else:
        print(f"❌ Error: {response.text}")
        return None

def upload_file_example(file_path: str):
    """Example: Upload and process a file"""
    print(f"\n📄 Testing file upload: {file_path}")
    
    if not Path(file_path).exists():
        print(f"❌ File not found: {file_path}")
        return None
    
    with open(file_path, 'rb') as f:
        files = {'file': (Path(file_path).name, f, 'application/octet-stream')}
        response = requests.post(f"{API_BASE}/process/file", files=files)
    
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print("✅ File processed successfully!")
        print(f"Source type: {result['source_type']}")
        print(f"Extracted info: {result['extracted_info'][:200]}...")
        return result
    else:
        print(f"❌ Error: {response.text}")
        return None

def upload_presentation_example(file_path: str):
    """Example: Upload and process a presentation"""
    print(f"\n📊 Testing presentation upload: {file_path}")
    
    if not Path(file_path).exists():
        print(f"❌ File not found: {file_path}")
        return None
    
    with open(file_path, 'rb') as f:
        files = {'file': (Path(file_path).name, f, 'application/octet-stream')}
        data = {
            'analyze_images': 'true',
            'specific_slides': '1,2,3'  # Optional: only process first 3 slides
        }
        response = requests.post(f"{API_BASE}/process/presentation", files=files, data=data)
    
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print("✅ Presentation processed successfully!")
        print(f"Source type: {result['source_type']}")
        print(f"Metadata: {result.get('metadata', {})}")
        print(f"Extracted info: {result['extracted_info'][:200]}...")
        return result
    else:
        print(f"❌ Error: {response.text}")
        return None

def generate_blog_example(extraction_result):
    """Example: Generate blog post from extracted information"""
    if not extraction_result:
        print("❌ No extraction result to generate blog from")
        return None
    
    print("\n✍️ Testing blog generation...")
    
    blog_data = {
        "extracted_info": extraction_result["extracted_info"],
        "source_type": extraction_result["source_type"]
    }
    
    response = requests.post(f"{API_BASE}/generate/blog", json=blog_data)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print("✅ Blog post generated successfully!")
        print("🎯 Generated LinkedIn Post:")
        print("=" * 60)
        print(result["blog_post"])
        print("=" * 60)
        return result["blog_post"]
    else:
        print(f"❌ Error: {response.text}")
        return None

def refine_blog_example(current_post, extraction_result):
    """Example: Refine blog post with feedback"""
    if not current_post or not extraction_result:
        print("❌ Missing required data for blog refinement")
        return None
    
    print("\n🔄 Testing blog refinement...")
    
    refinement_data = {
        "current_post": current_post,
        "feedback": "Make it more technical and add specific metrics. Include a call-to-action for engagement.",
        "extracted_info": extraction_result["extracted_info"],
        "source_type": extraction_result["source_type"]
    }
    
    response = requests.post(f"{API_BASE}/refine/blog", json=refinement_data)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print("✅ Blog post refined successfully!")
        print("🎯 Refined LinkedIn Post:")
        print("=" * 60)
        print(result["blog_post"])
        print("=" * 60)
        return result["blog_post"]
    else:
        print(f"❌ Error: {response.text}")
        return None

def get_supported_formats():
    """Example: Get supported file formats"""
    print("\n📋 Getting supported formats...")
    
    response = requests.get(f"{API_BASE}/supported-formats")
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        formats = response.json()
        print("✅ Supported formats:")
        for category, extensions in formats.items():
            print(f"  {category}: {', '.join(extensions)}")
    else:
        print(f"❌ Error: {response.text}")

def main():
    """Run example API interactions"""
    print("🚀 LinkedIn Blog AI Assistant - API Client Example")
    print("=" * 60)
    
    # Test API health
    if not test_health():
        print("❌ API is not healthy. Make sure the server is running.")
        return
    
    # Get supported formats
    get_supported_formats()
    
    # Test text processing
    extraction_result = process_text_example()
    
    # Test file upload (you can uncomment and provide a real file path)
    # extraction_result = upload_file_example("example.pdf")
    
    # Test presentation upload (you can uncomment and provide a real file path)
    # extraction_result = upload_presentation_example("example.pptx")
    
    if extraction_result:
        # Generate initial blog post
        blog_post = generate_blog_example(extraction_result)
        
        if blog_post:
            # Refine the blog post
            refined_post = refine_blog_example(blog_post, extraction_result)
    
    print("\n✅ API testing completed!")
    print("\n💡 Next steps:")
    print("1. Try uploading your own files")
    print("2. Experiment with different feedback for refinement")
    print("3. Check out the interactive docs at http://localhost:8000/docs")

if __name__ == "__main__":
    main() 