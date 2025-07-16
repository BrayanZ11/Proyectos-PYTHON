'''
import requests

url = 'https://api.agify.io/?name=michael'  # Esta API predice la edad según el nombre

response = requests.get(url)

if response.status_code == 200:
    data = response.json()
    print("Respuesta de la API:", data)
else:
    print("Error al consumir la API:", response.status_code)
'''    
    
  # [] 
import requests

pokemon= input("cual es el nombre del pokemon: ").strip().lower()
# URL base con parámetros
url= "https://pokeapi.co/api/v2/pokemon/charmander"

# Hacer solicitud GET
response = requests.get(url)

# Procesar respuesta
if response.status_code == 200:
    data = response.json()
    
    nombre = data["name"]
    id_pokemon = data["id"]
    altura=data["height"]
    peso=data["weight"]
    
    habilidades=[habilidad["ability"]["name"] for habilidad in data["abilities"]]
   
    tipo_pokemon=[tipo["type"]["name"] for tipo in data["types"]]
    
    estadisticas={stat["stat"]["name"]: stat["base_stat"] for stat in data["stats"]}
    
    print(f"Información de {nombre.capitalize()}:")
    print(f"ID: {id_pokemon}")
    print(f"Altura: {altura}")
    print(f"Peso: {peso}")
    print(f"Habilidades: {', '.join(habilidades)}")
    print(f"Tipos: {','.join(tipo_pokemon)}")
    print("Estadísticas:")
    for nombre_stat, valor in estadisticas.items():
        print(f"  {nombre_stat.capitalize()}: {valor}")
    
else:
    print("Error al consultar el pokemon:", response.status_code)


