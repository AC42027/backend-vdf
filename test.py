from pylogix import PLC

# Cambia aquí por uno de tus VDF reales
IP  = "10.107.210.111"
TAG = "VDF_CC01_Corrientes[4]"  

with PLC(IP) as comm:
    r = comm.Read(TAG)
    print("Status:", r.Status, "| Value:", r.Value)
