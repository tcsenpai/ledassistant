# 🔔 LED Notifiche macOS — Guida a sessioni (v2, 5 LED singoli)

**Regole del gioco:**
- Ogni sessione è autonoma: 15–30 minuti, poi puoi mollare senza perdere progressi.
- Ogni sessione finisce con **✅ VERIFICA**. Se passa, hai finito davvero.
- **🔧 Se si blocca** = guarda lì prima di improvvisare.

Setup: RP2040, 5 LED a due gambe (rosso, verde, blu, giallo, bianco), macOS M1 Max.

---

https://www.waveshare.com/wiki/RP2040-Zero

## 📦 Sessione 0 — Inventario (5 min)

- [x] RP2040 + cavo USB **dati** (non solo ricarica)
- [x] 5 LED: rosso, verde, blu, giallo, bianco
- [x] 5 resistenze 220–330Ω (una per LED, non condivise)
- [x] Dupont o saldatrice

Per ogni LED individua le gambe: **lunga = anodo (+), corta = catodo (−)**. Spesso c'è anche uno smusso sul corpo plastico dal lato del catodo, utile se le gambe sono state accorciate.

> ✅ VERIFICA: sai riconoscere anodo/catodo su ciascuno dei 5 LED.

---

## 🟢 Sessione 1 — CircuitPython + primo blink (15 min)

Nessuna saldatura, nessun LED esterno. Solo verifica che la scheda funzioni.

1. [x] `circuitpython.org/downloads`, cerca la tua scheda, scarica il `.UF2` stabile.
2. [x] Tieni **BOOTSEL**, collega USB, rilascia.
3. [x] Appare il disco **RPI-RP2**. Trascina dentro il `.UF2`.
4. [x] La scheda si riavvia, appare **CIRCUITPY**.
5. [x] Crea `code.py` nella radice:

```python
import board, digitalio, time

led = digitalio.DigitalInOut(board.LED)
led.direction = digitalio.Direction.OUTPUT

while True:
    led.value = not led.value
    time.sleep(0.5)
```

6. [x] Salva. Esecuzione automatica.

> ✅ VERIFICA: il LED integrato lampeggia ogni mezzo secondo.

**🔧 Se si blocca:**
- Non appare RPI-RP2 → cavo solo-ricarica, cambialo.
- File eseguito ma nessun effetto → controlla che si chiami `code.py` e non `code.py.txt` (Finder nasconde le estensioni).

---

## 🔌 Sessione 2 — Cablaggio dei 5 LED (20–30 min)

Schema per **ognuno** dei 5 LED, circuiti indipendenti:

```
GPIO_x → resistenza (220–330Ω) → gamba lunga (anodo)
gamba corta (catodo) → GND
```

I 5 GND si accorpano su un'unica linea GND della scheda — non serve un pin GND per LED.

Assegnazione (RP2040-Zero — stessa sintassi GPx del Pico):

| LED | Pin |
|---|---|
| Rosso | GP0 |
| Verde | GP1 |
| Blu | GP2 |
| Giallo | GP3 |
| Bianco | GP4 |

Nota: la scheda ha un LED RGB WS2812 integrato su un pin dedicato (probabilmente GP16, non verificato al 100% — controlla la serigrafia della tua scheda). GP0–GP4 sono comunque lontani da quel range e non dovrebbero avere conflitti.

- [x] Salda o cabla i 5 circuiti secondo lo schema.
- [x] Sostituisci `code.py`:

```python
import board, digitalio, time

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

while True:
    for c in pins:
        solo(c)
        time.sleep(1)
```

> ✅ VERIFICA: i 5 LED si accendono in sequenza, uno alla volta, in loop.

**🔧 Se si blocca:**
- Un LED resta spento → anodo/catodo invertiti su quel LED specifico, o resistenza/saldatura fredda. Controlla quel circuito isolatamente.
- Tutti spenti → GND comune non collegato, o pin sbagliati nel dizionario `pins` vs cablaggio reale.

Nota sulla resistenza: 220–330Ω va bene su tutti e cinque anche se il forward voltage varia per colore (rosso ~1.8–2.2V, blu/bianco ~3.0–3.4V) — a 3.3V il margine regge ovunque, non serve calcolarla per canale.

---

## 📡 Sessione 3 — Il LED ascolta il Mac (15 min)

Obiettivo: scrivi un nome-colore dal Mac, il LED corrispondente si accende (spegnendo gli altri).

1. [x] Crea `boot.py` nella radice di CIRCUITPY:

```python
import usb_cdc
usb_cdc.enable(console=True, data=True)
```

2. [x] Sostituisci `code.py`:

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
    if line == "off":
        spegni()
    elif line in pins:
        solo(line)
