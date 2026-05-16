import config
import numpy as np

threshold = config.SIMILARITY_THRESHOLD

def find_match(embedding, db):
    best_match_name = "Unknown"
    highest_similarity = -1.0
    norm_a = np.linalg.norm(embedding)

    for name, embedding_list in db.items():
        for stored_embedding in embedding_list:
            dot_product = np.dot(embedding, stored_embedding)
            norm_b = np.linalg.norm(stored_embedding)
            if norm_a == 0 or norm_b == 0:
                continue
                
            similarity = dot_product / (norm_a * norm_b)
            if similarity > highest_similarity:
                highest_similarity = similarity
                best_match_name = name

    if highest_similarity < threshold:
        return "Unknown"
    
    return best_match_name