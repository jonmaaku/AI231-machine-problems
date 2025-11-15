import cv2
import time
from fastapi import FastAPI, Request
from starlette.responses import StreamingResponse
import uvicorn

app = FastAPI()

# Function to capture frames from the USB camera using GStreamer (for hardware acceleration)
def gstreamer_pipeline(capture_width=1280, capture_height=720, display_width=1280, display_height=720, framerate=30, flip_method=0):
    """
    Returns a GStreamer pipeline string for use with cv2.VideoCapture()
    to access a USB camera on the Jetson with hardware acceleration (if possible).
    
    Note: The specific pipeline may vary based on your Jetson model and camera.
    A simple v4l2src often works well for standard USB cameras.
    """
    return (
        f'v4l2src device=/dev/video0 ! '
        f'video/x-raw, width=(int){capture_width}, height=(int){capture_height}, framerate=(fraction){framerate}/1 ! '
        f'nvvidconv flip-method={flip_method} ! '
        f'video/x-raw(memory:NVMM), format=(string)I420 ! '
        f'omxh264enc control-rate=2 bitrate=4000000 ! ' # Optional: encode to H264 if needed
        f'video/x-h264, stream-format=(string)byte-stream ! '
        f'h264parse ! '
        f'rtpenc_h264 ! '
        f'appsink' # This part might need adjustment for direct frame capture in OpenCV
    )

from fastapi import Query

def capture_frames(cam_index=0):
    cap = cv2.VideoCapture(cam_index)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    if not cap.isOpened():
        print("Cannot open camera")
        return
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        ret, buffer = cv2.imencode('.jpg', frame)
        if not ret:
            continue
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
        time.sleep(0.01)
    cap.release()

@app.get("/video_feed")
def video_feed(request: Request, cam: int = Query(0, description="Camera index (0=laptop, 1=USB)")):
    return StreamingResponse(capture_frames(cam), media_type="multipart/x-mixed-replace; boundary=frame")

@app.get("/")
def index():
    return """
    <html>
    <head>
        <title>FastAPI Video Streaming</title>
    </head>
    <body>
        <h1>USB/Laptop Camera Live Stream</h1>
        <p>
            <a href="/?cam=0">Laptop Camera</a> |
            <a href="/?cam=1">USB Camera</a>
        </p>
        <img id="video" src="/video_feed?cam=0" alt="Video Feed" width="640" height="480">
        <script>
            function setCam(cam) {
                document.getElementById('video').src = '/video_feed?cam=' + cam;
            }
            document.querySelectorAll('a').forEach(a => {
                a.onclick = function(e) {
                    e.preventDefault();
                    const cam = this.href.split('cam=')[1];
                    setCam(cam);
                }
            });
        </script>
    </body>
    </html>
    """

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
