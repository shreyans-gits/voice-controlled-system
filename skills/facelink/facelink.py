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
            name = matcher.find_match(embeddings, db)
            names.append(name)
        
        return names if names else "No faces detected"