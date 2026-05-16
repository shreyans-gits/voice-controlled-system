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

import webbrowser
import google_photos
from enrollment import Enrollment

def main():
    creds = google_photos.authenticate()
    if not creds:
        print("Authentication failed.")
        return

    session_id, picker_uri = google_photos.create_picker_session(creds)
    if not session_id:
        print("Failed to create picker session.")
        return

    print(f"Opening browser for photo selection...")
    webbrowser.open(picker_uri)

    temp_folder = "temp_google_photos"
    photo_paths = google_photos.download_selected_photos(creds, session_id, temp_folder)

    if not photo_paths:
        print("No photos were downloaded.")
        return

    name = input("Enter the name of the person in these photos: ").strip()
    if not name:
        print("Name cannot be empty. Enrollment cancelled.")
        return

    enroller = Enrollment()
    db = enroller.load_enrolled()

    print(f"Enrolling {name} into the local database...")
    for path in photo_paths:
        success = enroller.enroll_person(name, path, db)
        if not success:
            print(f"Skipping {path} - face could not be detected.")

    enroller.save_enrolled(db)
    print(f"Success! {name} has been enrolled using Google Photos.")

if __name__ == "__main__":
    main()