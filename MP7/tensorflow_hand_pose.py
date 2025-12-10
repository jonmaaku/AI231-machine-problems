"""
Hand Gesture Detection Testing Script
Uses YOLO to detect hand gestures (Open/Close) for POS system control
"""

import cv2
import numpy as np
from ultralytics import YOLO
import time
from collections import deque
from pathlib import Path

# Configuration
YOLO_MODEL = "MP7_Object_Detection\\v2dataset_yolov11n_augmented3\\weights\\best.pt"
CONFIDENCE_THRESHOLD = 0.5
IOU_THRESHOLD = 0.45
CAMERA_INDEX = 0  # USB camera
VGA_WIDTH = 1080
VGA_HEIGHT = 720
FPS = 60

# Hand gesture configuration
GESTURE_CLASSES = {
    'Open': 'open_hand',
    'Close': 'closed_fist'
}

GESTURE_COOLDOWN = 2  # seconds between gesture detections
GESTURE_HISTORY_SIZE = 5  # number of frames to track for smoothing

class HandGestureDetector:
    def __init__(self, model_path):
        """Initialize hand gesture detector"""
        print(f"Loading YOLO model: {model_path}")
        self.model = YOLO(model_path)
        
        self.last_gesture_time = 0
        self.current_gesture = None
        self.gesture_history = deque(maxlen=GESTURE_HISTORY_SIZE)
        self.pos_system_active = True
        
        print("Model loaded successfully!")
    
    def detect_gesture(self, frame: np.ndarray) -> tuple[np.ndarray, str, bool]:
        """
        Detect hand gestures in frame
        
        Returns:
            - annotated_frame: Frame with bounding boxes and labels
            - gesture: Current detected gesture ('open_hand', 'closed_fist', or 'none')
            - system_active: Whether POS system is active
        """
        start_time = time.time()
        
        try:
            # Run YOLO inference
            results = self.model(frame, conf=CONFIDENCE_THRESHOLD, iou=IOU_THRESHOLD, 
                               imgsz=640, verbose=False)[0]
            
            current_gesture = None
            current_time = time.time()
            
            # Process detections
            if results.boxes is not None:
                for box in results.boxes:
                    class_id = int(box.cls[0])
                    confidence = float(box.conf[0])
                    class_name = results.names[class_id]
                    
                    # Check for hand gestures
                    if class_name in GESTURE_CLASSES:
                        x1, y1, x2, y2 = map(int, box.xyxy[0])
                        gesture = GESTURE_CLASSES[class_name]
                        
                        # Add to history for smoothing
                        self.gesture_history.append(gesture)
                        current_gesture = gesture
                        
                        # Draw bounding box (blue for gestures)
                        color = (255, 0, 0) if gesture == 'open_hand' else (0, 0, 255)
                        cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                        
                        # Draw label
                        label = f"{class_name} ({confidence:.2f})"
                        label_size, _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)
                        cv2.rectangle(frame, (x1, y1 - label_size[1] - 10), 
                                    (x1 + label_size[0], y1), color, -1)
                        cv2.putText(frame, label, (x1, y1 - 5), 
                                  cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)
            
            # Handle gesture-based system toggle
            if current_gesture and (current_time - self.last_gesture_time) > GESTURE_COOLDOWN:
                if current_gesture == 'open_hand':
                    self.pos_system_active = True
                    print(f"[GESTURE] Open Hand detected → POS System: ON")
                    self.last_gesture_time = current_time
                elif current_gesture == 'closed_fist':
                    self.pos_system_active = False
                    print(f"[GESTURE] Closed Fist detected → POS System: OFF")
                    self.last_gesture_time = current_time
            
            self.current_gesture = current_gesture or 'none'
            
            # Add performance info
            inference_time = time.time() - start_time
            self.draw_info(frame, inference_time)
            
            return frame, self.current_gesture, self.pos_system_active
            
        except Exception as e:
            print(f"Detection error: {e}")
            return frame, 'none', self.pos_system_active
    
    def draw_info(self, frame: np.ndarray, inference_time: float):
        """Draw performance information on frame"""
        # System status
        status_color = (0, 255, 0) if self.pos_system_active else (0, 0, 255)
        status_text = "POS: ON" if self.pos_system_active else "POS: OFF"
        
        cv2.rectangle(frame, (10, 10), (250, 100), (0, 0, 0), -1)
        cv2.rectangle(frame, (10, 10), (250, 100), status_color, 2)
        
        cv2.putText(frame, status_text, (20, 35), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1, status_color, 2)
        cv2.putText(frame, f"Gesture: {self.current_gesture}", (20, 60), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 1)
        cv2.putText(frame, f"FPS: {int(1000/max(inference_time*1000, 1))}", (20, 85), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 1)
    
    def get_status(self) -> dict:
        """Get current system status"""
        return {
            'active': self.pos_system_active,
            'current_gesture': self.current_gesture,
            'gesture_history': list(self.gesture_history),
            'status': 'ON' if self.pos_system_active else 'OFF'
        }


