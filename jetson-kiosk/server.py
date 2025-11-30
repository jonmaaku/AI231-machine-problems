"""
Enhanced FastAPI POS System with YOLO Object Detection
Real-time product scanning with <0.5s latency for Jetson Orin Kiosk mode
"""

from fastapi import FastAPI, Response
from fastapi.responses import StreamingResponse, HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import cv2
import asyncio
from typing import Generator, Dict, List, Optional
import logging
from pathlib import Path
import numpy as np
from datetime import datetime
import time
from collections import defaultdict

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# YOLO imports
try:
    from ultralytics import YOLO
    YOLO_AVAILABLE = True
except ImportError:
    YOLO_AVAILABLE = False
    logger.warning("Ultralytics YOLO not installed. Install with: pip install ultralytics")

app = FastAPI(title="Jetson POS System")

# Camera configuration
CAMERA_INDEX = 1  # USB camera index (usually 0, adjust if needed)
VGA_WIDTH = 1080
VGA_HEIGHT = 720
FPS = 60

# YOLO configuration
YOLO_MODEL = "best.pt"  # Nano model for speed (can use yolov8s.pt, yolov11n.pt)
CONFIDENCE_THRESHOLD = 0.5
IOU_THRESHOLD = 0.45
INFERENCE_SIZE = 640  # Input size for YOLO

# Product database (mapping class IDs to products with prices)
PRODUCT_DATABASE = {
    "coffee_nescafe": {"name": "Nescafe Coffee", "price": 5.00, "category": "Beverages"},
    "coffee_kopiko": {"name": "Kopiko Coffee", "price": 3.50, "category": "Beverages"},
    "Lucky-Me-Pancit-Canton": {"name": "Lucky Me Pancit Canton", "price": 0.75, "category": "Food"},
    "Coke-in-can": {"name": "Coke in Can", "price": 1.25, "category": "Beverages"},
    "Alaska-Milk": {"name": "Alaska Milk", "price": 1.50, "category": "Dairy"},
    "Century-Tuna": {"name": "Century Tuna", "price": 2.00, "category": "Canned Goods"},
    "VCut-Spicy-Barbeque": {"name": "V-Cut Spicy Barbeque", "price": 1.00, "category": "Snacks"},
    "Selecta-Cornetto": {"name": "Selecta Cornetto", "price": 1.50, "category": "Desserts"},
    "Nestle-Yogurt": {"name": "Nestle Yogurt", "price": 2.00, "category": "Dairy"},
    "Femme-Bathroom-Tissue": {"name": "Femme Bathroom Tissue", "price": 0.75, "category": "Household"},
    "Maya-Champorado": {"name": "Maya Champorado", "price": 1.25, "category": "Food"},
    "JnJ-Potato-Chips": {"name": "JnJ Potato Chips", "price": 1.50, "category": "Snacks"},
    "Nivea-Deodorant": {"name": "Nivea Deodorant", "price": 3.00, "category": "Personal Care"},
    "UFC-Canned-Mushroom": {"name": "UFC Canned Mushroom", "price": 1.75, "category": "Canned Goods"},
    "Libbys-Vienna-Sausage-can": {"name": "Libby's Vienna Sausage", "price": 1.50, "category": "Canned Goods"},
    "Stik-O": {"name": "Stik-O", "price": 0.50, "category": "Snacks"},
    "NissinCupNoodles": {"name": "Nissin Cup Noodles", "price": 1.00, "category": "Food"},
    "Dewberry-Strawberry": {"name": "Dewberry Strawberry", "price": 0.75, "category": "Snacks"},
    "Smart-C": {"name": "Smart C", "price": 1.25, "category": "Beverages"},
    "Pineapple-juice-can": {"name": "Pineapple Juice Can", "price": 1.50, "category": "Beverages"},
    "Nestle-Chuckie": {"name": "Nestle Chuckie", "price": 1.00, "category": "Dairy"},
    "Delight-Probiotic-Drink": {"name": "Delight Probiotic Drink", "price": 1.25, "category": "Dairy"},
    "Summit-Drinking-Water": {"name": "Summit Drinking Water", "price": 0.50, "category": "Beverages"},
    "almond_milk": {"name": "Almond Milk", "price": 3.00, "category": "Dairy"},
    "Piknik": {"name": "Piknik", "price": 1.50, "category": "Snacks"},
    "Rambutan": {"name": "Rambutan", "price": 2.00, "category": "Fruits"},
    "HS-Shampoo": {"name": "Head & Shoulders Shampoo", "price": 3.50, "category": "Personal Care"},
    "irish-spring-soap": {"name": "Irish Spring Soap", "price": 1.25, "category": "Personal Care"},
    "c2_na_green": {"name": "C2 Green Tea", "price": 1.00, "category": "Beverages"},
    "colgate_toothpaste": {"name": "Colgate Toothpaste", "price": 2.50, "category": "Personal Care"},
    "555-sardines": {"name": "555 Sardines", "price": 1.00, "category": "Canned Goods"},
    "meadows-truffle": {"name": "Meadows Truffle", "price": 4.00, "category": "Snacks"},
    "double-black": {"name": "Double Black Coffee", "price": 2.50, "category": "Beverages"},
    "NongshimCupNoodles": {"name": "Nongshim Cup Noodles", "price": 1.75, "category": "Food"},
    "Close": {"name": "Close-Up Toothpaste", "price": 2.25, "category": "Personal Care"},
    "Open": {"name": "Open Product", "price": 0.00, "category": "Miscellaneous"}
}
# Global objects
camera = None
yolo_model = None
cart_items = []
detection_history = defaultdict(int)  # Track detection frequency for stability

