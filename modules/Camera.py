import cv2

class VideoCamera:
    def __init__(self):
        self.video = cv2.VideoCapture(0)
        if not self.video.isOpened():
            raise RuntimeError("Error: Could not open camera.")

        # Set camera properties
        self.video.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.video.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    def __del__(self):
        if self.video.isOpened():
            self.video.release()

    def get_frame(self):
        success, image = self.video.read()
        if not success:
            return None
        ret, jpeg = cv2.imencode('.jpg', image)
        if not ret:
            return None
        return jpeg.tobytes()
