#!/usr/bin/env python3
"""
Comprehensive test script for LangSmith integration with LinkedIn Blog AI Assistant
"""

import asyncio
import os
import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent))

from langsmith_config import verify_langsmith_setup
from ingestion.unified_processor import UnifiedProcessor
from blog_generation.workflow import BlogGenerationWorkflow
from blog_generation.config import BlogGenerationState, ProcessingStatus

async def test_langsmith_setup():
    """Test LangSmith configuration and connection"""
    print("🔧 Testing LangSmith Setup")
    print("=" * 50)
    
    # Check environment variables
    required_vars = ['LANGSMITH_API_KEY', 'LANGSMITH_PROJECT']
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Missing environment variables: {missing_vars}")
        print("💡 Please set them in your .env file:")
        for var in missing_vars:
            print(f"   {var}=your_value_here")
        return False
    
    # Verify LangSmith connection
    if verify_langsmith_setup():
        print("✅ LangSmith setup verified successfully!")
        print(f"📊 Project: {os.getenv('LANGSMITH_PROJECT', 'linkedin-blog-agent')}")
        return True
    else:
        print("❌ LangSmith setup verification failed")
        return False

async def test_ingestion_tracing():
    """Test ingestion system with LangSmith tracing"""
    print("\n📁 Testing Ingestion System Tracing")
    print("=" * 50)
    
    try:
        # Create a sample text file for testing
        sample_content = """
        Machine Learning Best Practices for 2024
        
        As we move into 2024, machine learning continues to evolve rapidly. 
        Here are the key best practices that every ML practitioner should follow:
        
        1. Data Quality First: Ensure your datasets are clean, diverse, and representative
        2. Model Versioning: Implement proper version control for all your models
        3. Continuous Monitoring: Set up comprehensive monitoring for model performance
        4. Ethical AI: Consider bias, fairness, and transparency in your models
        5. MLOps Integration: Automate your ML pipeline from development to production
        
        These practices will help you build more reliable and effective ML systems.
        """
        
        # Write sample file
        test_file = "test_sample.txt"
        with open(test_file, 'w') as f:
            f.write(sample_content)
        
        print(f"📝 Created test file: {test_file}")
        
        # Process file through ingestion system
        processor = UnifiedProcessor()
        result = processor.process_file(test_file)
        
        print(f"✅ File processing completed!")
        print(f"   Success: {result.success}")
        print(f"   Content Type: {result.content_type.value}")
        print(f"   AI Analysis Length: {len(result.ai_analysis) if result.ai_analysis else 0}")
        print(f"   Key Insights: {len(result.key_insights)}")
        
        # Clean up
        os.remove(test_file)
        
        return result.success
        
    except Exception as e:
        print(f"❌ Ingestion test failed: {e}")
        return False

async def test_blog_generation_tracing():
    """Test blog generation workflow with LangSmith tracing"""
    print("\n📝 Testing Blog Generation Workflow Tracing")
    print("=" * 50)
    
    try:
        # Sample content for blog generation
        sample_content = """
        The Future of AI in Business Operations
        
        Artificial Intelligence is revolutionizing how businesses operate, from automating 
        routine tasks to providing predictive insights that drive strategic decisions. 
        Companies that embrace AI early are seeing significant competitive advantages.
        
        Key benefits include:
        - Improved efficiency and reduced operational costs
        - Better customer insights and personalization
        - Predictive maintenance and quality control
        - Enhanced decision-making through data analysis
        
        The key to successful AI implementation is starting with clear business objectives
        and gradually expanding AI capabilities across different functions.
        """
        
        print("📝 Testing blog generation pipeline...")
        
        # Create blog generation workflow
        workflow = BlogGenerationWorkflow()
        
        # Create initial state
        initial_state = BlogGenerationState(
            source_content=sample_content,
            user_requirements="Create an engaging LinkedIn post for business professionals about AI trends",
            max_iterations=2,
            current_status=ProcessingStatus.GENERATING
        )
        
        # Run workflow (this will generate comprehensive traces)
        result_state = workflow.run_workflow(initial_state)
        
        print(f"✅ Blog generation completed!")
        print(f"   Status: {result_state.current_status}")
        print(f"   Iterations: {result_state.iteration_count}")
        
        if result_state.final_blog:
            print(f"   Title: {result_state.final_blog.title}")
            print(f"   Content Length: {len(result_state.final_blog.content)}")
            print(f"   Hashtags: {len(result_state.final_blog.hashtags)}")
        
        if result_state.latest_critique:
            print(f"   Quality Score: {result_state.latest_critique.quality_score}/10")
            print(f"   Quality Level: {result_state.latest_critique.quality_level}")
        
        return result_state.current_status == ProcessingStatus.COMPLETED
        
    except Exception as e:
        print(f"❌ Blog generation test failed: {e}")
        return False

async def test_api_tracing():
    """Test API endpoints with LangSmith tracing"""
    print("\n🌐 Testing API Endpoints Tracing")
    print("=" * 50)
    
    try:
        import requests
        import json
        
        # Test API health endpoint
        base_url = "http://localhost:8000"
        
        print("🏥 Testing health endpoint...")
        try:
            response = requests.get(f"{base_url}/health", timeout=5)
            if response.status_code == 200:
                print("✅ Health endpoint working")
            else:
                print(f"⚠️ Health endpoint returned {response.status_code}")
        except requests.exceptions.RequestException:
            print("⚠️ API server not running - start with: python api.py")
            return False
        
        # Test blog generation endpoint
        print("📝 Testing blog generation endpoint...")
        payload = {
            "text": "AI is transforming business operations through automation and insights.",
            "target_audience": "Business professionals",
            "tone": "Professional and engaging",
            "max_iterations": 1
        }
        
        try:
            response = requests.post(f"{base_url}/api/generate-blog", json=payload, timeout=30)
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Blog generation API working")
                print(f"   Success: {result.get('success', False)}")
                print(f"   Quality Score: {result.get('quality_score', 'N/A')}")
            else:
                print(f"⚠️ Blog generation API returned {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"⚠️ Blog generation API test failed: {e}")
        
        return True
        
    except ImportError:
        print("⚠️ requests library not available - install with: pip install requests")
        return False
    except Exception as e:
        print(f"❌ API test failed: {e}")
        return False

async def main():
    """Run all LangSmith integration tests"""
    print("🚀 LangSmith Integration Test Suite")
    print("=" * 60)
    
    # Test results
    results = {}
    
    # Test 1: LangSmith Setup
    results['setup'] = await test_langsmith_setup()
    
    # Test 2: Ingestion Tracing
    results['ingestion'] = await test_ingestion_tracing()
    
    # Test 3: Blog Generation Tracing
    results['blog_generation'] = await test_blog_generation_tracing()
    
    # Test 4: API Tracing
    results['api'] = await test_api_tracing()
    
    # Summary
    print("\n" + "=" * 60)
    print("🎯 Test Summary")
    print("=" * 60)
    
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{test_name.upper():<20} {status}")
    
    total_passed = sum(results.values())
    total_tests = len(results)
    
    print(f"\n📊 Overall: {total_passed}/{total_tests} tests passed")
    
    if total_passed == total_tests:
        print("\n🎉 All tests passed! LangSmith integration is working correctly.")
        print(f"\n🔍 Check your LangSmith dashboard at: https://smith.langchain.com")
        print(f"   Project: {os.getenv('LANGSMITH_PROJECT', 'linkedin-blog-agent')}")
        print(f"   Look for traces from this test run!")
    else:
        print(f"\n⚠️ {total_tests - total_passed} test(s) failed. Check the output above for details.")
    
    return total_passed == total_tests

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
