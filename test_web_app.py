#!/usr/bin/env python3
"""
Simple test script for the web application.
"""

import requests
import time
import json

def test_web_app():
    """Test the web application functionality."""
    base_url = "http://localhost:5000"
    
    print("🧪 Testing PubMed Paper Finder Web App")
    print("=" * 50)
    
    # Test 1: Health check
    print("1. Testing health check...")
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code == 200:
            print("✅ Health check passed")
        else:
            print("❌ Health check failed")
            return False
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        print("Make sure the web app is running: python app.py")
        return False
    
    # Test 2: Search functionality
    print("\n2. Testing search functionality...")
    search_data = {
        "query": "Pfizer",
        "max_results": 5,
        "email": "test@example.com",
        "debug": True
    }
    
    try:
        response = requests.post(f"{base_url}/search", json=search_data, timeout=10)
        if response.status_code == 200:
            search_result = response.json()
            search_id = search_result.get('search_id')
            print(f"✅ Search started with ID: {search_id}")
            
            # Test 3: Status checking
            print("\n3. Testing status checking...")
            max_attempts = 30
            for attempt in range(max_attempts):
                time.sleep(2)
                status_response = requests.get(f"{base_url}/status/{search_id}", timeout=5)
                if status_response.status_code == 200:
                    status_data = status_response.json()
                    print(f"   Status: {status_data.get('status')} - {status_data.get('progress')}")
                    
                    if status_data.get('status') == 'completed':
                        results = status_data.get('results', {})
                        summary = results.get('summary', {})
                        papers = results.get('papers', [])
                        
                        print(f"✅ Search completed successfully!")
                        print(f"   Total papers found: {summary.get('total_papers', 0)}")
                        print(f"   Papers with industry authors: {summary.get('papers_with_industry', 0)}")
                        print(f"   Papers shown: {summary.get('papers_shown', 0)}")
                        print(f"   Industry authors found: {summary.get('total_industry_authors', 0)}")
                        
                        if papers:
                            print(f"   First paper: {papers[0].get('title', 'N/A')[:50]}...")
                        
                        return True
                    elif status_data.get('status') == 'error':
                        print(f"❌ Search failed: {status_data.get('error')}")
                        return False
                else:
                    print(f"❌ Status check failed: {status_response.status_code}")
                    return False
            
            print("❌ Search timed out")
            return False
            
        else:
            print(f"❌ Search failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Search test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_web_app()
    if success:
        print("\n🎉 All tests passed! Web app is working correctly.")
    else:
        print("\n❌ Some tests failed. Check the web app.")