```

3. [x] **Scollega e ricollega l'USB** (boot.py si legge solo all'avvio).
4. [x] Terminale:

```bash
ls /dev/tty.usbmodem*
```

   Compaiono due porte. Quella giusta è la **seconda** (dati).
5. [x] Test manuale:

```bash
printf 'rosso\n' > /dev/tty.usbmodemXXXX2
printf 'off\n'   > /dev/tty.usbmodemXXXX2
```

> ✅ VERIFICA: `rosso` accende solo il LED rosso, `off` spegne tutto.

**🔧 Se si blocca:**
- Una sola porta → boot.py non caricato, nome sbagliato o USB non ricollegato.
- Nessuna reazione → stai scrivendo sulla prima porta (console), usa la seconda.

---

## 🖥 Sessione 4 — Il daemon (30 min)

Obiettivo: notifica in arrivo → LED corretto si accende da solo.

1. [x] Ambiente:

```bash
mkdir -p ~/led-daemon && cd ~/led-daemon
python3 -m venv venv
./venv/bin/pip install pyserial
```

2. [x] `~/led-daemon/daemon.py`:

```python
import sqlite3, serial, glob, time, os, sys

DB = os.path.expanduser("~/Library/Group Containers/"
    "group.com.apple.usernotificationcenter/db2/db")

COLORS = {
    "com.tinyspeck.slackmacgap": "blu",
    "com.apple.MobileSMS":       "verde",
    "com.apple.mail":            "giallo",
}
DEFAULT = "bianco"

def get_port():
    while True:
        ports = sorted(glob.glob("/dev/tty.usbmodem*"))
        if ports:
            try:
                return serial.Serial(ports[-1], 115200, timeout=1)
            except serial.SerialException:
                pass
        time.sleep(5)

port = get_port()
last = 0

while True:
    try:
        con = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
        row = con.execute(
            "SELECT a.identifier, r.delivered_date FROM record r "
            "JOIN app a ON r.app_id = a.app_id "
            "ORDER BY r.delivered_date DESC LIMIT 1").fetchone()
        con.close()
        if row and row[1] and row[1] > last:
            last = row[1]
            colore = COLORS.get(row[0], DEFAULT)
            try:
                port.write((colore + "\n").encode())
            except serial.SerialException:
                port = get_port()
    except sqlite3.OperationalError as e:
        print(f"DB error (Full Disk Access?): {e}", file=sys.stderr)
        time.sleep(30)
    time.sleep(2)
```

3. [x] **Full Disk Access** sul binario python del venv (senza questo il DB non si apre):
   - Impostazioni di Sistema → Privacy e Sicurezza → Accesso completo al disco
   - Trova il percorso reale:

```bash
readlink -f ~/led-daemon/venv/bin/python3
```

   - `+` → Cmd+Shift+G → incolla quel percorso → aggiungi. Attiva l'interruttore.
   - Aggiungi anche il Terminale, per i test manuali.

4. [x] Test:

```bash
~/led-daemon/venv/bin/python3 ~/led-daemon/daemon.py
```

5. [ ] Genera una notifica qualsiasi.

> ✅ VERIFICA: notifica in arrivo → LED corretto (o bianco di default) si accende. Ctrl+C per fermare.

**🔧 Se si blocca:**
- `unable to open database file` → Full Disk Access non attivo sul binario giusto (da qui il `readlink -f`).
- Nessuna reazione ma nessun errore → l'identifier dell'app non è mappato in `COLORS` e dovrebbe scattare `DEFAULT`; se non scatta nemmeno quello, aggiungi `print(row)` dopo il `fetchone()` per vedere cosa arriva davvero.

---

## 🚀 Sessione 5 — Autostart (10 min)

1. [ ] `~/Library/LaunchAgents/sh.tcsenpai.leddaemon.plist`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
 "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>sh.tcsenpai.leddaemon</string>
    <key>ProgramArguments</key>
    <array>
        <string>/Users/TUOUTENTE/led-daemon/venv/bin/python3</string>
        <string>/Users/TUOUTENTE/led-daemon/daemon.py</string>
    </array>
    <key>KeepAlive</key>
    <true/>
    <key>StandardErrorPath</key>
    <string>/tmp/leddaemon.err</string>
</dict>
</plist>
```

2. [ ] Sostituisci **TUOUTENTE** (due volte) con l'output di `whoami`.
3. [ ] Carica:

```bash
launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/sh.tcsenpai.leddaemon.plist
```

> ✅ VERIFICA: notifica senza terminale aperto → LED reagisce comunque.

**🔧 Se si blocca:**
- `cat /tmp/leddaemon.err` per la diagnosi. Se è il DB → Full Disk Access sul binario python.
- Stop/reload: `launchctl bootout gui/$(id -u)/sh.tcsenpai.leddaemon`

---

## ⚠️ Fragilità nota

Lo schema del DB `db2` delle notifiche non è API pubblica. Un major update di macOS può romperlo — se dopo un aggiornamento il LED smette di reagire e `/tmp/leddaemon.err` mostra errori SQL, la causa è quella.

