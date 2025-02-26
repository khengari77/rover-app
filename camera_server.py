from flask import Flask, Response
from threading import Lock
import threading
from picamera2 import Picamera2
import cv2
import numpy as np
import time
import tempfile
from gradio_client import Client, handle_file
import os
from dotenv import load_dotenv
# Load environment variables first
load_dotenv()
app = Flask(__name__)
# Initialize Picamera2
picam2 = Picamera2()
config = picam2.create_video_configuration(main={"size": (640, 480)}, lores={"size": (320, 240)}, display="lores")
picam2.configure(config)
picam2.start()
# Initialize Gradio client
client = Client(os.getenv("GRADIO_SPACE"), hf_token=os.getenv("HF_TOKEN"))
# Shared variables with locks
latest_frame = None
latest_depth_frame = None
frame_lock = Lock()
depth_lock = Lock()
# Temporary file setup
temp_dir = tempfile.TemporaryDirectory()
def process_depth(frame):
    try:
        # Save frame to temporary file
        input_path = f"{temp_dir.name}/input.jpg"
        cv2.imwrite(input_path, frame)
        im_file = handle_file(input_path)
        print(im_file.keys())
        
        # Call Depth-Anything API
        result = client.predict(
            image=im_file,
            api_name="/on_submit"
        )
        
        # Read depth map from result
        depth_path = result[1]  # Grayscale depth map
        depth = cv2.imread(depth_path, cv2.IMREAD_GRAYSCALE)
        
        # Normalize and apply color map
        depth_normalized = cv2.normalize(depth, None, 0, 255, cv2.NORM_MINMAX)
        depth_color = cv2.applyColorMap(depth_normalized, cv2.COLORMAP_JET)
        
        return depth_color
    except Exception as e:
        print(f"Depth processing error: {e}")
        return None
def capture_frames():
    global latest_frame
    while True:
        frame = picam2.capture_array()
        with frame_lock:
            latest_frame = frame.copy()
def process_frames():
    global latest_depth_frame
    frame = None 
    while True:
        with frame_lock:
            if latest_frame is not None:
                frame = latest_frame.copy()
        
        if frame is not None:
            processed = process_depth(frame)
            if processed is not None:
                with depth_lock:
                    latest_depth_frame = processed
def generate_stream(stream_type):
    while True:
        frame = None
        if stream_type == 'video':
            with frame_lock:
                frame = latest_frame
        elif stream_type == 'depth':
            with depth_lock:
                frame = latest_depth_frame
        
        if frame is not None:
            ret, jpeg = cv2.imencode('.jpg', frame)
            if ret:
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n\r\n')
@app.route('/stream')
def video_stream():
    return Response(generate_stream('video'),
                    mimetype='multipart/x-mixed-replace; boundary=frame')
@app.route('/depth')
def depth_stream():
    return Response(generate_stream('depth'),
                    mimetype='multipart/x-mixed-replace; boundary=frame')
if __name__ == '__main__':
    # Start frame capture thread
    capture_thread = threading.Thread(target=capture_frames)
    capture_thread.daemon = True
    capture_thread.start()
    # Start depth processing thread
    process_thread = threading.Thread(target=process_frames)
    process_thread.daemon = True
    process_thread.start()
    # Start Flask app
    app.run(host='0.0.0.0', port=5000, threaded=True)
