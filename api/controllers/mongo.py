# app/mongodb.py
from pymongo import MongoClient
# from api import config
from fastapi import FastAPI, Request, HTTPException

def connect_to_mongodb():
    try:
        # Configuración de la conexión a MongoDB
        mongo_client = MongoClient("mongodb+srv://franki:TEVuNkEx7Qev9KDp@cluster0.sdqqh1u.mongodb.net/")
        db = mongo_client["cortes-redmetro"]  # Reemplaza "nombre_basedatos" con el nombre de tu base de datos
        return mongo_client, db
    except Exception as e:
        print("Ocurrió un error:", str(e))
        raise HTTPException(status_code=500, detail="Error al agregar los datos a MongoDB")

def insert_document(collection, document):
    try:
        # Insertar el documento en la colección
        result = collection.insert_one(document)
        # Obtener el ID del documento insertado
        inserted_id = result.inserted_id
        return(f"Documento insertado con ID: {inserted_id}")
    except Exception as e:
        # Manejar cualquier error durante la inserción
        print(f"Error al insertar el documento: {e}")

def find_documents(collection):
    try:
        # Realizar la consulta para obtener todos los documentos de la colección
        documents = collection.find()
        # Iterar sobre los documentos y mostrarlos
        for document in documents:
            return(document)
    except Exception as e:
        # Manejar cualquier error durante la consulta
        print(f"Error al buscar documentos: {e}")

