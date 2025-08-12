from pylogix import PLC

# Configuración de cada PLC
plcs = [
    {
        "ip": "10.107.210.111",
        "nombre": "CC01",
        "tag_corriente": "VDF_CC01_Corrientes",
        "tag_temp": "VDF_CC01_Temp",
        "elementos": 16
    },
    {
        "ip": "10.107.210.121",
        "nombre": "CC02",
        "tag_corriente": "VDF_CC02_Corrientes",
        "tag_temp": "VDF_CC02_Temp",
        "elementos": 20
    },
    {
        "ip": "10.107.210.131",
        "nombre": "CC03",
        "tag_corriente": "VDF_CC03_Corrientes",
        "tag_temp": "VDF_CC03_Temp",
        "elementos": 16
    }
]

def leer_array(comm, base_tag, cantidad):
    datos = {}
    for i in range(cantidad):
        tag = f"{base_tag}[{i}]"
        r = comm.Read(tag)
        datos[tag] = r.Value if r.Status == 'Success' else None
    return datos

def main():
    for plc in plcs:
        print(f"\n🔌 Conectando a PLC {plc['nombre']} en {plc['ip']} ...")
        with PLC(plc["ip"]) as comm:
            print(f"✅ Conectado a {plc['nombre']}")

            print("📈 Corrientes:")
            corrientes = leer_array(comm, plc["tag_corriente"], plc["elementos"])
            for tag, val in corrientes.items():
                print(f"   {tag} → {val} A")

            print("\n🌡️ Temperaturas:")
            temperaturas = leer_array(comm, plc["tag_temp"], plc["elementos"])
            for tag, val in temperaturas.items():
                print(f"   {tag} → {val} °C")

if __name__ == "__main__":
    main()
