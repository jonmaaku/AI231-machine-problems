# System Architecture - Jetson POS System

## 🏗️ High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    JETSON ORIN HARDWARE                      │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────┐      ┌─────────────────┐                 │
│  │  USB Camera  │─────▶│  Video Capture  │                 │
│  └──────────────┘      └────────┬────────┘                 │
│                                  │                           │
│                                  ▼                           │
│  ┌───────────────────────────────────────────────────────┐  │
│  │              YOLO DETECTION ENGINE                     │  │
│  │  ┌─────────────────────────────────────────────────┐  │  │
│  │  │  YOLOv8/v11 Model (TensorRT Optimized)         │  │  │
│  │  │  - Object Detection                             │  │  │
│  │  │  - Bounding Box Generation                      │  │  │
│  │  │  - Confidence Scoring                           │  │  │
│  │  │  - GPU Acceleration (CUDA)                      │  │  │
│  │  └─────────────────────────────────────────────────┘  │  │
│  └────────────────────────┬──────────────────────────────┘  │
│                           │                                  │
│                           ▼                                  │
│  ┌───────────────────────────────────────────────────────┐  │
│  │              FASTAPI SERVER (server.py)               │  │
│  │  ┌──────────────────────────────────────────────┐    │  │
│  │  │  API Endpoints                                │    │  │
│  │  │  • /video_feed    - MJPEG Stream             │    │  │
│  │  │  • /api/detect    - Detection API            │    │  │
│  │  │  • /api/cart/*    - Cart Management          │    │  │
│  │  │  • /health        - Health Check             │    │  │
│  │  └──────────────────────────────────────────────┘    │  │
│  │  ┌──────────────────────────────────────────────┐    │  │
│  │  │  Business Logic                               │    │  │
│  │  │  • Product Database                           │    │  │
│  │  │  • Cart Management                            │    │  │
│  │  │  • Transaction Processing                     │    │  │
│  │  │  • Receipt Generation                         │    │  │
│  │  └──────────────────────────────────────────────┘    │  │
│  └────────────────────────┬──────────────────────────────┘  │
│                           │                                  │
└───────────────────────────┼──────────────────────────────────┘
                            │
                            ▼ (HTTP/WebSocket)
┌─────────────────────────────────────────────────────────────┐
│                   WEB BROWSER (KIOSK MODE)                   │
├─────────────────────────────────────────────────────────────┤
│  ┌───────────────────────────────────────────────────────┐  │
│  │                   pos.html (UI)                        │  │
│  │  ┌──────────────────┐  ┌───────────────────────────┐  │  │
│  │  │  Camera Section  │  │    Cart Section           │  │  │
│  │  │  • Live Stream   │  │    • Items List           │  │  │
│  │  │  • Detections    │  │    • Quantities           │  │  │
│  │  │  • Performance   │  │    • Prices               │  │  │
│  │  │  • Auto-Scan     │  │    • Totals               │  │  │
│  │  └──────────────────┘  │    • Checkout             │  │  │
│  │                        └───────────────────────────┘  │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

## 🔄 Data Flow

### 1. Video Stream Flow
```
Camera → Frame Capture → YOLO Detection → Annotation → 
JPEG Encode → MJPEG Stream → Browser Display
```

### 2. Detection Flow
```
Frame → YOLO Inference → Product Matching → 
API Response → Cart Update → UI Refresh
```

### 3. Checkout Flow
```
Cart Items → Checkout API → Receipt Generation → 
Transaction Record → Cart Clear → Display Receipt
```

## 📦 Component Details

### Camera Module
- **Input**: USB Camera (UVC compatible)
- **Resolution**: 1080x720 @ 60fps
- **Format**: MJPEG or YUV
- **Buffer**: Minimal latency configuration

### YOLO Detection Engine
- **Model**: YOLOv8n/s/m or YOLOv11n
- **Framework**: Ultralytics + PyTorch
- **Optimization**: TensorRT (FP16)
- **Inference**: <500ms target
- **Output**: Bounding boxes, class IDs, confidence scores

### FastAPI Server
- **Framework**: FastAPI (async)
- **Port**: 8000 (configurable)
- **CORS**: Enabled for cross-origin requests
- **Static Files**: Serves web interface
- **WebSocket**: Potential for real-time updates

### Product Database
```python
{
  "class_name": {
    "name": "Display Name",
    "price": 9.99,
    "category": "Category"
  }
}
```

### Cart State
```python
[
  {
    "name": "Product Name",
    "price": 9.99,
    "category": "Category",
    "quantity": 2,
    "added_at": "timestamp"
  }
]
```

## 🔌 API Architecture

```
┌─────────────────────────────────────────┐
│         FastAPI Application             │
├─────────────────────────────────────────┤
│                                         │
│  GET /video_feed                        │
│  └─→ MJPEG Stream Generator             │
│      └─→ Camera + YOLO + Encode         │
│                                         │
│  GET /api/detect                        │
│  └─→ Single Frame Detection             │
│      └─→ Product List + Timing          │
│                                         │
│  POST /api/cart/add                     │
│  └─→ Add Item to Cart                   │
│      └─→ Update Global Cart State       │
│                                         │
│  GET /api/cart                          │
│  └─→ Get Cart Contents                  │
│      └─→ Calculate Totals               │
│                                         │
│  POST /api/cart/checkout                │
│  └─→ Process Transaction                │
│      └─→ Generate Receipt + Clear Cart  │
│                                         │
│  GET /health                            │
│  └─→ System Health Check                │
│      └─→ Camera + Server Status         │
│                                         │
└─────────────────────────────────────────┘
```

## 🎯 Performance Pipeline

```
┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐
│  Camera  │─▶│   YOLO   │─▶│ Product  │─▶│   Cart   │─▶│    UI    │
│ Capture  │  │ Inference│  │ Matching │  │  Update  │  │  Render  │
└──────────┘  └──────────┘  └──────────┘  └──────────┘  └──────────┘
   ~10ms        ~200-500ms      ~5ms         ~10ms        ~16ms
                                                                    
Total Target: <500ms end-to-end latency
```

## 🖥️ UI Component Structure

```
pos.html
├── Camera Section
│   ├── Video Stream Container
│   │   ├── MJPEG Image Element
│   │   └── Performance Overlay
│   │       ├── Latency Indicator
│   │       ├── Detection Count
│   │       └── FPS Counter
│   └── Auto-Scan Toggle
│
└── Cart Section
    ├── Cart Header (Item count)
    ├── Items List (scrollable)
    │   └── Cart Item Cards
    │       ├── Product Info (name, category, price)
    │       └── Controls (quantity +/-, remove)
    ├── Cart Summary
    │   ├── Total Items
    │   ├── Subtotal
    │   └── Grand Total
    └── Action Buttons
        ├── Scan Now
        ├── Clear Cart
        └── Checkout
```

## 🔐 Security Considerations

### Current Implementation
- **No Authentication**: Designed for kiosk mode (trusted environment)
- **Local Network**: Server binds to 0.0.0.0 (all interfaces)
- **No HTTPS**: HTTP only (add reverse proxy for production)

### Production Recommendations
1. Add authentication for admin endpoints
2. Implement HTTPS with SSL certificates
3. Rate limiting for API endpoints
4. Input validation and sanitization
5. Database for transaction persistence
6. Backup and recovery mechanisms

## 📈 Scalability Options

### Horizontal Scaling
```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  Camera 1   │────▶│  Jetson 1   │────▶│  Display 1  │
└─────────────┘     └─────────────┘     └─────────────┘
                           │
                           ▼
                    ┌─────────────┐
                    │  Central DB │
                    └─────────────┘
                           ▲
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  Camera 2   │────▶│  Jetson 2   │────▶│  Display 2  │
└─────────────┘     └─────────────┘     └─────────────┘
```

### Cloud Integration
```
Jetson POS ──▶ MQTT/REST ──▶ Cloud Server
                              ├── Analytics
                              ├── Inventory Management
                              ├── Transaction Database
                              └── Reporting Dashboard
```

## 🛠️ Technology Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Hardware** | NVIDIA Jetson Orin | Edge AI computing |
| **AI/ML** | YOLOv8/v11, TensorRT | Object detection |
| **Backend** | FastAPI, Uvicorn | API server |
| **Computer Vision** | OpenCV, PyTorch | Image processing |
| **Frontend** | HTML5, CSS3, JavaScript | User interface |
| **OS** | Ubuntu 20.04/22.04 | Operating system |
| **Display** | Chromium (Kiosk) | Browser runtime |

## 🎯 Optimization Targets

| Metric | Target | Optimization Method |
|--------|--------|---------------------|
| Inference Latency | <500ms | TensorRT, small model, low resolution |
| Video FPS | 30-60fps | Efficient encoding, buffering |
| Cart Update | <50ms | In-memory state, async API |
| UI Responsiveness | <100ms | Debouncing, batch updates |
| Memory Usage | <4GB | Model quantization, caching |
| CPU Usage | <70% | GPU offload, async I/O |

---

**Architecture designed for: Real-time performance, Low latency, Jetson optimization, Scalability**
