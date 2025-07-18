#!/usr/bin/env python3
"""
Test script for FastAPI endpoints
Tests the converted FastAPI endpoints to ensure they work correctly
"""

import requests
import json

# Configuration
ODOO_URL = 'http://localhost:10017'
FASTAPI_BASE_URL = f'{ODOO_URL}/api/attendance'

def test_endpoints():
    """Test the FastAPI endpoints"""
    
    print("🧪 Testing FastAPI Endpoints")
    print("=" * 50)
    
    # Test endpoints
    endpoints_to_test = [
        {
            'name': 'Get Person Types',
            'method': 'GET',
            'url': f'{FASTAPI_BASE_URL}/person-types',
            'expected_status': 200
        },
        {
            'name': 'Get Locations', 
            'method': 'GET',
            'url': f'{FASTAPI_BASE_URL}/locations',
            'expected_status': 200
        },
        {
            'name': 'Get Current Attendance',
            'method': 'GET', 
            'url': f'{FASTAPI_BASE_URL}/current',
            'expected_status': 200
        }
    ]
    
    for test in endpoints_to_test:
        print(f"\n🔍 Testing: {test['name']}")
        print(f"   URL: {test['url']}")
        
        try:
            if test['method'] == 'GET':
                response = requests.get(test['url'])
            elif test['method'] == 'POST':
                response = requests.post(test['url'], json=test.get('data', {}))
            
            print(f"   Status: {response.status_code}")
            
            if response.status_code == test['expected_status']:
                print(f"   ✅ SUCCESS")
                
                # Try to parse JSON response
                try:
                    data = response.json()
                    if isinstance(data, dict) and 'success' in data:
                        print(f"   📊 Success: {data.get('success')}")
                        if 'data' in data and isinstance(data['data'], list):
                            print(f"   📝 Records: {len(data['data'])}")
                    else:
                        print(f"   📄 Response: {str(data)[:100]}...")
                except:
                    print(f"   📄 Response: {response.text[:100]}...")
            else:
                print(f"   ❌ FAILED - Expected {test['expected_status']}, got {response.status_code}")
                print(f"   📄 Response: {response.text[:200]}...")
                
        except requests.exceptions.ConnectionError:
            print(f"   ❌ CONNECTION ERROR - Is Odoo running?")
        except Exception as e:
            print(f"   ❌ ERROR: {str(e)}")

def test_swagger_ui():
    """Test if Swagger UI is accessible"""
    
    print(f"\n🎨 Testing Swagger UI")
    print("=" * 50)
    
    swagger_urls = [
        f'{FASTAPI_BASE_URL}/docs',
        f'{FASTAPI_BASE_URL}/openapi.json',
        f'{ODOO_URL}/api/docs',
        f'{ODOO_URL}/api/openapi.json'
    ]
    
    for url in swagger_urls:
        print(f"\n🔍 Testing: {url}")
        try:
            response = requests.get(url)
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                print(f"   ✅ SUCCESS - Swagger UI accessible!")
                if 'openapi.json' in url:
                    try:
                        openapi_spec = response.json()
                        print(f"   📊 OpenAPI Version: {openapi_spec.get('openapi', 'Unknown')}")
                        print(f"   📝 Title: {openapi_spec.get('info', {}).get('title', 'Unknown')}")
                        paths = openapi_spec.get('paths', {})
                        print(f"   🛣️  Endpoints: {len(paths)}")
                    except:
                        print(f"   📄 Valid JSON response")
                break
            else:
                print(f"   ❌ Not accessible")
                
        except requests.exceptions.ConnectionError:
            print(f"   ❌ CONNECTION ERROR")
        except Exception as e:
            print(f"   ❌ ERROR: {str(e)}")

def main():
    """Main test function"""
    
    print("🚀 FastAPI Endpoint Testing")
    print("=" * 60)
    print("Testing converted HTTP routes to FastAPI endpoints")
    print("Checking if Swagger UI is working")
    print("=" * 60)
    
    # Test basic endpoints
    test_endpoints()
    
    # Test Swagger UI
    test_swagger_ui()
    
    print("\n" + "=" * 60)
    print("🎯 Test Summary:")
    print("✅ If endpoints return 200 status, conversion was successful")
    print("🎨 If Swagger UI is accessible, documentation is working")
    print("🔧 If tests fail, check Odoo logs and module installation")
    print("=" * 60)

if __name__ == "__main__":
    main()
