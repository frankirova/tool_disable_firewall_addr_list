# app/google_sheets.py
from fastapi import HTTPException

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google.oauth2 import service_account
# from app import config

import os
from dotenv import load_dotenv

def get_sheet_values(data):
    try:
        SPREADSHEET_NAME = data.get('SPREADSHEET_NAME')
        SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
        load_dotenv()
        KEY = os.getenv('KEY')
        SPREADSHEET_ID = os.getenv('SPREADSHEET_ID')

        # conexion a google sheets
        creds = None
        creds = service_account.Credentials.from_service_account_file(KEY, scopes=SCOPES)

        service = build('sheets', 'v4', credentials=creds)
        sheet = service.spreadsheets()

        # obteniendo los valores
        result = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range=SPREADSHEET_NAME).execute()

        values = result.get('values', [])
        DATA_PARSED = []
        # Obtén los encabezados de la hoja de cálculo
        headers = values[0]

        # Convierte cada fila de la hoja de cálculo en un diccionario
        for row in values[1:]:
            data = {}
            for i in range(len(headers)):
                data[headers[i]] = row[i]
            DATA_PARSED.append(data)

        # creamos sheet_list
        sheet_list = []
        for client in DATA_PARSED:
            sheet_data = {'ip': client["ip"], 'nombre': client['nombre']}
            sheet_list.append(sheet_data)
            
        return sheet_list

    except Exception as e:
        # Manejo de la excepción
        print("Ocurrió un error:", str(e))
        raise HTTPException(status_code=500, detail='Error en los datos ingresados al formulario')
