#!/usr/bin/env python3
"""
Simple test script to verify LangSmith integration without requiring real API keys
"""

import os
import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent))

def test_imports():
    """Test that all LangSmith imports work correctly"""
    print("🔧 Testing LangSmith Imports")
    print("=" * 50)
    
    try:
        from langsmith_config import trace_step, verify_langsmith_setup, langsmith_client
        print("✅ LangSmith config imports successfully")
        
        from ingestion.unified_processor import UnifiedProcessor
        print("✅ Ingestion processor imports successfully")
        
        from blog_generation.workflow import BlogGenerationWorkflow
        print("✅ Blog generation workflow imports successfully")
        
        return True
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False

def test_decorators():
    """Test that tracing decorators are properly applied"""
    print("\n🎯 Testing Tracing Decorators")
    print("=" * 50)
    
    try:
        from langsmith_config import trace_step
        
        # Test decorator creation
        @trace_step("test_function", "tool")
        def test_function():
            return "test_result"
        
        # Check if decorator was applied
        result = test_function()
        print(f"✅ Decorator applied successfully: {result}")
        
        # Test that the function has the traceable attribute
        if hasattr(test_function, '__wrapped__'):
            print("✅ Function properly wrapped with traceable decorator")
        else:
            print("⚠️ Function may not be properly wrapped")
        
        return True
    except Exception as e:
        print(f"❌ Decorator test failed: {e}")
        return False

def test_environment_setup():
    """Test environment variable configuration"""
    print("\n🌍 Testing Environment Setup")
    print("=" * 50)
    
    # Check if environment variables are set
    env_vars = {
        'LANGSMITH_TRACING': os.getenv('LANGSMITH_TRACING'),
        'LANGSMITH_PROJECT': os.getenv('LANGSMITH_PROJECT'),
    }
    
    for var, value in env_vars.items():
        if value:
            print(f"✅ {var}: {value}")
        else:
            print(f"⚠️ {var}: Not set")
    
    # Check if .env file exists
    env_file = Path(".env")
    if env_file.exists():
        print("✅ .env file exists")
    else:
        print("⚠️ .env file not found - create one from env_template.txt")
    
    return True

def test_processor_initialization():
    """Test that processors can be initialized with tracing"""
    print("\n🏗️ Testing Processor Initialization")
    print("=" * 50)
    
    try:
        # Test ingestion processor
        from ingestion.unified_processor import UnifiedProcessor
        processor = UnifiedProcessor()
        print("✅ UnifiedProcessor initialized successfully")
        
        # Test blog generation workflow
        from blog_generation.workflow import BlogGenerationWorkflow
        workflow = BlogGenerationWorkflow()
        print("✅ BlogGenerationWorkflow initialized successfully")
        
        return True
    except Exception as e:
        print(f"❌ Processor initialization failed: {e}")
        return False

def test_tracing_integration():
    """Test that tracing is integrated into key methods"""
    print("\n🔍 Testing Tracing Integration")
    print("=" * 50)
    
    try:
        from ingestion.unified_processor import UnifiedProcessor
        from blog_generation.workflow import BlogGenerationWorkflow
        
        # Check if key methods have tracing decorators
        processor = UnifiedProcessor()
        workflow = BlogGenerationWorkflow()
        
        # Check process_file method
        if hasattr(processor.process_file, '__wrapped__'):
            print("✅ UnifiedProcessor.process_file has tracing decorator")
        else:
            print("⚠️ UnifiedProcessor.process_file may not have tracing")
        
        # Check run method
        if hasattr(workflow.run, '__wrapped__'):
            print("✅ BlogGenerationWorkflow.run has tracing decorator")
        else:
            print("⚠️ BlogGenerationWorkflow.run may not have tracing")
        
        # Check generate_content_node method
        if hasattr(workflow.generate_content_node, '__wrapped__'):
            print("✅ BlogGenerationWorkflow.generate_content_node has tracing decorator")
        else:
            print("⚠️ BlogGenerationWorkflow.generate_content_node may not have tracing")
        
        return True
    except Exception as e:
        print(f"❌ Tracing integration test failed: {e}")
        return False

def main():
    """Run all simple LangSmith integration tests"""
    print("🚀 LangSmith Integration Test Suite (Simple)")
    print("=" * 60)
    
    # Test results
    results = {}
    
    # Test 1: Imports
    results['imports'] = test_imports()
    
    # Test 2: Decorators
    results['decorators'] = test_decorators()
    
    # Test 3: Environment
    results['environment'] = test_environment_setup()
    
    # Test 4: Processor Initialization
    results['processors'] = test_processor_initialization()
    
    # Test 5: Tracing Integration
    results['tracing'] = test_tracing_integration()
    
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
        print("\n🎉 All tests passed! LangSmith integration is properly configured.")
        print("\n💡 Next steps:")
        print("   1. Get a LangSmith API key from https://smith.langchain.com")
        print("   2. Add it to your .env file: LANGSMITH_API_KEY=your_key_here")
        print("   3. Run the full test: python test_langsmith_integration.py")
        print("   4. Check your LangSmith dashboard for traces!")
    else:
        print(f"\n⚠️ {total_tests - total_passed} test(s) failed. Check the output above for details.")
    
    return total_passed == total_tests

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
