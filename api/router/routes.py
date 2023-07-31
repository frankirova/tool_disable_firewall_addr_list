from fastapi import APIRouter, Request, HTTPException
from api.controllers.sheets import get_sheet_values
from api.controllers.mikrotik import connect_to_mikrotik, get_addresses, add_suspended_address, show_suspend_address, suspend_address
import pymongo

router = APIRouter()

@router.post("/preview")
async def preview(request: Request):
    try:
        data = await request.json()

        # obtengo la data de sheets
        sheet_list = get_sheet_values(data)
        # conexion con la api Miktoik
        api = await connect_to_mikrotik(data)
        # obtengo el address list
        addr_list_ip = await get_addresses(api, sheet_list)

        addr_list_updated = await add_suspended_address(addr_list_ip, sheet_list, api)
        # await disconnect_mikrotik(api)
        return await show_suspend_address(sheet_list, addr_list_updated, data)
    except Exception as e:
        # Manejo de la excepción
        print("Ocurrió un error:", str(e))
        raise HTTPException(status_code=500, detail='Error en los datos ingresados al formulario')

@router.post("/script")
async def main(request: Request):
    try:
        data = await request.json()
        # obtengo la data de sheets
        sheet_list = get_sheet_values(data)
        # conexion con la api Miktoik
        api = await connect_to_mikrotik(data)
        # obtengo el address list
        addr_list_ip =await  get_addresses(api, sheet_list)

        addr_list_updated =await add_suspended_address(addr_list_ip, sheet_list, api)

        await suspend_address(api, sheet_list, addr_list_updated, data)
        return {'message':'done'}
    except Exception as e:
        # Manejo de la excepción
        print("Ocurrió un error:", str(e))
        raise HTTPException(status_code=500, detail="Error ejecutando la accion en mikrotik")

@router.post("/addOptions")
async def addOptions():
    data = [
        "192.168.2.238",
        "64.76.121.146",
        "64.76.121.147",
        "64.76.121.143",
        "64.76.121.243",
        "168.194.32.50",
        "168.194.32.71",
        "168.194.32.21",
        "168.194.32.14",
        "168.194.34.196",
        "168.194.34.197",
    ]
    
    try:
        # Configuración de la conexión a MongoDB
        mongo_client = pymongo.MongoClient("mongodb+srv://franki:TEVuNkEx7Qev9KDp@cluster0.sdqqh1u.mongodb.net/")
        db = mongo_client["cortes-redmetro"]  # Reemplaza "nombre_basedatos" con el nombre de tu base de datos
        collection = db["options"]  # Reemplaza "nombre_coleccion" con el nombre de tu colección

        # Insertar los datos en la colección
        for item in data:
            document = {'option':item}
            collection.insert_one(document)

        return {"message": "Datos agregados correctamente"}

    except Exception as e:
        print("Ocurrió un error:", str(e))
        raise HTTPException(status_code=500, detail="Error al agregar los datos a MongoDB")

@router.get("/readOptions")
async def readOptions():

    try:
        # Configuración de la conexión a MongoDB
        mongo_client = pymongo.MongoClient("mongodb+srv://franki:TEVuNkEx7Qev9KDp@cluster0.sdqqh1u.mongodb.net/")
        db = mongo_client["cortes-redmetro"]  # Reemplaza "nombre_basedatos" con el nombre de tu base de datos
        collection = db["options"]  # Reemplaza "nombre_coleccion" con el nombre de tu colección

        # Consulta todos los documentos en la colección
        documents = collection.find()

        # Crea una lista para almacenar los datos leídos
        data = []
        for document in documents:
            data.append(document["option"])

        return {"data": data}

    except Exception as e:
        print("Ocurrió un error:", str(e))
        raise HTTPException(status_code=500, detail="Error al leer los datos de MongoDB")

@router.post('/addDoc')
async def addDoc(request: Request):
    data = await request.json()
    option = data.get('option')

    # Configuración de la conexión a MongoDB
    mongo_client = pymongo.MongoClient("mongodb+srv://franki:TEVuNkEx7Qev9KDp@cluster0.sdqqh1u.mongodb.net/")
    db = mongo_client["cortes-redmetro"]
    collection = db["options"]

    # Documento a insertar
    documento = {
        "option": option
    }

    try:
        # Insertar el documento en la colección
        collection.insert_one(documento)
        print("Documento agregado correctamente")

    except Exception as e:
        print("Ocurrió un error:", str(e))