def test_with_camera():
    """Test hand gesture detection with live camera feed"""
    print("\n=== Hand Gesture Detection - Camera Test ===")
    print("Controls:")
    print("  - Open Hand (✋) → Turn POS System ON")
    print("  - Closed Fist (✊) → Turn POS System OFF")
    print("  - Press 'q' to quit\n")
    
    # Initialize detector
    detector = HandGestureDetector(YOLO_MODEL)
    
    # Initialize camera
    camera = cv2.VideoCapture(CAMERA_INDEX)
    camera.set(cv2.CAP_PROP_FRAME_WIDTH, VGA_WIDTH)
    camera.set(cv2.CAP_PROP_FRAME_HEIGHT, VGA_HEIGHT)
    camera.set(cv2.CAP_PROP_FPS, FPS)
    
    if not camera.isOpened():
        print(f"Error: Could not open camera at index {CAMERA_INDEX}")
        return
    
    print(f"Camera opened: {VGA_WIDTH}x{VGA_HEIGHT} @ {FPS}fps\n")
    
    frame_count = 0
    start_time = time.time()
    
    try:
        while True:
            ret, frame = camera.read()
            if not ret:
                print("Failed to read frame from camera")
                break
            
            # Detect gestures
            frame, gesture, system_active = detector.detect_gesture(frame)
            
            # Display frame
            cv2.imshow('Hand Gesture Detection - POS Control', frame)
            
            # Print status periodically
            frame_count += 1
            if frame_count % 30 == 0:
                elapsed = time.time() - start_time
                fps = frame_count / elapsed
                status = detector.get_status()
                print(f"Frame {frame_count} | FPS: {fps:.1f} | Status: {status['status']} | Gesture: {status['current_gesture']}")
            
            # Exit on 'q' key
            if cv2.waitKey(1) & 0xFF == ord('q'):
                print("\nTest ended by user")
                break
    
    finally:
        camera.release()
        cv2.destroyAllWindows()
        print("\nCamera released")


def test_with_image(image_path: str):
    """Test hand gesture detection with a single image"""
    print(f"\n=== Hand Gesture Detection - Image Test ===")
    print(f"Testing image: {image_path}\n")
    
    # Initialize detector
    detector = HandGestureDetector(YOLO_MODEL)
    
    # Load image
    image = cv2.imread(image_path)
    if image is None:
        print(f"Error: Could not load image from {image_path}")
        return
    
    print(f"Image shape: {image.shape}")
    
    # Detect gestures
    annotated_image, gesture, system_active = detector.detect_gesture(image)
    
    # Get status
    status = detector.get_status()
    print(f"\nDetection Results:")
    print(f"  - Gesture Detected: {gesture}")
    print(f"  - System Active: {system_active}")
    print(f"  - Status: {status['status']}")
    
    # Save result
    output_path = image_path.replace('.jpg', '_detected.jpg').replace('.png', '_detected.png')
    cv2.imwrite(output_path, annotated_image)
    print(f"  - Annotated image saved: {output_path}")
    
    # Display
    cv2.imshow('Hand Gesture Detection Result', annotated_image)
    print("\nPress any key to close the window...")
    cv2.waitKey(0)
    cv2.destroyAllWindows()


def test_with_video(video_path: str):
    """Test hand gesture detection with a video file"""
    print(f"\n=== Hand Gesture Detection - Video Test ===")
    print(f"Testing video: {video_path}\n")
    
    # Initialize detector
    detector = HandGestureDetector(YOLO_MODEL)
    
    # Open video
    video = cv2.VideoCapture(video_path)
    if not video.isOpened():
        print(f"Error: Could not open video from {video_path}")
        return
    
    fps = video.get(cv2.CAP_PROP_FPS)
    frame_count = 0
    gesture_detections = {}
    
    print(f"Video FPS: {fps}")
    print("Processing...\n")
    
    try:
        while True:
            ret, frame = video.read()
            if not ret:
                break
            
            frame_count += 1
            frame, gesture, system_active = detector.detect_gesture(frame)
            
            # Track gesture detections
            if gesture != 'none':
                gesture_detections[gesture] = gesture_detections.get(gesture, 0) + 1
            
            # Display frame
            cv2.imshow('Hand Gesture Detection - Video', frame)
            
            # Print progress
            if frame_count % 30 == 0:
                status = detector.get_status()
                print(f"Frame {frame_count} | Gesture: {status['current_gesture']} | System: {status['status']}")
            
            # Exit on 'q' key
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    
    finally:
        video.release()
        cv2.destroyAllWindows()
        
        print(f"\nVideo Test Summary:")
        print(f"  - Total Frames: {frame_count}")
        print(f"  - Gesture Detections:")
        for gesture, count in gesture_detections.items():
            print(f"    - {gesture}: {count} frames")


if __name__ == "__main__":
    import sys
    
    print("\n╔════════════════════════════════════════════════════════════╗")
    print("║     Hand Gesture Detection for POS System Control         ║")
    print("║                  Testing Script                           ║")
    print("╚════════════════════════════════════════════════════════════╝\n")
    
    if len(sys.argv) > 1:
        test_input = sys.argv[1]
        
        # Check if it's a file path
        if Path(test_input).exists():
            if test_input.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp')):
                test_with_image(test_input)
            elif test_input.lower().endswith(('.mp4', '.avi', '.mov', '.mkv')):
                test_with_video(test_input)
            else:
                print(f"Unsupported file format: {test_input}")
        else:
            print(f"File not found: {test_input}")
    else:
        # Default: test with camera
        test_with_camera()
