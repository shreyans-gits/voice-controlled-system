import face_recognition as fr
import cv2

class Detector:
    def __init__(self):
        pass

    def detect_faces(self,image):
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        locations = fr.face_locations(rgb_image, model="hog")
        return locations