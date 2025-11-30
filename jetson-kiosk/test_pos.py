#!/usr/bin/env python3
"""
POS System Test Script
Tests YOLO detection, camera, and API endpoints
"""

import sys
import requests
import cv2
import time
from pathlib import Path

def print_header(text):
    print("\n" + "="*60)
    print(f"  {text}")
    print("="*60)

def test_imports():
    """Test required Python packages"""
    print_header("Testing Python Imports")
    
    required_packages = [
        ('cv2', 'OpenCV'),
        ('fastapi', 'FastAPI'),
        ('uvicorn', 'Uvicorn'),
        ('numpy', 'NumPy'),
    ]
    
    optional_packages = [
        ('ultralytics', 'Ultralytics YOLO'),
        ('torch', 'PyTorch'),
    ]
    
    all_good = True
    
    for module, name in required_packages:
        try:
            __import__(module)
            print(f"✅ {name}: OK")
        except ImportError:
            print(f"❌ {name}: NOT FOUND")
            all_good = False
    
    for module, name in optional_packages:
        try:
            __import__(module)
            print(f"✅ {name}: OK")
        except ImportError:
            print(f"⚠️  {name}: NOT FOUND (optional, but recommended)")
    
    return all_good

def test_camera():
    """Test camera access"""
    print_header("Testing Camera Access")
    
    camera_indices = [0, 1, 2]
    found_camera = False
    
    for idx in camera_indices:
        cap = cv2.VideoCapture(idx)
        if cap.isOpened():
            ret, frame = cap.read()
            if ret:
                h, w = frame.shape[:2]
                print(f"✅ Camera {idx}: Found ({w}x{h})")
                found_camera = True
                cap.release()
                break
            cap.release()
    
    if not found_camera:
        print("❌ No camera found on indices 0-2")
        return False
    
    return True

def test_yolo():
    """Test YOLO model loading"""
    print_header("Testing YOLO Model")
    
    try:
        from ultralytics import YOLO
        print("Loading YOLO model...")
        model = YOLO('yolov8n.pt')
        print("✅ YOLO model loaded successfully")
        
        # Test inference on dummy image
        import numpy as np
        dummy_img = np.zeros((640, 640, 3), dtype=np.uint8)
        
        print("Running test inference...")
        start = time.time()
        results = model(dummy_img, verbose=False)
        inference_time = (time.time() - start) * 1000
        
        print(f"✅ Test inference completed: {inference_time:.1f}ms")
        
        if inference_time < 500:
            print("✅ Inference speed: EXCELLENT (<500ms)")
        elif inference_time < 1000:
            print("⚠️  Inference speed: OK (500-1000ms)")
        else:
            print("⚠️  Inference speed: SLOW (>1000ms) - consider optimization")
        
        return True
        
    except ImportError:
        print("❌ Ultralytics YOLO not installed")
        print("   Install with: pip install ultralytics")
        return False
    except Exception as e:
        print(f"❌ YOLO test failed: {e}")
        return False

def test_server(base_url="http://localhost:8000"):
    """Test server endpoints"""
    print_header("Testing Server Endpoints")
    
    print(f"Base URL: {base_url}")
    print("\nMake sure the server is running!")
    print("Start with: python server.py\n")
    
    time.sleep(1)
    
    endpoints = [
        ("/health", "Health Check"),
        ("/api/info", "Server Info"),
        ("/api/cart", "Cart Status"),
        ("/api/products", "Products Database"),
    ]
    
    all_good = True
    
    for endpoint, name in endpoints:
        try:
            response = requests.get(f"{base_url}{endpoint}", timeout=5)
            if response.status_code == 200:
                print(f"✅ {name} ({endpoint}): OK")
                if endpoint == "/api/info":
                    data = response.json()
                    print(f"   Server: {data.get('server')}")
                    print(f"   Resolution: {data.get('resolution')}")
                    print(f"   YOLO: {'Available' if data.get('yolo_available') else 'Not Available'}")
            else:
                print(f"❌ {name} ({endpoint}): HTTP {response.status_code}")
                all_good = False
        except requests.exceptions.ConnectionError:
            print(f"❌ {name} ({endpoint}): Server not reachable")
            print("   Make sure server is running: python server.py")
            all_good = False
            break
        except Exception as e:
            print(f"❌ {name} ({endpoint}): {e}")
            all_good = False
    
    return all_good

