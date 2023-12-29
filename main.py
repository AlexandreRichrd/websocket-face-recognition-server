import asyncio
import websockets
import os
from io import BytesIO
import json
import base64


async def echo(websocket, path):
    async for message in websocket:
        # Déterminer si le message est de type bytes (données binaires)
        if isinstance(message, bytes):
            # Créer un BytesIO à partir des données binaires
            image_data = BytesIO(message)



            # Définir le chemin du fichier où l'image sera enregistrée
            file_path = os.path.join('models', 'received_image.jpg')

            # Enregistrer l'image
            with open(file_path, 'wb') as file:
                file.write(image_data.getbuffer())

            print(f"Image enregistrée sous : {file_path}")
            await websocket.send(f"Image reçue et enregistrée sous : {file_path}")
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
            await websocket.send(f"Image reçue et enregistrée sous : {file_path}")


        else:
            print(message)
            await websocket.send(message)


async def main():
    # Assurez-vous que le dossier 'models' existe
    if not os.path.exists('models'):
        os.makedirs('models')

    async with websockets.serve(echo, 'localhost', 8765):
        await asyncio.Future()  # run forever


asyncio.run(main())
