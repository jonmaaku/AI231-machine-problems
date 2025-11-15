"""
FastAPI Video Streaming Server for Jetson Orin
Streams VGA resolution video from USB camera
"""

from fastapi import FastAPI, Response
from fastapi.responses import StreamingResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
import cv2
import asyncio
from typing import Generator
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Jetson Camera Stream")

# Camera configuration
CAMERA_INDEX = 0  # USB camera index (usually 0, adjust if needed)
VGA_WIDTH = 640
VGA_HEIGHT = 480
FPS = 30

# Global camera object
camera = None


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


@app.get("/")
async def root():
    """Root endpoint - redirects to video feed page"""
    return {"status": "running", "message": "Video server is active", "stream_url": "/video_feed"}


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


@app.on_event("shutdown")
async def shutdown_event():
    """Release camera on shutdown"""
    global camera
    if camera is not None and camera.isOpened():
        camera.release()
        logger.info("Camera released")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
