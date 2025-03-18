import cv2
import face_recognition
import numpy as np
import os
import pickle
from modules.Camera import VideoCamera  # Use an absolute import; adjust if needed

class FaceRecognitionSystem:
    def __init__(self):
        self.known_encodings = []
        self.employee_ids = []
        self.load_encodings()

    def load_encodings(self):
        employee_photos_dir = 'employee_photos'
        if not os.path.exists(employee_photos_dir):
            os.makedirs(employee_photos_dir)
            
        for emp_folder in os.listdir(employee_photos_dir):
            encoding_path = os.path.join(employee_photos_dir, emp_folder, 'encoding.dat')
            if os.path.exists(encoding_path):
                with open(encoding_path, 'rb') as f:
                    self.known_encodings.append(pickle.load(f))
                # Expecting folder names like "employee_123"
                parts = emp_folder.split('_')
                if len(parts) > 1:
                    self.employee_ids.append(parts[1])
                else:
                    self.employee_ids.append(emp_folder)

    def recognize_face(self, frame):
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        face_locations = face_recognition.face_locations(rgb_frame)
        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)
        
        recognized = []
        for face_encoding, face_location in zip(face_encodings, face_locations):
            matches = face_recognition.compare_faces(self.known_encodings, face_encoding)
            name = "Unknown"
            if True in matches:
                first_match_index = matches.index(True)
                name = self.employee_ids[first_match_index]
            recognized.append((name, face_location))
        return recognized

    def capture_registration_photo(self):
        # Create a temporary VideoCapture instance
        cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        if not cap.isOpened():
            cap = cv2.VideoCapture(0, cv2.CAP_MSMF)
        if not cap.isOpened():
            cap = cv2.VideoCapture(0)
        ret, frame = cap.read()
        cap.release()
        if not ret:
            raise RuntimeError("Failed to capture image from camera.")
        return frame

    def register_employee(self, employee_name, photo_path):
        """
        Registers a new employee by encoding their face from the provided photo and saving it.
        """
        image = face_recognition.load_image_file(photo_path)
        face_encodings = face_recognition.face_encodings(image)
        if not face_encodings:
            raise ValueError(f"No face found in the image {photo_path}.")
        
        encoding = face_encodings[0]
        employee_folder = os.path.join('employee_photos', f'employee_{employee_name}')
        os.makedirs(employee_folder, exist_ok=True)
        encoding_path = os.path.join(employee_folder, 'encoding.dat')
        with open(encoding_path, 'wb') as f:
            pickle.dump(encoding, f)
        self.known_encodings.append(encoding)
        self.employee_ids.append(employee_name)

def process_frame(frame, entry_zone, exit_zone, face_recognition_system):
    """
    Process a single frame: detect faces, recognize them, and annotate the frame.
    """
    recognized_faces = face_recognition_system.recognize_face(frame)
    
    for name, (top, right, bottom, left) in recognized_faces:
        # Draw a rectangle around the face
        cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
        # Draw a label with the name below the face
        cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 255, 0), cv2.FILLED)
        font = cv2.FONT_HERSHEY_DUPLEX
        cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)
    
    return frame
