import cv2
import pickle
import os
from skills.facelink.detector import Detector
from skills.facelink.embedder import Embedder

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DB_PATH = os.path.join(BASE_DIR, "data", "enrolled_faces.pkl")

class Enrollment:
    def __init__(self):
        self.detector = Detector()
        self.embedder = Embedder()

    def save_enrolled(self, db, file_path="data/enrolled_faces.pkl"):
        with open(file_path, "wb") as f:
            pickle.dump(db, f)
        print(f"Database saved to {file_path}")

    def load_enrolled(self, file_path="data/enrolled_faces.pkl"):
        if not os.path.exists(file_path):
            return {}
        with open(file_path, "rb") as f:
            return pickle.load(f)

    def enroll_person(self, name, photo_path, db):
        image = cv2.imread(photo_path)
        
        if image is None:
            print(f"Error: Could not load image at {photo_path}")
            return False
        locations = self.detector.detect_faces(image)
        if len(locations) == 0:
            print(f"Error: No face found in {photo_path}")
            return False
        embeddings = self.embedder.get_embedding(image, locations)
        
        if name not in db:
            db[name] = []
        db[name].append(embeddings)

        print(f"Successfully enrolled {name}!")
        return True