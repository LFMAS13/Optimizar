"""
Cada que quiera iniciar a trabajar (Windows):
    pip install pandas openpyxl selenium
    python opti.py

Ver procesos activos (si se necesita matar alguno):
    tasklist | findstr python
    taskkill /PID <numero> /F
"""

from selenium.webdriver.chrome.service import Service
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
import re

RFC_ID = 'ctl00_MainContent_Wizard1_TextBox1'
CORREO_ID = 'ctl00_MainContent_Wizard1_TextBox2'
ENVIAR_ID = 'ctl00_MainContent_Wizard1_StartNavigationTemplateContainerID_StartNextButton'

EXCEL_PATH = 'BASE SC-BE-S 26 copia 2.xlsx'
EXCEL_SHEET = 'Nacionales'
LOG_FILE = 'eventos_cofidi.csv'

#HPR LOGIN
USER_ID = 'Result_UserName'
PASSWORD_ID = 'Result_Password'
LOGIN_BTN_SELECTOR = '.btn.btn-default.btn-block'

#Credenciales
USUARIO_HPR = 'mvizzuet@its.jnj.com'
PASSWORD_HPR = 'Marieventos2026.'

#-----------------Flujo de programa--------------#
CARPETA_SCRIPT = os.path.dirname(os.path.abspath(__file__))
CHROMEDRIVER_PATH = os.path.join(CARPETA_SCRIPT, 'chromedriver.exe')


def buscar_datos_evento(id_evento):
    """Busca el ID de evento en el Excel y regresa (rfc, correo, nombre)."""
    df = pd.read_excel(EXCEL_PATH, sheet_name=EXCEL_SHEET, dtype=str)
    df.columns = df.columns.str.strip()

    fila = df[df['Número de evento'] == str(id_evento)]

    if fila.empty:
        raise ValueError(f"No se encontró el ID de evento '{id_evento}' en el Excel")

    rfc = fila.iloc[0]['ID Vendor']
    correo = fila.iloc[0]['Dirección correo elec. ponente/consultor']
    nombre = fila.iloc[0]['Nombre Speaker']

    return rfc, correo, nombre


def limpiar_nombre_carpeta(texto):
    """Quita caracteres no válidos para nombres de carpeta en Windows."""
    return re.sub(r'[\\/:*?"<>|]', '', texto).strip()


def crear_carpeta_evento(id_evento, nombre):
    nombre_limpio = limpiar_nombre_carpeta(nombre)
    nombre_carpeta = f"{id_evento} . {nombre_limpio}"
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
    driver = webdriver.Chrome(service=Service(CHROMEDRIVER_PATH))
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
            EC.element_to_be_clickable((By.ID, ENVIAR_ID))
        )
        enviar_btn.click()
        estado = 'enviado'
        print("Send")

    except Exception as e:
        estado = f'error: {type(e).__name__}'
        print(f" ERROR: {type(e).__name__}: {e}")

    finally:
        guardar_evento(id_evento, rfc, correo, estado)

    return driver


def login_hpr(user, password):
    driver = webdriver.Chrome(service=Service(CHROMEDRIVER_PATH))
    try:
        driver.get('https://hpr.jnj.com/LogOn/Login?ReturnUrl=%2flogin')
        time.sleep(2)

        driver.find_element(By.ID, USER_ID).send_keys(user)
        driver.find_element(By.ID, PASSWORD_ID).send_keys(password)

        login_btn = WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, LOGIN_BTN_SELECTOR))
        )
        login_btn.click()

        print("Login enviado")

    except Exception as e:
        print(f" ERROR: {type(e).__name__}: {e}")

    return driver


def buscar_eventos_hpr(driver, id_evento):
    try:
        url_busqueda = f'https://hpr.jnj.com/Home/SearchList?Keyword={id_evento}'
        driver.get(url_busqueda)
        time.sleep(2)

    except Exception as e:
        print(f" ERROR: {type(e).__name__}: {e}")

    return driver


try:
    id_evento = input("Ingresa número de ID de evento: ")

    rfc, correo, nombre = buscar_datos_evento(id_evento)
    print(f"Datos encontrados -> RFC: {rfc} | Correo: {correo} | Nombre: {nombre}")

    carpeta_evento = crear_carpeta_evento(id_evento, nombre)

    driver_cofidi = cofidi(rfc, correo, id_evento)

    driver_hpr = login_hpr(USUARIO_HPR, PASSWORD_HPR)
    driver_hpr = buscar_eventos_hpr(driver_hpr, id_evento)

except Exception as e:
    print(f" ERROR en el flujo principal: {type(e).__name__}: {e}")

while True:
    time.sleep(3600)