"""
Enhanced FastAPI Video Streaming Server with Static File Serving
Streams VGA resolution video from USB camera and serves web interface
"""

from fastapi import FastAPI, Response
from fastapi.responses import StreamingResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
import cv2
import asyncio
from typing import Generator
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Jetson Camera Stream")

# Camera configuration
CAMERA_INDEX = 0  # USB camera index (usually 0, adjust if needed)
VGA_WIDTH = 1080
VGA_HEIGHT = 720
FPS = 60

# Global camera object
camera = None

# Get the directory where this script is located
BASE_DIR = Path(__file__).resolve().parent
WEB_DIR = BASE_DIR / "web"


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


def generate_frames() -> Generator[bytes, None, None]:
    """Generate frame bytes for MJPEG stream"""
    cam = get_camera()
    
    while True:
        success, frame = cam.read()
        if not success:
            logger.warning("Failed to read frame from camera")
            break
        
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
        "server": "Jetson Orin Camera Server",
        "resolution": f"{VGA_WIDTH}x{VGA_HEIGHT}",
        "fps": FPS,
        "camera_index": CAMERA_INDEX
    }


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
