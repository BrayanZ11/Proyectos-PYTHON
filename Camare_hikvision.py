import cv2
import sys
import os

#Configuración de la cámara Hikvision 
HIKVISION_USER = "admin"
HIKVISION_PASSWORD = "xxxxx" # Reemplaza con la contraseña de tu cámara
HIKVISION_IP = "192.168.3.xxx"  # Reemplaza con la IP de tu cámara
HIKVISION_RTSP_PORT = "xxx"   # Puerto RTSP 
HIKVISION_STREAM_PATH = "Streaming/Channels/101" # 101 para stream principal, 102 para substream

# Construir la URL RTSP
RTSP_URL = f"rtsp://{HIKVISION_USER}:{HIKVISION_PASSWORD}@{HIKVISION_IP}:{HIKVISION_RTSP_PORT}/{HIKVISION_STREAM_PATH}"

print(f"Intentando conectar a la cámara con URL: {RTSP_URL}")

def connect_and_display_camera(rtsp_url):
    try:
        cap = cv2.VideoCapture(rtsp_url)

        if not cap.isOpened():
            print(f"Error: No se pudo abrir el stream RTSP desde {rtsp_url}")
            print("Asegúrate de que la IP, usuario, contraseña y puerto sean correctos,")
            print("y que el stream RTSP esté habilitado en la configuración de la cámara.")
            sys.exit(1)

        print("Conexión exitosa a la cámara. Presiona 'q' para salir.")

        while True:
            ret, frame = cap.read()

            if not ret:
                print("Error: No se pudo leer el frame. El stream podría haberse detenido o hay un problema de red.")
                break

            #Redimensionar el frame si es demasiado grande para la pantalla de la Raspberry Pi
            width = int(frame.shape[1] * 0.8)
            height = int(frame.shape[0] * 0.8)
            frame = cv2.resize(frame, (width, height), interpolation=cv2.INTER_AREA)

            cv2.imshow('Hikvision ANPR Camera Stream (Presiona Q para salir)', frame)

            # Presiona 'q' para salir del bucle
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            elif cv2.waitKey(1) & 0xFF == ord('Q'):
                break

    except Exception as e:
        print(f"Ocurrió un error: {e}")
    finally:
        if 'cap' in locals() and cap.isOpened():
            cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    connect_and_display_camera(RTSP_URL)