import os
import time
import subprocess
import pygame
import platform

# Configuración
MEDIA_DIR = "C:/Users/RRAIGOSA/Pictures/BRAYAN"  # Cambia a tu ruta local
PRINCIPAL = "C:/Users/RRAIGOSA/Downloads/Mensaje inicial.png"
DISPLAY_TIME = 6  # segundos

# Resolución de ventana (simula pantalla LCD)
LCD_WIDTH = 480
LCD_HEIGHT = 320

# Extensiones
IMAGE_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.bmp']
VIDEO_EXTENSIONS = ['.mp4', '.mov', '.avi', '.mkv']

# Inicializar pygame
pygame.init()
screen = pygame.display.set_mode((LCD_WIDTH, LCD_HEIGHT))
pygame.display.set_caption("Visor Multimedia")

def show_image(path):
    try:
        image = pygame.image.load(path)
        image = pygame.transform.scale(image, (LCD_WIDTH, LCD_HEIGHT))
        screen.blit(image, (0, 0))
        pygame.display.flip()
    except Exception as e:
        print(f"Error mostrando imagen: {path} -> {e}")

def play_video(path):
    # En Windows usamos ffplay si está disponible
    if platform.system() == "Windows":
        subprocess.run(['ffplay', '-autoexit', '-noborder', '-loglevel', 'quiet', path])
    else:
        print(f"Video omitido en este entorno: {path}")

def main():
    all_files = sorted(os.listdir(MEDIA_DIR))
    principal_path = os.path.join(MEDIA_DIR, PRINCIPAL)

    media_files = [
        os.path.join(MEDIA_DIR, f) for f in all_files
        if f != PRINCIPAL
        and os.path.splitext(f)[1].lower() in IMAGE_EXTENSIONS + VIDEO_EXTENSIONS
    ]

    while True:
        # Mostrar imagen principal
        if os.path.exists(principal_path):
            show_image(principal_path)
            time.sleep(DISPLAY_TIME)

        # Mostrar el resto de archivos
        for media in media_files:
            ext = os.path.splitext(media)[1].lower()
            if ext in IMAGE_EXTENSIONS:
                show_image(media)
                time.sleep(DISPLAY_TIME)
            elif ext in VIDEO_EXTENSIONS:
                play_video(media)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pygame.quit()
