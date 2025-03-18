from flask import Flask, render_template, Response, request, jsonify
from werkzeug.utils import secure_filename
import os
import threading
import time
import configparser
from modules.Camera import VideoCamera

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # For flash messages

# Read configuration from config.ini
config = configparser.ConfigParser()
config.read('config.ini')
ENTRY_ZONE = (float(config['DOOR']['ENTRY_ZONE_START']), float(config['DOOR']['ENTRY_ZONE_END']))
EXIT_ZONE = (float(config['DOOR']['EXIT_ZONE_START']), float(config['DOOR']['EXIT_ZONE_END']))

# Initialize the video camera
camera = VideoCamera()

# Configure upload folder and allowed extensions
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Employees')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def allowed_file(filename):
    """Check if the file has an allowed extension."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

def generate_frames():
    """Video streaming generator function."""
    while True:
        frame = camera.get_frame()
        if frame is None:
            continue
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
        time.sleep(0.03)

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        employee_name = request.form.get('name')
        file = request.files.get('photo')
        if not employee_name or not file:
            return jsonify({"status": "danger", "message": "Employee name and photo are required."})
        if not allowed_file(file.filename):
            return jsonify({"status": "danger", "message": "Invalid file type."})
        
        employee_folder = os.path.join(app.config['UPLOAD_FOLDER'], employee_name)
        photos_folder = os.path.join(employee_folder, 'photos')
        os.makedirs(photos_folder, exist_ok=True)
        
        filename = secure_filename(file.filename)
        photo_path = os.path.join(photos_folder, filename)
        try:
            file.save(photo_path)
            return jsonify({"status": "success", "message": "Employee registered successfully."})
        except Exception as e:
            return jsonify({"status": "danger", "message": "Error saving file: " + str(e)})
    return render_template('register.html')

@app.route('/attendance')
def attendance():
    return render_template('attendance.html')

@app.route('/attendance_data')
def attendance_data():
    # Return an empty list or dummy data for now.
    data = []
    return jsonify(data)

@app.route('/notifications')
def notifications():
    # Return empty notifications as a stub.
    return jsonify([])

if __name__ == '__main__':

    app.run(host='0.0.0.0', port=5000, debug=True)