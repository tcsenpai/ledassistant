# Debug handoff — LED notifiche RP2040-Zero, canale seriale muto

## Ambiente

- Board: Waveshare RP2040-Zero
- Firmware: Adafruit CircuitPython 10.2.1 (2026-05-13)
- Host: macOS M1 Max
- Porte USB rilevate: `/dev/cu.usbmodem21201` (console/REPL, confermata funzionante — risponde a input Python) e `/dev/cu.usbmodem21203` (canale dati)

## Sintomo

Scrivendo sul canale dati (`21203`) non succede assolutamente nulla: nessun errore lato Mac, nessuna reazione sui LED, nessun output sulla console (`21201`) anche con un `print()` di debug aggiunto nel loop di lettura.

## File attuali sulla scheda

`boot.py`:
```python
import usb_cdc
usb_cdc.enable(console=True, data=True)
```

`code.py` (versione con debug):
```python
import usb_cdc, board, digitalio

pins = {
    "rosso":  digitalio.DigitalInOut(board.GP0),
    "verde":  digitalio.DigitalInOut(board.GP1),
    "blu":    digitalio.DigitalInOut(board.GP2),
    "giallo": digitalio.DigitalInOut(board.GP3),
    "bianco": digitalio.DigitalInOut(board.GP4),
}
for p in pins.values():
    p.direction = digitalio.Direction.OUTPUT

def solo(colore):
    for nome, p in pins.items():
        p.value = (nome == colore)

def spegni():
    for p in pins.values():
        p.value = False

ser = usb_cdc.data

while True:
    line = ser.readline().strip().decode(errors="ignore").lower()
    if line:
        print("ricevuto:", line)
    if line == "off":
        spegni()
    elif line in pins:
        solo(line)
```

## Sequenza di test eseguita

1. `tio /dev/cu.usbmodem21201` → conferma console attiva, REPL raggiungibile, versione CircuitPython visibile.
2. `tio /dev/cu.usbmodem21203` → nessuna risposta all'invio (atteso, è il canale dati).
3. `printf 'rosso\n' > /dev/cu.usbmodem21203` con `tio` aperto in parallelo su `21201` → **nessun output** "ricevuto: rosso" atteso sulla console. Silenzio totale.

## Cablaggio hardware (non ancora escluso come causa, ma sintomo è sul canale seriale non sui LED)

5 LED singoli (rosso/verde/blu/giallo/bianco), ciascuno: `GPIO_x → resistenza 220–330Ω → anodo (gamba lunga)`, catodo comune → GND. Pin: GP0–GP4.

## Ipotesi da verificare, in ordine di probabilità

1. **`ser.readline()` con timeout di default che non si comporta come atteso.** In CircuitPython, `usb_cdc.data` ha un attributo `timeout` — verificare il default in 10.2.1 e se `readline()` blocca indefinitamente (nel qual caso il loop non arriva mai al `print` successivo perché è fermo lì, e i print successivi non escono mai) invece di ritornare `b''` a ogni giro. Test: aggiungere `print("loop tick")` **prima** della riga `ser.readline()`, fuori da qualunque condizione, per vedere se il loop gira affatto o è bloccato dentro la `readline()`.
2. **`code.py` non è la versione in esecuzione.** Verificare aprendo la console: al salvataggio del file CircuitPython dovrebbe stampare un messaggio di soft-reboot. Se quel messaggio non compare quando si salva, la scheda potrebbe non star ricaricando il file (permessi di scrittura sul volume CIRCUITPY, o editor che scrive su un file temporaneo senza sincronizzare).
3. **Line ending mismatch.** `printf 'rosso\n'` manda `\n` (0x0A). Verificare se `readline()` di `usb_cdc.data` si aspetta `\r\n` per considerare la riga completa — in tal caso la riga resta bufferizzata in attesa del terminatore e non viene mai restituita. Test: `printf 'rosso\r\n' > /dev/cu.usbmodem21203`.
4. **Buffer USB CDC non flush-ato dal lato host.** Con redirezione shell (`> device`), il file descriptor viene chiuso subito dopo la write — possibile che il buffer USB non venga inviato in tempo utile prima della chiusura. Test alternativo con Python esplicito:
   ```python
   import serial, time
   s = serial.Serial('/dev/cu.usbmodem21203', 115200, timeout=1)
   s.write(b'rosso\n')
   s.flush()
   time.sleep(0.5)
   s.close()
   ```
5. **Ordine/enable dei due canali USB CDC in `boot.py` non effettivo dopo modifiche successive.** Confermare che l'USB sia stato scollegato e ricollegato fisicamente **dopo l'ultima modifica** a `boot.py` (non solo la prima volta) — CircuitPython legge `boot.py` solo all'avvio, non al salvataggio.

## Obiettivo per l'agente

Isolare in quale dei 5 punti sopra si trova il problema, partendo dal punto 1 (aggiungere `print("loop tick")` grezzo prima di `readline()` è il test più economico e diagnostico) e dal punto 3 (line ending), prima di considerare cause hardware.
