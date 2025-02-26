from flask import Flask, Response
from threading import Lock
import threading
from picamera2 import Picamera2
import cv2
import numpy as np
import time

# Load environment variables first
load_dotenv()
app = Flask(__name__)
# Initialize Picamera2
picam2 = Picamera2()
config = picam2.create_video_configuration(main={"size": (640, 480)}, lores={"size": (320, 240)}, display="lores")
picam2.configure(config)
picam2.start()

# Shared variables with locks
latest_frame = None
frame_lock = Lock()

def capture_frames():
    global latest_frame
    while True:
        frame = picam2.capture_array()
        with frame_lock:
            latest_frame = frame.copy()
    time.sleep(1/60)

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
if __name__ == '__main__':
    # Start frame capture thread
    capture_thread = threading.Thread(target=capture_frames)
    capture_thread.daemon = True
    capture_thread.start()
    
    # Start Flask app
    app.run(host='0.0.0.0', port=5000, threaded=True)