# Get the directory where this script is located
BASE_DIR = Path(__file__).resolve().parent
WEB_DIR = BASE_DIR / "web"


def load_yolo_model():
    """Load and initialize YOLO model with TensorRT optimization if available"""
    global yolo_model
    
    if not YOLO_AVAILABLE:
        logger.warning("YOLO not available - running in camera-only mode")
        return None
    
    if yolo_model is None:
        try:
            logger.info(f"Loading YOLO model: {YOLO_MODEL}")
            yolo_model = YOLO(YOLO_MODEL)
            
            # Try to export to TensorRT for Jetson optimization
            try:
                logger.info("Attempting TensorRT optimization for Jetson...")
                # This will create a .engine file for faster inference
                yolo_model.export(format='engine', device=0, half=True)
                logger.info("TensorRT optimization successful")
            except Exception as e:
                logger.info(f"TensorRT export skipped: {e}")
            
            logger.info("YOLO model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load YOLO model: {e}")
            return None
    
    return yolo_model


def get_camera():
    """Initialize and return camera object"""
    global camera
    if camera is None or not camera.isOpened():
        camera = cv2.VideoCapture(CAMERA_INDEX)
        camera.set(cv2.CAP_PROP_FRAME_WIDTH, VGA_WIDTH)
        camera.set(cv2.CAP_PROP_FRAME_HEIGHT, VGA_HEIGHT)
        camera.set(cv2.CAP_PROP_FPS, FPS)
        
        if not camera.isOpened():
            logger.error(f"Failed to open camera at index {CAMERA_INDEX}")
            raise RuntimeError("Could not open camera")
        
        logger.info(f"Camera opened: {VGA_WIDTH}x{VGA_HEIGHT} @ {FPS}fps")
    
    return camera

