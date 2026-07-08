import usb_cdc, board, digitalio, time, neopixel

pins = {
    "blu":    digitalio.DigitalInOut(board.GP0),
    "giallo": digitalio.DigitalInOut(board.GP1),
    "rosso":  digitalio.DigitalInOut(board.GP2),
    "verde":  digitalio.DigitalInOut(board.GP3),
    "bianco": digitalio.DigitalInOut(board.GP4),
}

for p in pins.values():
    p.direction = digitalio.Direction.OUTPUT

# LED RGB onboard (RP2040-Zero: WS2812 su GP16). Heartbeat "board viva".
status = neopixel.NeoPixel(board.GP16, 1, brightness=0.1, auto_write=True)
HB_PERIOD = 5.0    # ogni 5s
HB_ON = 0.05       # blink breve
hb_last = time.monotonic()
hb_lit = False


def set_led(colore, stato):
    p = pins.get(colore)
    if p is not None:
        p.value = stato


def spegni_tutti():
    for p in pins.values():
        p.value = False


ser = usb_cdc.data
if ser is not None:
    ser.timeout = 0.1

spegni_tutti()
print("code.py avviato, ser =", ser)

# Protocollo (una riga per comando):
#   on <colore>   accendi un LED
#   off <colore>  spegni un LED
#   off           spegni tutti
while True:
    # heartbeat non-bloccante: blink verde tenue ogni HB_PERIOD
    now = time.monotonic()
    if not hb_lit and now - hb_last >= HB_PERIOD:
        status[0] = (0, 40, 0)
        hb_lit = True
        hb_last = now
    elif hb_lit and now - hb_last >= HB_ON:
        status[0] = (0, 0, 0)
        hb_lit = False
        hb_last = now

    if ser is None:
        time.sleep(0.1)
        continue
    line = ser.readline()
    if line:
        line = line.strip().decode("utf-8").lower()
        print("ricevuto:", line)
        parts = line.split()
        if not parts:
            pass
        elif parts[0] == "off" and len(parts) == 1:
            spegni_tutti()
        elif parts[0] == "on" and len(parts) == 2:
            set_led(parts[1], True)
        elif parts[0] == "off" and len(parts) == 2:
            set_led(parts[1], False)
    time.sleep(0.01)
