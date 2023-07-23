from concurrent.futures import thread
from urllib import response
import websocket
import json
import threading
import time
from email import header
import requests
import sys
import re
import os
from websocket import create_connection
from websocket._exceptions import WebSocketConnectionClosedException
import mysql.connector
import gspread
import json
import requests
import easyocr
import os
import torch
print(torch.cuda.is_available())
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(torch.__version__)
print(torch.version.cuda)
print(torch.cuda.is_available())
print(device)



from oauth2client.service_account import ServiceAccountCredentials


codigo = 'DISCORD_GATEWAY_API'


os.environ['CUDA_VISIBLE_DEVICES'] = '0' # Reemplaza 0 con el número de tu GPU

# Autenticar con las credenciales del servicio de Google Sheets
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('google_credentials.json', scope)
client = gspread.authorize(creds)

# Abrir la hoja de cálculo por URL
sheet_url = 'URL-GOOGLE-DOCS'
sheet = client.open_by_url(sheet_url)

# Seleccionar la hoja de la que queremos actualizar la celda
worksheet = sheet.get_worksheet(0)


def send_messages(channelid, message):
        payload = {
                'content': message
        }

        header = { 
                'authorization': codigo
        }

        r = requests.post(f'https://discord.com/api/v9/channels/{channelid}/messages',
                                data=payload, headers=header)

# Pillar mensajes a pelo usando credenciales key
def retrive_messages(channelid):
        headers = { 
                'authorization': codigo
        }

        r = requests.get(f'https://discord.com/api/v9/channels/{channelid}/messages', headers=headers)

        jsonn = json.loads(r.text)
        for value in jsonn:
                print(value, '\n')

def send_json_request(ws, request):
    ws.send(json.dumps(request))

def con_ws():
    ws = websocket.WebSocket()
    ws.connect('wss://gateway.discord.gg/?v=6&encording=json')
    event = recieve_json_response(ws)

# traducion del response json
def recieve_json_response(ws):
    response = ws.recv()
    if response:
        return json.loads(response)

#latido
def heartbeat(interval, ws):
    print('Heartbeat begin')
    while True:
        time.sleep(interval)
        heartbeatJSON = {
            "op": 1,
            "d": "null"
        }
        send_json_request(ws, heartbeatJSON)
        print("heartbeat sent")

# Web socket y su thread, configuracion del token de navegador y load + datos
ws = websocket.WebSocket()
ws.connect('wss://gateway.discord.gg/?v=6&encording=json')
event = recieve_json_response(ws)

heartbeat_interval = event['d']['heartbeat_interval'] / 1000
threading._start_new_thread(heartbeat, (heartbeat_interval, ws))

token = codigo
payload = {
    'op': 2,
    "d": {
        "token": token,
        "properties": {
            "$os": "windows",
            "$browser": "chrome",
            "$device": "pc"
        }
    }
}

send_json_request(ws, payload)
message_info = ""


def row(text):
    global descartado
    global value1
    #print(lines)
    pattern = re.compile(r'(\d{1,3})')
    match = re.findall(pattern, text)


    if len(match) == 1:
        # Convertir los números a enteros
        value1 = int(match[0])
    
    return value1

imagenes = []

def procesar_imagenes(mensaje):
    global imagenes
    imagenes = []
    for attachment in mensaje['d']['attachments']:
        if attachment['content_type'].startswith('image/'):
            imagen_url = attachment['url']
            imagen_respuesta = requests.get(imagen_url)
            imagen_bytes = imagen_respuesta.content
            resultado_easyocr = easyocr.Reader(['es'], gpu=True).readtext(imagen_bytes)
            texto_encontrado = ""
            for resultado in resultado_easyocr:
                texto_encontrado += resultado[1] + " "
            imagenes.append(texto_encontrado.strip())
        print(imagenes)
    return imagenes

def formatear_mac(mac):
    # Eliminar caracteres no deseados
    mac = re.sub(r'[^a-fA-F0-9]', '', mac)

    # Dividir en bloques de dos caracteres y unir con ":"
    mac = ":".join([mac[i:i+2] for i in range(0, 12, 2)])
    return mac.upper()

value1 = "0"
while True:
    re_reconex = "false"

    try:
        event = recieve_json_response(ws)
        #print(event)
        op_code = f"{event['op']}"
        #print (op_code)
        #print (event)
    except:
        print ('receive no funciona')
        re_reconex = "true"
        
  
    if re_reconex == 'true':
        re_reconex = "false"
        print('reconectando......')
        time.sleep(5)
        ws = websocket.WebSocket()
        ws.connect('wss://gateway.discord.gg/?v=9&encoding=json')
        event = recieve_json_response(ws)
        heartbeat_interval = event['d']['heartbeat_interval'] / 1000
        +threading._start_new_thread(heartbeat, (heartbeat_interval,ws))
        print(event)
        send_json_request(ws, payload)
    
    try:
        # almacena temporalmente el id del canal  y su contenido para confirmar que es mensaje de nova y donde mandarse
        # Guardo en variable canal id y su mensaje
        #print(f"{event['d']['author']['username']}: {event['d']['content']} {event['d']['channel_id']}")
        descartado = 0
        pedido = 0
        canal_id  = f"{event['d']['channel_id']}"
        mensaje_nova = f"{event['d']['content']}"
        mensaje_nova_id = f"{event['d']['id']}"
        value1 = "0"

        match canal_id:
            case "1080843353081524267":
                id_to_send = '1080843353081524267'
                pedido = 1
            case "1080988052106793061":
                id_to_send = '1080988052106793061'
                pedido = 2
            case "1081016966942306334":
                id_to_send = '1081016966942306334'
                pedido = 3
            case _:
                pedido = 0
        descartado = 0

        imagenes = []
        if pedido == 1:
            fila = row(mensaje_nova)
            fila_int = int(fila)
            print(event)
            procesar_imagenes(event)
            worksheet.update_cell(fila_int,1,imagenes[0])
            send_messages(id_to_send, 'Datos insertados..... :white_check_mark: ')
            send_messages(id_to_send, 'Datos insertados:' + imagenes[0] )


            #print(f"Updated cell {fila}, {columna} with '{dispositivo}' y '{mac}'")
        if pedido == 2:
            fila = row(mensaje_nova)
            fila_int = int(fila)
            print(event)
            procesar_imagenes(event)
            converted_mac_address = formatear_mac(imagenes[0])
            print(converted_mac_address)
            worksheet.update_cell(fila_int,2,converted_mac_address)
            send_messages(id_to_send, 'Datos insertados..... :white_check_mark: ')
            send_messages(id_to_send, 'Datos insertados:' + converted_mac_address )

            #print(f"Updated cell {fila}, {columna} with '{dispositivo}' y '{mac}'")
        if pedido == 3:
            fila = row(mensaje_nova)
            fila_int = int(fila)
            print(event)
            procesar_imagenes(event)
            worksheet.update_cell(fila_int,5,imagenes[0])
            send_messages(id_to_send, 'Datos insertados..... :white_check_mark: ')
            send_messages(id_to_send, 'Datos insertados:' + imagenes[0] )


    except:
        pass
          