model = load_yolo_model()
def detect_products(frame: np.ndarray) -> tuple[np.ndarray, List[Dict], float]:
    """
    Perform YOLO detection on frame and return annotated frame with detections
    Returns: (annotated_frame, detections_list, inference_time)
    """
    
    if model is None:
        return frame, [], 0.0
    
    start_time = time.time()
    
    try:
        # Run inference
        results = model(frame, conf=CONFIDENCE_THRESHOLD, iou=IOU_THRESHOLD, 
                       imgsz=INFERENCE_SIZE, verbose=False)[0]
        
        detections = []
        
        # Process detections
        if results.boxes is not None:
            for box in results.boxes:
                class_id = int(box.cls[0])
                confidence = float(box.conf[0])
                class_name = results.names[class_id]
                
                # Only process items in our product database
                if class_name in PRODUCT_DATABASE:
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    
                    product_info = PRODUCT_DATABASE[class_name].copy()
                    product_info.update({
                        "class_name": class_name,
                        "confidence": confidence,
                        "bbox": [x1, y1, x2, y2]
                    })
                    
                    detections.append(product_info)
                    
                    # Draw bounding box
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    
                    # Draw label with price
                    label = f"{product_info['name']} ${product_info['price']:.2f}"
                    label_size, _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)
                    cv2.rectangle(frame, (x1, y1 - label_size[1] - 10), 
                                (x1 + label_size[0], y1), (0, 255, 0), -1)
                    cv2.putText(frame, label, (x1, y1 - 5), 
                              cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)
        
        inference_time = time.time() - start_time
        
        # Draw inference time on frame
        fps_text = f"Inference: {inference_time*1000:.1f}ms"
        cv2.putText(frame, fps_text, (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        return frame, detections, inference_time
        
    except Exception as e:
        logger.error(f"Detection error: {e}")
        return frame, [], 0.0


def generate_frames() -> Generator[bytes, None, None]:
    """Generate frame bytes for MJPEG stream with YOLO detection"""
    cam = get_camera()
    
    while True:
        success, frame = cam.read()
        if not success:
            logger.warning("Failed to read frame from camera")
            break
        
        # Perform detection
        frame, detections, inference_time = detect_products(frame)
        
        # Add FPS counter
        fps_text = f"FPS: {int(1000/max(inference_time*1000, 1))}"
        cv2.putText(frame, fps_text, (10, 60), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        # Encode frame as JPEG
        ret, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
        if not ret:
            continue
        
        frame_bytes = buffer.tobytes()
        
        # Yield frame in multipart format
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')


@app.get("/video_feed")
async def video_feed():
    """MJPEG video stream endpoint"""
    return StreamingResponse(
        generate_frames(),
        media_type="multipart/x-mixed-replace; boundary=frame"
    )


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        cam = get_camera()
        success, _ = cam.read()
        return {
            "status": "healthy" if success else "unhealthy",
            "camera": "connected" if cam.isOpened() else "disconnected",
            "resolution": f"{VGA_WIDTH}x{VGA_HEIGHT}",
            "fps": FPS
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


@app.get("/api/info")
async def get_info():
    """Get camera and server information"""
    return {
        "server": "Jetson Orin POS System",
        "resolution": f"{VGA_WIDTH}x{VGA_HEIGHT}",
        "fps": FPS,
        "camera_index": CAMERA_INDEX,
        "yolo_available": YOLO_AVAILABLE,
        "yolo_model": YOLO_MODEL if YOLO_AVAILABLE else None
    }


@app.get("/api/detect")
async def detect_once():
    """Perform single detection on current frame"""
    try:
        cam = get_camera()
        success, frame = cam.read()
        
        if not success:
            return JSONResponse({"error": "Failed to capture frame"}, status_code=500)
        
        _, detections, inference_time = detect_products(frame)
        
        return {
            "detections": detections,
            "inference_time_ms": round(inference_time * 1000, 2),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


@app.post("/api/cart/add")
async def add_to_cart(item: Dict):
    """Add item to shopping cart"""
    global cart_items
    
    try:
        # Check if item already exists in cart
        existing_item = next((i for i in cart_items if i["name"] == item["name"]), None)
        
        if existing_item:
            existing_item["quantity"] += item.get("quantity", 1)
        else:
            cart_items.append({
                "name": item["name"],
                "price": item["price"],
                "category": item.get("category", "Unknown"),
                "quantity": item.get("quantity", 1),
                "added_at": datetime.now().isoformat()
            })
        
        return {"success": True, "cart": cart_items}
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


@app.post("/api/cart/remove")
async def remove_from_cart(item_name: str):
    """Remove item from shopping cart"""
    global cart_items
    
    cart_items = [item for item in cart_items if item["name"] != item_name]
    return {"success": True, "cart": cart_items}


@app.post("/api/cart/update")
async def update_cart_quantity(item_name: str, quantity: int):
    """Update item quantity in cart"""
    global cart_items
    
    for item in cart_items:
        if item["name"] == item_name:
            if quantity > 0:
                item["quantity"] = quantity
            else:
                cart_items.remove(item)
            break
    
    return {"success": True, "cart": cart_items}


@app.get("/api/cart")
async def get_cart():
    """Get current shopping cart"""
    total_items = sum(item["quantity"] for item in cart_items)
    total_price = sum(item["price"] * item["quantity"] for item in cart_items)
    
    return {
        "items": cart_items,
        "total_items": total_items,
        "total_price": round(total_price, 2),
        "timestamp": datetime.now().isoformat()
    }


@app.post("/api/cart/clear")
async def clear_cart():
    """Clear shopping cart"""
    global cart_items
    cart_items = []
    return {"success": True, "cart": cart_items}


@app.post("/api/cart/checkout")
async def checkout():
    """Process checkout and clear cart"""
    global cart_items
    
    total_items = sum(item["quantity"] for item in cart_items)
    total_price = sum(item["price"] * item["quantity"] for item in cart_items)
    
    receipt = {
        "items": cart_items.copy(),
        "total_items": total_items,
        "total_price": round(total_price, 2),
        "checkout_time": datetime.now().isoformat(),
        "transaction_id": f"TXN{int(time.time())}"
    }
    
    # Clear cart after checkout
    cart_items = []
    
    return receipt


@app.get("/api/products")
async def get_products():
    """Get available products database"""
    return {"products": PRODUCT_DATABASE}


@app.on_event("shutdown")
async def shutdown_event():
    """Release camera on shutdown"""
    global camera
    if camera is not None and camera.isOpened():
        camera.release()
        logger.info("Camera released")


# Mount static files (web interface)
if WEB_DIR.exists():
    app.mount("/", StaticFiles(directory=str(WEB_DIR), html=True), name="static")
    logger.info(f"Serving web interface from {WEB_DIR}")
else:
    logger.warning(f"Web directory not found at {WEB_DIR}")
    
    @app.get("/")
    async def root():
        """Root endpoint - basic HTML when web directory is missing"""
        return HTMLResponse("""
        <html>
            <head><title>Jetson Camera Stream</title></head>
            <body style="background: #000; color: #fff; font-family: Arial; text-align: center; padding-top: 50px;">
                <h1>Jetson Camera Stream</h1>
                <img src="/video_feed" style="max-width: 90%; border: 2px solid #333;">
                <p>Direct video feed - Web interface not available</p>
            </body>
        </html>
        """)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
