"""
Cada que quiera iniciar a trabajar:
source venv/bin/activate
safaridriver --enable

Para correrlo: python3 -u opti.py & disown
Matar procesos despues: ps aux | grep opti.py
    Librerias:
        #pip install selenium
        #safaridriver --enable
        #pip3 install pandas openpyxl
    """
    


import pandas as pd
import os
import csv
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

RFC_ID = 'ctl00_MainContent_Wizard1_TextBox1'
CORREO_ID = 'ctl00_MainContent_Wizard1_TextBox2'
ENVIAR_ID = 'ctl00_MainContent_Wizard1_StartNavigationTemplateContainerID_StartNextButton'

EXCEL_PATH = 'eventos.xlsx'   # <- ajusta el nombre/ruta real de tu archivo
LOG_FILE = 'eventos_cofidi.csv'


def buscar_datos_evento(id_evento):
    """Busca el ID de evento en el Excel y regresa (rfc, correo, nombre)."""
    df = pd.read_excel(EXCEL_PATH, dtype=str)
    fila = df[df['ID'] == str(id_evento)]

    if fila.empty:
        raise ValueError(f"No se encontró el ID de evento '{id_evento}' en el Excel")

    rfc = fila.iloc[0]['RFC']
    correo = fila.iloc[0]['Correo']
    nombre = fila.iloc[0]['Nombre']   # <- ajusta al nombre real de esa columna en tu Excel

    return rfc, correo, nombre


def crear_carpeta_evento(id_evento, nombre):
    """Crea una carpeta tipo 'Eventoid . Nombre' y regresa su ruta."""
    nombre_carpeta = f"{id_evento} . {nombre}"
    ruta_carpeta = os.path.join(CARPETA_SCRIPT, nombre_carpeta)
    os.makedirs(ruta_carpeta, exist_ok=True)
    return ruta_carpeta

def guardar_evento(id_evento, rfc, correo, estado):
    existe = os.path.exists(LOG_FILE)
    with open(LOG_FILE, mode='a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        if not existe:
            writer.writerow(['fecha_hora', 'id_evento', 'rfc', 'correo', 'estado'])
        writer.writerow([datetime.now().isoformat(), id_evento, rfc, correo, estado])



def cofidi(rfc, correo, id_evento):
    driver = webdriver.Safari()
    estado = 'iniciado'
    try:
        driver.get('https://red.cofidi.com.mx/Upload.aspx')
        time.sleep(2)

        driver.find_element(By.ID, RFC_ID).send_keys(rfc, Keys.TAB)
        

        correo_field = WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((By.ID, CORREO_ID))
        )
        correo_field.send_keys(correo)
        
        
        enviar_btn = WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((By.ID, 'ctl00_MainContent_Wizard1_StartNavigationTemplateContainerID_StartNextButton'))
        )
        enviar_btn.click()
        estado = 'enviado'
        print("Send")
        


    except Exception as e:
        estado = f'error: {type(e).__name__}'
        print(f" ERROR: {type(e).__name__}: {e}")
        
    finally:
        guardar_evento(id_evento, rfc, correo, estado)   # ahora sí se llama

    return driver

#-----------------Flujo de programa--------------#
CARPETA_SCRIPT = os.path.dirname(os.path.abspath(__file__))

try:
    id_evento = input("Ingresa número de ID de evento: ")

    rfc, correo, nombre = buscar_datos_evento(id_evento)
    print(f"Datos encontrados -> RFC: {rfc} | Correo: {correo} | Nombre: {nombre}")
    
    carpeta_evento = crear_carpeta_evento(id_evento, nombre)

    driver = cofidi(rfc, correo, id_evento)
    

except Exception as e:
    print(f" ERROR en el flujo principal: {type(e).__name__}: {e}")
    

while True:
    time.sleep(3600)
    

