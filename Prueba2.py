'''
Este codigo fue escrito en el lenguaje de programacion pyython donde
se utilizo FASTAPI, este cuenta con una camara hikvision DS-TCG405-E y una
impresora "Kiosk printer model: SMK3S-H120" el desarrollo en el backend 
fue escrito en C#, este codigo por medio de la camara manda la informacion
al backend y el raspberry trae los datos de ella y este permite realizar
la impresion del ticket con los datos traidos desde la api. 
'''
import time
import threading
import logging
from datetime import datetime
from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional, Any
try:
    from gpiozero import Button
    GPIO_AVAILABLE = True
except ImportError:
    GPIO_AVAILABLE = False
    logging.warning("gpiozero no disponible - modo simulación")

try:
    from escpos.printer import Usb
    PRINTER_AVAILABLE = True
except ImportError:
    PRINTER_AVAILABLE = False
    logging.warning("escpos no disponible - modo simulación")

import uvicorn

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

BUTTON_GPIO = 26 #pin Boton raspberry
Pulsador = None
if GPIO_AVAILABLE:
    try:
        Pulsador = Button(BUTTON_GPIO)
        logging.info(f"Boton Conectado al pin {BUTTON_GPIO}")
    except Exception as e:
        logging.warning(f"No se pudo inicializar el botón GPIO: {e}")

PRINTER_VENDOR_ID = 0x0525
PRINTER_PRODUCT_ID = 0xa700
PRINTER_USB_BUS = None
PRINTER_USB_ADDRESS = None
printer = None

ultimo_evento = None
app = FastAPI()

class EntryTicketInfo(BaseModel):
    accessId: int
    plateNumber: str
    vehicleType: str
    entranceTimeStamp: str
    rate: str
    rateValue: float

class ParkingInfo(BaseModel):
    name: str
    address: str
    phone: str
    city: str
    nit: str
    logo: Optional[str] = None
    

class SoftwareInfo(BaseModel):
    companyName: str
    nit: str
    copyRight: str

class EventoEntrada(BaseModel):
    entryTicketInfo: EntryTicketInfo
    parkingInfo: ParkingInfo
    softwareInfo: SoftwareInfo

def setup_printer():
    global printer
    if not PRINTER_AVAILABLE:
        logging.info("Impresora en modo simulación")
        return True
    try:
        printer = Usb(PRINTER_VENDOR_ID, PRINTER_PRODUCT_ID, PRINTER_USB_BUS, PRINTER_USB_ADDRESS)
        logging.info("Impresora inicializada")
        return True
    except Exception as e:
        logging.error(f"Hay un error al iniciar la impresora: {e}")
        return False

def imprimir_ticket():
    global ultimo_evento	
	#glo
    if not PRINTER_AVAILABLE:
        logging.info("Simulando impresión de ticket")
        if ultimo_evento:
            datos = ultimo_evento.entryTicketInfo
            parqueadero = ultimo_evento.parkingInfo
            logging.info(f"Simulando impresión para vehículo: {datos.plateNumber}")
        else:
            logging.info("No hay datos para imprimir")
        return
    
    if not printer:
        logging.warning("No se inicializo la impresora")
        return
        
    if not ultimo_evento:
        logging.info("No hay datos para imprimir")
        try:
            printer.set(align='center')
            printer.text("---ERROR---\n")
            printer.text("No hay datos para imprimir \n")
            printer.text("Espere la deteccion del vehiculo.\n")
            printer.cut()
        except Exception as e:
            logging.error(f"Error al imprimir mensaje de fallo: {e}")
        return
        
    datos = ultimo_evento.entryTicketInfo
    parqueadero = ultimo_evento.parkingInfo
    software = ultimo_evento.softwareInfo
    
    try:
        parsed_time = datetime.strptime(datos.entranceTimeStamp, "%d/%m/%Y %H:%M")
        formatear_tiempo = parsed_time.strftime('%Y-%m-%d %H:%M:%S')
    except ValueError:
        logging.error(f"Error a parafrasear la fecha/hora '{datos.entranceTimeStamp}'. usando formato original.")
        formatear_tiempo = datos.entranceTimeStamp
        
    try:
        printer.set(align='center')
        printer.text(f"--- {parqueadero.name} ---\n")
        printer.text(f"--- NIT: {parqueadero.nit} ---\n")
        printer.text(f"--- TEL: {parqueadero.phone} ---\n")
        printer.text(f"{parqueadero.address}\n")
        printer.text(f"{parqueadero.city}\n")
        printer.text("------------------------\n")
        
        printer.set(align='left')
        printer.text(f"Fecha: {formatear_tiempo}\n")
        printer.text(f"Matricula: {datos.plateNumber}\n")
        printer.text(f"Tipo vehículo: {datos.vehicleType}\n")
        printer.text(f"Tipo Tarifa: {datos.rate}\n")
        printer.text(f"Precio: ${datos.rateValue:,.0f} COP\n")
        
        printer.set(align='center')
        printer.text("\n¡Gracias por su visita!\n")
        printer.text(f" Un producto {software.companyName}\n")
        printer.text(f"Nit: {software.nit}\n")
        printer.text("------------------------\n")
        printer.cut()
        logging.info("Ticket impreso correctamente.")
    except Exception as e:
        logging.error(f"Error al imprimir: {e}")

def boton_presionado():
    logging.info("Botón presionado, preparando impresión...")
    time.sleep(0.1)
    imprimir_ticket()

def iniciar_boton():
    if not GPIO_AVAILABLE or not Pulsador:
        logging.info("Botón GPIO no disponible - modo simulación")
        return
    
    Pulsador.when_pressed = boton_presionado
    while True:
        time.sleep(1)

#@app.post("/api/Entry")
@app.post("/evento")
async def recibir_evento(evento: EventoEntrada):
    global ultimo_evento
    ultimo_evento = evento
    logging.info("El evento fue recibido y almacenado con exito")
    return {"status": "ok", "mensaje": "Evento recibido correctamente"}

if __name__ == '__main__':
    if setup_printer():
        logging.info("El sistema esta listo para Imprimir")
        hilo_boton = threading.Thread(target=iniciar_boton, daemon=True)
        hilo_boton.start()
        uvicorn.run(app, host="0.0.0.0", port=8000, log_level="debug")
    else:
        logging.error("La impresora no fue detectada")
