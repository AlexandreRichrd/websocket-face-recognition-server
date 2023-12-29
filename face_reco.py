import threading
import queue
import face_recognition
import numpy as np
import json
import os



# Paramètres
MAX_QUEUE_SIZE = 10
VIDEO_CAPTURE_INDEX = 0

# Files d'attente
frame_queue = queue.Queue(maxsize=MAX_QUEUE_SIZE)
processed_frame_queue = queue.Queue(maxsize=MAX_QUEUE_SIZE)


def generate_face_encodings(image_path, new_encoding_path):
    image = face_recognition.load_image_file(image_path)
    face_locations = face_recognition.face_locations(image)
    face_encodings = face_recognition.face_encodings(image, face_locations)

    face_encodings = [encoding.tolist() if isinstance(encoding, np.ndarray) else encoding for encoding in
                      face_encodings]

    # Save face encodings to a json file
    # TODO: Change the file path with the name from the main with index
    file_path = new_encoding_path + image_path.split('\\')[-1].split('.')[0] + '.json'

    with open(file_path, 'w') as f:
        json.dump(face_encodings, f)


async def compare_encodings():
    # On récupère tous les encodings depuis models/encodings
    encodings_path = 'models/encodings'
    encodings_files = os.listdir(encodings_path)

    # On récupère l'encoding de l'image à tester
    test_image_path = 'encodings/received_image.json'
    with open(test_image_path, 'r') as f:
        test_encoding = json.load(f)

    #  Check si test_encoding n'est pas vide
    if not test_encoding:
        print("No faces found in the image.")
        return 'inconnu'

    test_encoding = np.array(test_encoding[0]) 

    known_encodings = []
    known_names = []

    # Charger les encodings et les noms
    for file in encodings_files:
        with open(os.path.join(encodings_path, file), 'r') as f:
            encoding = json.load(f)
            if encoding:  # Check si encoding n'est pas vide
                known_encodings.append(encoding[0])
                known_names.append(file.replace('.json', ''))

    # Ensure we have known encodings before proceeding
    if not known_encodings:
        print("No known encodings loaded.")
        return 'inconnu'

    # Convertir les encodings en numpy arrays
    known_encodings = [np.array(encoding) for encoding in known_encodings]

    # Comparer les encodings
    face_distances = face_recognition.face_distance(known_encodings, test_encoding)
    best_match_index = np.argmin(face_distances)

   
    if best_match_index < len(known_names) and face_distances[best_match_index] < 0.6:
        return known_names[best_match_index]
    else:
        return 'inconnu'
