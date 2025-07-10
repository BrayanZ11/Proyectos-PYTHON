'''
Este codigo esta escrito en Python 3.10
Requiere instalar OpenCV: pip install opencv-python
Este codigo reproducira imagenes y videos de una carpeta especificada sera un regalo para alguien especial.
se utilizara una rapsberry pi para reproducirlo en una pantalla de 3.5 pulgadas.
El codigo se ejecutara en un bucle infinito, mostrando cada imagen durante 6 segundos y reproduciendo cada video hasta que se presione 's'.
'''
import os, cv2, time

import os
import cv2
import time
import subprocess

# --- Detectar resolución de pantalla ---
def obtener_resolucion_pantalla():
    try:
        output = subprocess.check_output(['xdpyinfo']).decode()
        for line in output.splitlines():
            if "dimensions:" in line:
                dims = line.split()[1]
                width, height = map(int, dims.split('x'))
                return (width, height)
    except Exception as e:
        print(" No se pudo detectar la resolución automáticamente:", e)
        return (480, 320)

# --- Rutas (ajústalas para tu Raspberry Pi) ---
Url_carpeta = 'C:\\Users\\RRAIGOSA\\Pictures\\Placas test'  #aqui cambia la ruta donde estan las imagenes y videos
url_Meses = 'C:\\Users\\RRAIGOSA\\Pictures\\Fondos de pantalla puestos\\wallhaven-gjjrml.png' 


Tipo_imagen = ('.jpg', '.jpeg', '.png', '.bmp', '.gif')
Tipo_video = ('.mp4', '.avi', '.mov', '.mkv')

# --- Resolución de pantalla ---
RESOLUCION_PANTALLA = obtener_resolucion_pantalla()
print(f"🖥️ Resolución detectada: {RESOLUCION_PANTALLA}")

# Crear ventana pantalla completa una sola vez
cv2.namedWindow('Visor multimedia', cv2.WINDOW_FULLSCREEN)
cv2.setWindowProperty('Visor multimedia', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

# --- Funciones de reproducción ---
def Play_imainicio(ruta_logo):
    if not os.path.exists(ruta_logo):
        print(' No se encontró la imagen de inicio')
        return
    imagen = cv2.imread(ruta_logo)
    if imagen is None:
        print(f' No se pudo cargar: {ruta_logo}')
        return
    imagen = cv2.resize(imagen, RESOLUCION_PANTALLA)
    cv2.imshow('Visor multimedia', imagen)
    print(" Mostrando imagen de inicio")
    cv2.waitKey(5000)

def Play_imagen(ruta):
    imagen = cv2.imread(ruta)
    if imagen is None:
        print(f' No se pudo cargar la imagen: {ruta}')
        return
    imagen = cv2.resize(imagen, RESOLUCION_PANTALLA)
    cv2.imshow('Visor multimedia', imagen)
    print(f" Mostrando imagen: {os.path.basename(ruta)}")
    cv2.waitKey(6000)

def Play_video(ruta):
    video = cv2.VideoCapture(ruta)
    if not video.isOpened():
        print(f' No se pudo cargar el video: {ruta}')
        return
    print(f"🎥 Reproduciendo video: {os.path.basename(ruta)}")
    while video.isOpened():
        ret, frame = video.read()
        if not ret:
            break
        frame = cv2.resize(frame, RESOLUCION_PANTALLA)
        cv2.imshow('Visor multimedia', frame)
        if cv2.waitKey(30) & 0xFF == ord('s'):
            break
    video.release()

# --- Verifica carpeta ---
if not os.path.isdir(Url_carpeta):
    print(f' La carpeta no existe: {Url_carpeta}')
    exit()

# --- Imagen de inicio ---
Play_imainicio(url_Meses)

# --- Bucle infinito ---
while True:
    archivos = sorted(os.listdir(Url_carpeta))
    for archivo in archivos:
        ruta_archivo = os.path.join(Url_carpeta, archivo)

        if os.path.isfile(ruta_archivo):
            if archivo.lower().endswith(Tipo_imagen):
                Play_imagen(ruta_archivo)
            elif archivo.lower().endswith(Tipo_video):
                Play_video(ruta_archivo)

        if cv2.waitKey(1) & 0xFF == ord('b'):  # Salir con 'b'
            print(" Saliendo del visor multimedia.")
            cv2.destroyAllWindows()
            exit()

    # Espera un segundo antes de volver a empezar
    time.sleep(1)