def test_detection_api(base_url="http://localhost:8000"):
    """Test detection endpoint"""
    print_header("Testing Detection API")
    
    try:
        print("Calling /api/detect endpoint...")
        start = time.time()
        response = requests.get(f"{base_url}/api/detect", timeout=10)
        request_time = (time.time() - start) * 1000
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Detection API: OK")
            print(f"   Request time: {request_time:.1f}ms")
            print(f"   Inference time: {data.get('inference_time_ms', 0):.1f}ms")
            print(f"   Detections: {len(data.get('detections', []))}")
            
            if data.get('detections'):
                print("\n   Detected items:")
                for det in data['detections'][:3]:  # Show first 3
                    print(f"   - {det.get('name')}: ${det.get('price')} ({det.get('confidence', 0):.2f})")
            
            return True
        else:
            print(f"❌ Detection API: HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Detection API failed: {e}")
        return False

def test_cart_api(base_url="http://localhost:8000"):
    """Test cart operations"""
    print_header("Testing Cart API")
    
    try:
        # Clear cart first
        requests.post(f"{base_url}/api/cart/clear")
        
        # Add test item
        test_item = {
            "name": "Test Product",
            "price": 9.99,
            "category": "Test",
            "quantity": 2
        }
        
        print("Adding test item to cart...")
        response = requests.post(
            f"{base_url}/api/cart/add",
            json=test_item
        )
        
        if response.status_code == 200:
            print("✅ Add to cart: OK")
        else:
            print(f"❌ Add to cart failed: HTTP {response.status_code}")
            return False
        
        # Get cart
        print("Fetching cart...")
        response = requests.get(f"{base_url}/api/cart")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Get cart: OK")
            print(f"   Items: {data.get('total_items')}")
            print(f"   Total: ${data.get('total_price')}")
        
        # Clear cart
        print("Clearing cart...")
        response = requests.post(f"{base_url}/api/cart/clear")
        if response.status_code == 200:
            print("✅ Clear cart: OK")
        
        return True
        
    except Exception as e:
        print(f"❌ Cart API failed: {e}")
        return False

def test_files():
    """Check required files exist"""
    print_header("Checking Required Files")
    
    required_files = [
        'server.py',
        'requirements.txt',
        'web/pos.html',
        'web/index.html',
    ]
    
    all_good = True
    
    for file_path in required_files:
        path = Path(file_path)
        if path.exists():
            print(f"✅ {file_path}: Found")
        else:
            print(f"❌ {file_path}: NOT FOUND")
            all_good = False
    
    return all_good

def main():
    print("\n" + "🚀 JETSON POS SYSTEM - DIAGNOSTIC TEST ".center(60, "="))
    print("\nThis script will test all components of the POS system\n")
    
    # Track results
    results = {}
    
    # Run tests
    results['files'] = test_files()
    results['imports'] = test_imports()
    results['camera'] = test_camera()
    results['yolo'] = test_yolo()
    
    # Server tests (optional - only if server is running)
    print("\n" + "="*60)
    print("SERVER TESTS (requires running server)")
    print("="*60)
    response = input("\nIs the server running? (y/n): ").lower().strip()
    
    if response == 'y':
        results['server'] = test_server()
        if results['server']:
            results['detection'] = test_detection_api()
            results['cart'] = test_cart_api()
    else:
        print("\nSkipping server tests.")
        print("To test server endpoints, run:")
        print("  1. python server.py")
        print("  2. python test_pos.py")
    
    # Summary
    print_header("TEST SUMMARY")
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name.upper()}")
    
    print(f"\nResult: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! System is ready to use.")
        print("\nNext steps:")
        print("  1. Start server: python server.py")
        print("  2. Open browser: http://localhost:8000/pos.html")
    else:
        print("\n⚠️  Some tests failed. Please review errors above.")
        print("\nCommon fixes:")
        print("  - Install missing packages: pip install -r requirements.txt")
        print("  - Check camera connection: ls /dev/video*")
        print("  - Verify server is running: python server.py")
    
    return 0 if passed == total else 1

if __name__ == "__main__":
    sys.exit(main())
