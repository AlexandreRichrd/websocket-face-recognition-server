import asyncio
import websockets
import os
from io import BytesIO
import json
import base64


from face_reco import generate_face_encodings, compare_encodings


async def echo(websocket, path):
    async for message in websocket:
        # Déterminer si le message est de type bytes (données binaires)
        if isinstance(message, bytes):
            # Créer un BytesIO à partir des données binaires
            image_data = BytesIO(message)

            # Définir le chemin du fichier où l'image sera enregistrée
            file_path = os.path.join('encodings/queue', 'received_image.jpg')

            # Enregistrer l'image
            with open(file_path, 'wb') as file:
                file.write(image_data.getbuffer())

            print(f"Image enregistrée sous : {file_path}")

            # Générer les encodages de visage
            generate_face_encodings(file_path, 'encodings/')

            # Comparer les encodages
            name = await compare_encodings()

            print(name)

            # Envoyer le résultat de la comparaison
            await websocket.send(name)


        # Déterminer si le message est de type str (chaîne de caractères)
        elif isinstance(message, str):
            data = json.loads(message)
            image_data = base64.b64decode(data['image'].split(',')[1])
            name = data['name']

            file_path = os.path.join('models', f"{name}.jpg")
            index = 1
            while os.path.exists(file_path):
                file_path = os.path.join('models', f"{name}_{index}.jpg")
                index += 1
            with open(file_path, 'wb') as file:
                file.write(image_data)

            print(f"Image enregistrée sous : {file_path}")
            await websocket.send(f"Image reçue et en cours et traîtée.")

            # Générer les encodages de visage
            generate_face_encodings(file_path, 'models/encodings/')


        else:
            print(message)
            await websocket.send(message)


async def main():
    # Assurez-vous que le dossier 'models' existe
    if not os.path.exists('models'):
        os.makedirs('models')
    if not os.path.exists('models/encodings'):
        os.makedirs('models/encodings')
    if not os.path.exists('encodings/queue'):
        os.makedirs('encodings/queue')

    async with websockets.serve(echo, 'localhost', 8765):
        await asyncio.Future()  # run forever


asyncio.run(main())
