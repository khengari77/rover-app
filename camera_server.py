from flask import Flask, Response
from threading import Lock, Thread
import time
import cv2
import numpy as np
from picamera2 import Picamera2
from gradio_client import Client, handle_file
import os
import tempfile
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)
picam2 = Picamera2()

# Correct configuration using frame_duration for FPS control
config = picam2.create_video_configuration(
    main={"size": (640, 480)},  # Stream size
    lores={"size": (320, 240)},
    display="lores",
    frame_duration=int(1e9 / 10)  # 10 FPS (1e9 ns per second / 10 FPS)
)
picam2.configure(config)
picam2.start()

client = Client(os.getenv("GRADIO_SPACE"), hf_token=os.getenv("HF_TOKEN"))
latest_frame = None
latest_depth_frame = None
frame_lock = Lock()
depth_lock = Lock()
temp_dir = tempfile.TemporaryDirectory()

def process_depth(frame):
    try:
        input_path = f"{temp_dir.name}/input.jpg"
        cv2.imwrite(input_path, frame)
        im_file = handle_file(input_path)
        result = client.predict(image=im_file, api_name="/on_submit")
        depth_path = result[1]
        depth = cv2.imread(depth_path, cv2.IMREAD_GRAYSCALE)
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
    interval = 5.0
    last_processing_time = time.time()
    next_allowed_time = last_processing_time + interval
    
    while True:
        current_time = time.time()
        if current_time >= next_allowed_time:
            with frame_lock:
                if latest_frame is not None:
                    frame = latest_frame.copy()
            
            if frame is not None:
                processed = process_depth(frame)
                if processed is not None:
                    with depth_lock:
                        latest_depth_frame = processed
                    last_processing_time = current_time
                    next_allowed_time = last_processing_time + interval
            else:
                last_processing_time = current_time
                next_allowed_time = last_processing_time + interval
        else:
            time.sleep(next_allowed_time - current_time)

def generate_stream(stream_type):
    while True:
        frame = None
        with (frame_lock if stream_type == 'video' else depth_lock):
            frame = latest_frame if stream_type == 'video' else latest_depth_frame
        
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
    capture_thread = Thread(target=capture_frames, daemon=True)
    process_thread = Thread(target=process_frames, daemon=True)
    capture_thread.start()
    process_thread.start()
    app.run(host='0.0.0.0', port=5000, threaded=True)
