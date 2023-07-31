import routeros_api
from fastapi import HTTPException
import os
from dotenv import load_dotenv

# from app import config

async def connect_to_mikrotik(data):
    try:
        IP_MIKROTIK = data.get('IP_MIKROTIK')
        load_dotenv()
        PASS_MIKROTIK = os.getenv('PASS_MIKROTIK')
        USER_MIKROTIK = os.getenv('USER_MIKROTIK')
    # conexion con la api Miktoik
        connection = routeros_api.RouterOsApiPool(IP_MIKROTIK, username=USER_MIKROTIK, password=PASS_MIKROTIK, plaintext_login=True)
        api = connection.get_api()
        return api
    except Exception as e:
        # Manejo de la excepción
        print("Ocurrió un error:", str(e))
        raise HTTPException(status_code=500, detail='Error en mikrotik')

async def get_addresses(api, sheet_list):
            # obtengo el address list de la lista 'Suspendido'
        response = api.get_resource("/ip/firewall/address-list").get(list='suspendido')
        addr_list = []
        susp_list = []
        # si no esta en addr_list lo agregamos
        for ip in response:
            addr_list.append({'ip': ip['address'], 'comment': ip['comment'], 'id':ip['id']})  # ips mkt

        for item in addr_list:
            if item in sheet_list:
                susp_list.append(item)

        addr_list_ip = []
        for ip in addr_list:
            addr_list_ip.append(ip['ip'])
        return addr_list_ip

async def add_suspended_address(addr_list_ip, sheet_list, api):
    for item in sheet_list:
            if item['ip'] not in addr_list_ip:
                created_client = api.get_resource("/ip/firewall/address-list").add(address=item['ip'], list='suspendido', comment=item['nombre'])
    response = api.get_resource("/ip/firewall/address-list").get(list='SUSPENDIDOS')

    addr_list_updated = []
    for ip in response:
        addr_list_updated.append({'ip': ip['address'], 'comment': ip['comment'],'id':ip['id']})  # ips mkt
    return addr_list_updated

async def suspend_address(api, sheet_list, addr_list_updated, data):
    # recorro response para generar una lista que solo contenga el id + la ip + comentario (lista de suspendidos)
        DATE = data.get('DATE')

        susp_list = []
        for id in addr_list_updated:
            if id in addr_list_updated:
                item = ({'id': id['id'], 'address': id['ip'], 'comment': id['comment']})
                susp_list.append(item)    # id + ip a suspender

        # recorro susp_list para generar la lista de suspension que contiene solamente los id de las ip que coinciden con addr_list
        susp_list_id = []
        for ip in sheet_list:
            for item in susp_list:
                if item['address'] == ip['ip']:
                    # Si el nombre coincide, agregar el diccionario a la lista susp_list_id
                    susp_list_id.append(item['id'])  # lista de los ids a suspender

        comment_list = []
        for comment in susp_list:
            for item in sheet_list:
                if item['ip'] == comment['address']:
                    item = {'id': comment['id'], 'comment': comment['comment']}
                    comment_list.append(item)   # lista de comentarios

        fecha = f"// SUSPENDIDO - {DATE}"
        comment_finally = []
        for com in comment_list:
            item = {'id': com['id'], 'comment': com['comment'] + fecha}
            comment_finally.append(item)

        # recorro susp_list_id para ejecutar la accion de suspender en mikrotik en cada iteracion
        for id_suspense in susp_list_id:
            id_suspense_list = api.get_resource("/ip/firewall/address-list").set(id=id_suspense, disabled='false') # lista que se suspendio (accion ejecutada)

        # recorro comment_list para ejecutar la accion de editar el comentario en mikrotik en cada iteracion
        for comment_suspense in comment_finally:
            comment_suspense_list = api.get_resource("/ip/firewall/address-list").set(id=comment_suspense['id'], comment=comment_suspense['comment'])

        return {'message': 'done'}

async def show_suspend_address(sheet_list, addr_list_updated, data, ):
        # recorro response para generar una lista que solo contenga el id + la ip + comentario (lista de suspendidos)
        DATE = data.get('DATE')

        susp_list = []
        for id in addr_list_updated:
            if id in addr_list_updated:
                item = ({'id': id['id'], 'address': id['ip'], 'comment': id['comment']})
                susp_list.append(item)    # id + ip a suspender

        # recorro susp_list para generar la lista de suspension que contiene solamente los id de las ip que coinciden con addr_list
        susp_list_id = []
        for ip in sheet_list:
            for item in susp_list:
                if item['address'] == ip['ip']:
                    # Si el nombre coincide, agregar el diccionario a la lista susp_list_id
                    susp_list_id.append(item['id'])  # lista de los ids a suspender

        # addr_list_updated_in_sheets = []
        # for i in addr_list_updated:
        #     for e in sheet_list:
        #         if i['ip'] == e['ip']:
        #             item = {'ip': i['ip'], 'comment': i['comment'], 'id':i['id']}
        #             addr_list_updated_in_sheets.append(item)

        comment_list = []
        for comment in susp_list:
            for item in sheet_list:
                if item['ip'] == comment['address']:
                    item = {'id': comment['id'], 'comment': comment['comment']}
                    comment_list.append(item)   # lista de comentarios

        fecha = f"// SUSPENDIDO - {DATE}"
        comment_finally = []
        for com in comment_list:
            item = {'id': com['id'], 'comment': com['comment'] + fecha}
            comment_finally.append(item)

        return [comment_list, comment_finally]
