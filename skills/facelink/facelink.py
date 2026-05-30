import os
import sys
import types
import cv2
from skills.facelink.enrollment import Enrollment
from skills.facelink.detector import Detector
from skills.facelink.embedder import Embedder
from skills.facelink import matcher

class FaceLink:
    def __init__(self):
        venv_site = r"e:\ek-gits\NOVA\venv\Lib\site-packages"
        m_dir = os.path.join(venv_site, "face_recognition_models", "models")
        m = types.ModuleType("face_recognition_models")
        m.pose_predictor_model_location = lambda: os.path.join(m_dir, "shape_predictor_68_face_landmarks.dat")
        m.pose_predictor_five_point_model_location = lambda: os.path.join(m_dir, "shape_predictor_5_face_landmarks.dat")
        m.face_recognition_model_location = lambda: os.path.join(m_dir, "dlib_face_recognition_resnet_model_v1.dat")
        m.cnn_face_detector_model_location = lambda: os.path.join(m_dir, "mmod_human_face_detector.dat")
        sys.modules["face_recognition_models"] = m

        self.enrollment = Enrollment()
        self.detector = Detector()
        self.embedder = Embedder()

        self.db = self.enrollment.load_enrolled()

    def identify(self):
        cap = cv2.VideoCapture(0)
        ret, frame = cap.read()
        cap.release()
        
        if not ret:
            return "No frame captured"
        
        frame = cv2.flip(frame, 1)
        db = self.enrollment.load_enrolled()
        
        small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)

        locations = self.detector.detect_faces(small_frame)
        if not locations:
            return "No faces detected"
        names = []
        for location in locations:
            embeddings = self.embedder.get_embedding(small_frame, [location])
            if embeddings is None:
                continue
            name = matcher.find_match(embeddings, self.db)
            names.append(name)
        return names if names else "No faces detected"

    def detect_and_identify_frame(self, frame):
        import cv2
        if frame is None:
            return []

        results = []
        try:
            small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
            
            rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

            face_locations = self.detector.detect_faces(rgb_small_frame)

            for location in face_locations:
                try:
                    embedding = self.embedder.get_embedding(rgb_small_frame, [location])
                    name = matcher.find_match(embedding, self.db) if embedding is not None else "Unknown"
                    if not name:
                        name = "Unknown"
                except Exception as e:
                    print(f"[FaceLink Match] {e}")
                    name = "Unknown"

                top, right, bottom, left = location
                scaled_location = (top * 4, right * 4, bottom * 4, left * 4)
                results.append((scaled_location, name))
                
        except Exception as e:
            print(f"[FaceLink Core Engine Exception] Array scanning skipped: {e}")
            
        return results