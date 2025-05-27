# image_pipeline.py

import google.generativeai as genai
from PIL import Image
import os
from typing import Dict, Any
from pathlib import Path

class ImagePipeline:
    def __init__(self, api_key: str = None):
        """Initialize the image extraction pipeline with Gemini Vision"""
        # Configure Gemini API
        genai.configure(api_key=api_key or os.getenv("GOOGLE_API_KEY"))
        self.model = genai.GenerativeModel('gemini-1.5-flash')
        
        self.extraction_prompt = """
Analyze this image and extract information that would be valuable for creating a LinkedIn blog post.

Please provide:
1. Main Subject/Topic of the image
2. Key Visual Elements and their significance
3. Any text, data, or statistics visible in the image
4. The story or message conveyed by the image
5. Professional insights that can be drawn from the image
6. How this image relates to business, technology, or professional development
7. Potential talking points for a LinkedIn audience

Format the output in a structured way focusing on professional and business insights.
If the image contains diagrams, charts, or infographics, extract all relevant data points.
"""
    
    def extract_from_image(self, image_path: str) -> Dict[str, Any]:
        """Extract information from image file"""
        try:
            # Open and process image
            image = Image.open(image_path)
            
            # Generate content using Gemini Vision
            response = self.model.generate_content([self.extraction_prompt, image])
            
            return {
                "source_type": "image",
                "file_path": image_path,
                "extracted_info": response.text,
                "status": "success"
            }
            
        except Exception as e:
            return {
                "source_type": "image",
                "file_path": image_path,
                "error": str(e),
                "status": "error"
            }
    
    def extract_from_multiple_images(self, image_paths: list) -> Dict[str, Any]:
        """Extract information from multiple images"""
        try:
            all_extractions = []
            
            for image_path in image_paths:
                result = self.extract_from_image(image_path)
                if result["status"] == "success":
                    all_extractions.append(result["extracted_info"])
            
            # Combine all extractions
            combined_prompt = f"""
Synthesize the following information extracted from multiple images into a cohesive summary 
for a LinkedIn blog post:

{chr(10).join([f"Image {i+1}: {extraction}" for i, extraction in enumerate(all_extractions)])}

Create a unified narrative that combines insights from all images.
"""
            
            response = self.model.generate_content(combined_prompt)
            
            return {
                "source_type": "multiple_images",
                "file_paths": image_paths,
                "extracted_info": response.text,
                "status": "success"
            }
            
        except Exception as e:
            return {
                "source_type": "multiple_images",
                "file_paths": image_paths,
                "error": str(e),
                "status": "error"
            }
    
    def is_supported_format(self, file_path: str) -> bool:
        """Check if the image format is supported"""
        supported_formats = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'}
        return Path(file_path).suffix.lower() in supported_formats