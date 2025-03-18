import sys
sys.path.append("../")

import cv2
from detection.face_matching import *

import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import storage
from sklearn.datasets import fetch_lfw_people
from sklearn.preprocessing import LabelEncoder
from sklearn.svm import SVC
import numpy as np


# Load the LFW dataset
lfw_people = fetch_lfw_people(min_faces_per_person=70, resize=0.4, color=False)

# Extract images and labels
images = lfw_people.images
labels = lfw_people.target
target_names = lfw_people.target_names

# Flatten the images for the classifier
n_samples, h, w = images.shape
X = images.reshape(n_samples, h * w)
y = labels

# Encode labels
label_encoder = LabelEncoder()
y = label_encoder.fit_transform(y)

# Train a classifier
clf = SVC(kernel='linear', C=1)
clf.fit(X, y)


def match_with_database(img, clf, target_names):
    # Detect faces in the frame (you should implement detect_faces properly)
    faces = detect_faces(img)

    for face in faces:
        try:
            # Align the face
            aligned_face = align_face(img, face)

            # Resize the aligned face to match the size of the LFW images
            aligned_face = cv2.resize(aligned_face, (h, w))

            # Flatten the aligned face
            X_new = aligned_face.reshape(1, h * w)

            # Predict the label
            y_pred = clf.predict(X_new)
            predicted_name = target_names[y_pred][0]
            print(f"Predicted: {predicted_name}")

        except:
            print("No face detected")

    # Draw the rectangle around each face
    for x, y, w, h in faces:
        cv2.rectangle(img, (x, y), (x + w, y + h), (0, 0, 255), 4)
        print("Face detected")

    # Display the frame
    cv2.imshow("Detected Faces", img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


cred = credentials.Certificate("../database/serviceAccountKey.json")
firebase_admin.initialize_app(
    cred,
    {
        "databaseURL": "https://face-recognition-486cb-default-rtdb.firebaseio.com/",
        "storageBucket": "face-recognition-486cb.appspot.com",
    },
)

# Information to database
ref = db.reference("Employee")
# Obtain the last EmployerId number from the database
number_Employer = len(ref.get())
print("There are", (number_Employer - 1), "Employee in the database")

database = {}
for i in range(1, number_Employer):
    EmployerInfo = db.reference(f"Employee/{i}").get()
    EmployerName = EmployerInfo["name"]
    EmployerEmbedding = EmployerInfo["embeddings"]
    database[EmployerName] = EmployerEmbedding

camera_or_image = input("Enter (1) if you have camera\nEnter (2) if you have image: ")

if camera_or_image == "1":
    # define a video capture object
    vid = cv2.VideoCapture(0)
    while True:
        # Capture the video frame
        ret, frame = vid.read()

        # Add beautiful text to the frame to save the image with 's' button
        cv2.putText(
            frame,
            "Press 's' to save the image",
            (50, 50),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 0, 255),
            2,
            cv2.LINE_AA,
        )

        # Display the resulting frame
        cv2.imshow("frame", frame)

        if cv2.waitKey(1) & 0xFF == ord("s"):
            break

    # After the loop release the cap object
    vid.release()
    cv2.destroyAllWindows()

    match_with_database(frame, clf, target_names)

elif camera_or_image == "2":
    # Read the image
    img = cv2.imread("../examples/face1.png")
    match_with_database(img, clf, target_names)
