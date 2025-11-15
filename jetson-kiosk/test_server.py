"""
Test server with synthetic video (no camera required)
Useful for testing the system without a physical camera
"""

from fastapi import FastAPI
from fastapi.responses import StreamingResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
import numpy as np
import cv2
import time
from pathlib import Path
from datetime import datetime

app = FastAPI(title="Camera Test Server (Virtual)")

# Get web directory
BASE_DIR = Path(__file__).resolve().parent
WEB_DIR = BASE_DIR / "web"


def generate_fake_frames():
    """Generate synthetic video frames for testing"""
    width, height = 640, 480
    frame_count = 0
    
    while True:
        # Create a frame with gradient background
        frame = np.zeros((height, width, 3), dtype=np.uint8)
        
        # Create animated gradient
        hue = (frame_count % 180)
        for y in range(height):
            for x in range(width):
                h = (hue + (x + y) // 10) % 180
                frame[y, x] = [h, 255, 200]
        
        # Convert HSV to BGR
        frame = cv2.cvtColor(frame, cv2.COLOR_HSV2BGR)
        
        # Add moving circle
        center_x = int(320 + 200 * np.sin(frame_count * 0.05))
        center_y = int(240 + 150 * np.cos(frame_count * 0.05))
        cv2.circle(frame, (center_x, center_y), 50, (255, 255, 255), -1)
        
        # Add frame counter
        text = f"VIRTUAL CAMERA - Frame {frame_count}"
        cv2.putText(frame, text, (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 
                    0.7, (255, 255, 255), 2)
        
        # Add timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cv2.putText(frame, timestamp, (50, 430), cv2.FONT_HERSHEY_SIMPLEX, 
                    0.6, (255, 255, 255), 1)
        
        # Add "TEST MODE" warning
        cv2.putText(frame, "TEST MODE - NO REAL CAMERA", (150, 250), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
        
        # Encode frame as JPEG
        ret, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
        frame_bytes = buffer.tobytes()
        
        # Yield frame in multipart format
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
        
        frame_count += 1
        time.sleep(1/30)  # 30 FPS


@app.get("/video_feed")
async def video_feed():
    """MJPEG video stream endpoint (virtual camera)"""
    return StreamingResponse(
        generate_fake_frames(),
        media_type="multipart/x-mixed-replace; boundary=frame"
    )


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "camera": "virtual",
        "resolution": "640x480",
        "fps": 30,
        "mode": "test"
    }


@app.get("/api/info")
async def get_info():
    """Get server information"""
    return {
        "server": "Test Server (Virtual Camera)",
        "resolution": "640x480",
        "fps": 30,
        "camera_type": "synthetic",
        "mode": "test"
    }


# Mount static files (web interface)
if WEB_DIR.exists():
    app.mount("/", StaticFiles(directory=str(WEB_DIR), html=True), name="static")
else:
    @app.get("/")
    async def root():
        """Root endpoint - basic HTML when web directory is missing"""
        return HTMLResponse("""
        <html>
            <head><title>Test Camera Stream</title></head>
            <body style="background: #000; color: #fff; font-family: Arial; text-align: center; padding-top: 50px;">
                <h1>Virtual Camera Stream (TEST MODE)</h1>
                <p style="color: #ff6666;">No physical camera required</p>
                <img src="/video_feed" style="max-width: 90%; border: 2px solid #333;">
                <p>This is a test server with synthetic video</p>
            </body>
        </html>
        """)


if __name__ == "__main__":
    import uvicorn
    print("=" * 60)
    print("TEST SERVER - Virtual Camera Mode")
    print("=" * 60)
    print("No physical camera required!")
    print("Server starting on http://localhost:8000")
    print("Press Ctrl+C to stop")
    print("=" * 60)
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
