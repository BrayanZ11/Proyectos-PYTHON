'''
En este codigo se utiliza el lenguaje de programacion de python 
con el fin de utilizar la informacion que la API nos devuelve
este codigo al presionar el boton imprimira el recibo con los datos que 
nos trae la api desde el sistema, se cuenta con una impresora "Kiosk printer
model: SMK3S-H120", con este codigo se prueba la configuracion de 
impresion y el correcto funcionamiento de la API
'''

import time
import logging
import requests
from gpiozero import Button
from escpos.printer import Usb

# Configuración de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Configuraciones
BUTTON_GPIO = 26 #PIN DE RASPBERRY 
API_URL = "http://192.168.x.xx:port/api/Entry/Access/{}/Info"  

PRINTER_VENDOR_ID = 0x0525
PRINTER_PRODUCT_ID = 0xa700
PRINTER_USB_BUS = None
PRINTER_USB_ADDRESS = None

# Inicialización
Pulsador = Button(BUTTON_GPIO)
logging.info(f"Botón configurado en GPIO {BUTTON_GPIO}.")
printer = None

# Inicializa la impresora
def setup_printer():
    global printer
    try:
        printer = Usb(PRINTER_VENDOR_ID, PRINTER_PRODUCT_ID, PRINTER_USB_BUS, PRINTER_USB_ADDRESS)
        logging.info("Impresora USB inicializada exitosamente.")
        return True
    except Exception as e:
        logging.error(f"Error al inicializar la impresora USB: {e}")
        return False

# Obtiene datos de la API
def obtener_datos(ticket_id=1):
    try:
        response = requests.get(API_URL.format(ticket_id), timeout=5)
        response.raise_for_status()
        datos = response.json()
        info = datos.get("entryTicketInfo", {})  # Ajusta si cambia el JSON
        parkingInfo = datos.get("parkingInfo", {})
        print("Respuesta cruda de la API:", response.text)

        resultado = {
            "matricula": info.get("plateNumber", "N/A"),
            "tipo_vehiculo": info.get("vehicleType", "N/A"),
            "foto": info.get("fotoMatricula", None),
            "tipo_acceso": info.get("tipoAcceso", "N/A"),
            "punto_marcacion": info.get("puntoMarcacion", "N/A"),
            "fecha": info.get("entranceTimeStamp", ""),
            "parqueadero": parkingInfo.get("name", "")
        }

        logging.info(f"Datos obtenidos de la API: {resultado}")
        return resultado
    except Exception as e:
        logging.error(f"Error al obtener datos de la API: {e}")
        return None

# Imprime el ticket
def print_ticket():
    if printer:
        try:
            datos = obtener_datos()
            if not datos:
                printer.text("Error al obtener datos del ticket.\n")
                printer.cut()
                return

            printer.set(align='center')
            printer.text(f"--- {datos['parqueadero']} ---\n")
            printer.text("------------------------\n")
            printer.set(align='left')
            printer.text(f"Fecha: {datos['fecha']}\n")
            printer.text(f"Matrícula: {datos['matricula']}\n")
            printer.text(f"Tipo de vehículo: {datos['tipo_vehiculo']}\n")
            printer.text(f"Tipo de acceso: {datos['tipo_acceso']}\n")
            printer.text(f"Punto de marcación: {datos['punto_marcacion']}\n")
            
            printer.set(align='center')
            printer.text("\n¡Gracias por su visita!\n")
            printer.text("Visita nuestra web: ejemplo.com\n")
            printer.text("------------------------\n")
            printer.cut()
            logging.info("Ticket impreso exitosamente.")
        except Exception as e:
            logging.error(f"Error durante la impresión: {e}")
    else:
        logging.warning("Impresora no fue inicializada. No es posible imprimir el ticket.")

# Evento al presionar el botón
def boton_presionado():
    logging.info("Botón presionado, preparando impresión...")
    print_ticket()
    time.sleep(0.5)

# Programa principal
if __name__ == '__main__':
    logging.info("Iniciando script de impresión con botón.")
    printer_ready = setup_printer()

    if printer_ready:
        logging.info("Esperando el pulso para imprimir ticket...")
        try:
            Pulsador.when_pressed = boton_presionado
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            logging.info("Script terminado por el usuario (Ctrl+C).")
        except Exception as e:
            logging.error(f"Ha ocurrido un error en el bucle: {e}")
    else:
        logging.error("No se pudo iniciar la impresión por problemas con la impresora.")

    logging.info("Saliendo del script.")
