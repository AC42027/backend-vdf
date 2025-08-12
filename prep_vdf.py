import json
from pylogix import PLC

# 1) Carga de configuración
with open("devices.json", "r") as f:
    devices = json.load(f)

def leer_dispositivo(dev):
    ip   = dev["ip"]
    slot = dev.get("slot", 0)
    tags = dev["tags"]
    resultados = {}

    print(f"Conectando a {ip} (slot {slot}) → {len(tags)} tags")
    with PLC(ip, slot=slot) as comm:
        # Lectura masiva de todos los tags
        respuestas = comm.Read(tags)
        for r in respuestas:
            if r.Status == "Success":
                resultados[r.TagName] = r.Value
            else:
                resultados[r.TagName] = None
    return resultados

def main():
    for dev in devices:
        datos = leer_dispositivo(dev)
        print("Valores recibidos:")
        for tag, val in datos.items():
            print(f"   • {tag}: {val}")
    print("Lectura completada.")

if __name__ == "__main__":
    main()
