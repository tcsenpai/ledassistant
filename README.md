# lednotify

Physical LED notifications for macOS. A daemon reads the macOS notification database, matches apps to colors, and drives LEDs on an RP2040 board over USB serial.

## How it works

1. `daemon.py` polls the macOS user notification database (`usernoted` SQLite DB).
2. When a notification appears for a mapped app, it sends `on <color>` over serial.
3. When the notification clears, it sends `off <color>`.
4. The CircuitPython firmware on the board receives the command and toggles the corresponding GPIO pin.

The daemon reconnects automatically if the USB link drops. The board runs a heartbeat blink on the onboard NeoPixel to confirm it is alive.

## Hardware

- RP2040-Zero (or any RP2040 board with CircuitPython support)
- 5 LEDs on GP0 through GP4 (blue, yellow, red, green, white)
- Current-limiting resistors on each LED

## Schema

<img width="1920" height="1080" alt="schema" src="https://github.com/user-attachments/assets/c542f42c-3840-485c-8dd2-d7ccbb19d21a" />


## Default app mappings

| App | Color |
|-----|-------|
| Telegram | Blue |
| WhatsApp | Green |
| Discord | Yellow |
| Slack | Red |
| Proton Mail | White |

Edit the `COLORS` dict in `daemon.py` to change them. The key is the macOS bundle identifier.

## Setup

1. Flash CircuitPython onto the RP2040.
2. Copy `circuitpy/boot.py`, `circuitpy/code.py`, and `circuitpy/lib/neopixel.mpy` to the board.
3. Wire LEDs to GP0-GP4 with resistors.
4. Install pyserial: `pip install pyserial`
5. Grant Full Disk Access to your terminal/Python in System Settings (the notification DB is protected).
6. Run: `python3 daemon.py`

## Testing

`test_leds.py` cycles through all LEDs one by one, then lights them all at once. Close the daemon first since it holds the serial port.

```
python3 test_leds.py
```

## Serial protocol

One command per line, plain text:

```
on <color>    # turn on one LED
off <color>   # turn off one LED
off           # turn off all LEDs
```

## License

MIT
