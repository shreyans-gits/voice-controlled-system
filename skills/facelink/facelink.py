import os
import sys
import types

venv_site = r"e:\ek-gits\Facelink\venv\Lib\site-packages"
m_dir = os.path.join(venv_site, "face_recognition_models", "models")
m = types.ModuleType("face_recognition_models")
m.pose_predictor_model_location = lambda: os.path.join(m_dir, "shape_predictor_68_face_landmarks.dat")
m.pose_predictor_five_point_model_location = lambda: os.path.join(m_dir, "shape_predictor_5_face_landmarks.dat")
m.face_recognition_model_location = lambda: os.path.join(m_dir, "dlib_face_recognition_resnet_model_v1.dat")
m.cnn_face_detector_model_location = lambda: os.path.join(m_dir, "mmod_human_face_detector.dat")
sys.modules["face_recognition_models"] = m

print("Successfully spoofed face_recognition_models.")

import cv2

import config
from enrollment import Enrollment
from detector import Detector
from embedder import Embedder
import matcher

def main():
    enrollment = Enrollment()
    detector = Detector()
    embedder = Embedder()

    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

    w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    if not cap.isOpened():
        print("Camera Not Opened")
        return
    
    db = enrollment.load_enrolled()
    print("Enrolled number : ", len(db))
    
    print("Starting FaceLink... Press 'q' to quit.")
    cv2.namedWindow("FaceLink", cv2.WINDOW_NORMAL)
    cv2.setWindowProperty("FaceLink", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

    frame_count = 0
    last_results = []

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error: Failed to capture frame.")
            break

        frame = cv2.flip(frame, 1)

        if frame_count % 5 == 0:
            small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
            last_results = []
            locations = detector.detect_faces(small_frame)

            for location in locations:
                embeddings = embedder.get_embedding(small_frame,[location])
                if embeddings is None:
                    continue
                name = matcher.find_match(embeddings, db)
                top, right, bottom, left = location
                last_results.append(((top*4, right*4, bottom*4, left*4), name))
        
        for location,name in last_results:
            top, right, bottom, left = location
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
            cv2.putText(frame, name, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

        cv2.imshow("FaceLink", frame)
        frame_count += 1
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()