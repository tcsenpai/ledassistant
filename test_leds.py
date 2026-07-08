"""Test hardware: cicla i 5 LED usando lo stesso protocollo del daemon.
Uso: python3 test_leds.py   (chiudere il daemon prima, tiene la porta)
"""
import serial, glob, time, sys

COLORI = ["blu", "giallo", "rosso", "verde", "bianco"]


def get_port():
    ports = sorted(glob.glob("/dev/tty.usbmodem*"))
    if not ports:
        sys.exit("nessuna porta usbmodem trovata")
    return serial.Serial(ports[-1], 115200, timeout=1)


def send(port, cmd):
    port.write((cmd + "\n").encode())
    print(f"-> {cmd}")


port = get_port()
send(port, "off")            # parti pulito
time.sleep(0.5)

try:
    # 1. uno alla volta
    for c in COLORI:
        send(port, "on " + c)
        time.sleep(0.6)
        send(port, "off " + c)
        time.sleep(0.2)

    # 2. tutti accesi insieme, poi spegni
    for c in COLORI:
        send(port, "on " + c)
        time.sleep(0.2)
    time.sleep(1)
    send(port, "off")
    print("test completato")
finally:
    port.close()
