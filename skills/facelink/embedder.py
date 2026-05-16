import face_recognition as fr

class Embedder:
    def __init__(self):
        pass

    def load_model(self):
        print("Face recognition embedder ready.")

    def get_embedding(self, image, locations):
        encodings = fr.face_encodings(image, known_face_locations=locations)
        if len(encodings) == 0:
            return None
        return encodings[0]