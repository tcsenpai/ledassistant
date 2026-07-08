# 🔔 macOS Notification LEDs — Build Guide (v3, 5 discrete LEDs)

Turn a Waveshare RP2040-Zero into a physical notification indicator for macOS:
when a mapped app gets a notification, its dedicated LED turns on; when you
read the notification, the LED turns off.

> This guide is the **corrected** English version of `ORIGINAL_GUIDE.md`.
> Where the two disagree, **this repo is the source of truth** — the guide was
> written before the firmware and daemon were finalized, so several details
> (pin mapping, serial protocol, database path, DB access strategy, app
> mapping) changed. Divergences are flagged inline with **⚠️ Changed from the
> original guide**.

**Hardware used here:**
- Waveshare RP2040-Zero ([wiki](https://www.waveshare.com/wiki/RP2040-Zero))
- CircuitPython 10.2.1 (`waveshare_rp2040_zero`)
- 5 discrete LEDs: red, green, blue, yellow, white
- 5 resistors 220–330 Ω (one per LED, not shared)
- macOS (developed on an M1 Max)

**Session rules:**
- Each session is self-contained: 15–30 min, then you can stop without losing progress.
- Each session ends with **✅ CHECK**. If it passes, you are actually done.
- **🔧 If stuck** = read that block before improvising.

---

## 📦 Session 0 — Inventory (5 min)

- [ ] RP2040-Zero + **data** USB cable (not charge-only)
- [ ] 5 LEDs: red, green, blue, yellow, white
- [ ] 5 resistors 220–330 Ω (one per LED, not shared)
- [ ] Dupont wires or a soldering iron

For each LED identify the legs: **long = anode (+), short = cathode (−)**. There
is usually also a flat spot on the plastic body on the cathode side, useful if
the legs were trimmed.

> ✅ CHECK: you can tell anode from cathode on all 5 LEDs.

---

## 🟢 Session 1 — CircuitPython + first blink (15 min)

No soldering, no external LED yet. Just confirm the board works.

1. [ ] Go to `circuitpython.org/downloads`, search for **Waveshare RP2040-Zero**, download the stable `.UF2`.
2. [ ] Hold **BOOTSEL**, plug in USB, release.
3. [ ] The **RPI-RP2** disk appears. Drag the `.UF2` onto it.
4. [ ] The board reboots and **CIRCUITPY** appears.
5. [ ] Create `code.py` at the root:

```python
import board, digitalio, time

led = digitalio.DigitalInOut(board.LED)
led.direction = digitalio.Direction.OUTPUT

while True:
    led.value = not led.value
    time.sleep(0.5)
```

6. [ ] Save. It runs automatically.

> ✅ CHECK: the onboard LED blinks every half second.

> ℹ️ Note: on the RP2040-Zero, `board.LED` drives the onboard **WS2812 RGB**
> LED (on GP16), not a plain single-color LED. The blink still verifies the
> board runs code. The final firmware uses this RGB LED as a heartbeat — see
> Session 3.

**🔧 If stuck:**
- No RPI-RP2 disk → charge-only cable, replace it.
- File runs but nothing happens → check it is called `code.py` and not `code.py.txt` (Finder hides extensions).

---

## 🔌 Session 2 — Wiring the 5 LEDs (20–30 min)

Circuit for **each** of the 5 LEDs, independent:

```
GPIO_x → resistor (220–330 Ω) → long leg (anode)
short leg (cathode) → GND
```

The 5 cathodes join a single GND rail on the board — you do not need one GND pin per LED.

**⚠️ Changed from the original guide — pin assignment.** The original guide
mapped colors to pins `red=GP0, green=GP1, blue=GP2, yellow=GP3, white=GP4`.
The firmware actually flashed to the board uses a **different** mapping:

| LED    | Pin |
|--------|-----|
| Blue   | GP0 |
| Yellow | GP1 |
| Red    | GP2 |
| Green  | GP3 |
| White  | GP4 |

The color↔pin mapping is a wiring convention, not a hardware constraint — but
it **must match `code.py`**. If you wire by physical pin instead of by color,
either rewire to the table above or edit the `pins` dict in `code.py`
(`circuitpy/code.py`) to match how you soldered.

> ℹ️ The onboard WS2812 RGB LED is on **GP16** (confirmed on this board:
> `board_id = waveshare_rp2040_zero`). GP0–GP4 are clear of it, no conflict.

### Wiring diagram

GP0–GP4 sit on the **top-right** of the board; the shared GND is the pin below
5V on the **top-left**. Each LED is an independent branch off the common GND rail.

![LED wiring diagram](docs/wiring-excalidraw.png)

<sub>Sources in `docs/`: `wiring.excalidraw` (+ `wiring-excalidraw.svg`/`.png`) and
`wiring.mmd` (+ `wiring-mermaid.png`). Regenerate the Mermaid PNG with
`npx -y @mermaid-js/mermaid-cli -i docs/wiring.mmd -o docs/wiring-mermaid.png -b white -s 3`.</sub>

<details>
<summary>ASCII fallback (renders anywhere)</summary>

```
 RP2040-Zero (USB-C at top, pins as silkscreened)

        left header                 right header
     ┌───────────────┐          ┌───────────────────┐
 5V ─┤ 5V            │          │            GP0 ├──┐  ← Blue
GND ─┤ GND ●         │          │            GP1 ├─┐│  ← Yellow
3V3 ─┤ 3V3           │          │            GP2 ├┐││  ← Red
     │  … GP29…GP26  │          │            GP3 ├─┘││  (GP3 → Green)
     │  GP15  GP14   │          │            GP4 ├──┘│  (GP4 → White)
     └───────┬───────┘          └───────────────────┘
             │ GND ●
             │
   ┌─────────┴──────────────────────────────────┐   common GND rail
   │        │        │        │        │         │
  cath.    cath.    cath.    cath.    cath.       │
  (−)      (−)      (−)      (−)      (−)          │
 ┌─┴─┐    ┌─┴─┐    ┌─┴─┐    ┌─┴─┐    ┌─┴─┐         │
 │LED│    │LED│    │LED│    │LED│    │LED│         │
 │blu│    │gia│    │ros│    │ver│    │bia│         │
 └─┬─┘    └─┬─┘    └─┬─┘    └─┬─┘    └─┬─┘         │
  (+)      (+)      (+)      (+)      (+)          │
 anode    anode    anode    anode    anode        │
   │        │        │        │        │          │
 [220Ω]  [220Ω]  [220Ω]  [220Ω]  [220Ω]           │
   │        │        │        │        │          │
  GP0      GP1      GP2      GP3      GP4          │
 (Blue)  (Yellow)  (Red)   (Green)  (White)       │
```
</details>

Per-LED, the current path is:

```
GPn ──[220–330 Ω]──►|── LED ──► GND
              (resistor)  (anode → cathode)
```

- **Anode (+, long leg)** → resistor → **GPn** (the GPIO drives it HIGH to light).
- **Cathode (−, short leg)** → **common GND rail** → board **GND** pin.
- One resistor **per LED** (not shared), in series with either leg (anode side shown).

> ℹ️ The board has **two** GND pins (top-left, plus one on the bottom header) —
> either works. Tie all 5 cathodes to the same rail and run one wire to a single
> GND pin.

- [ ] Solder or wire the 5 circuits per the schematic.
- [ ] Flash the real firmware. The working `code.py` lives at `circuitpy/code.py`
  in this repo — copy it to the board's `CIRCUITPY` root. It also needs the
  `neopixel` library:
  - Copy `circuitpy/lib/neopixel.mpy` to `CIRCUITPY/lib/neopixel.mpy` (create
    `lib/` if missing). Get it from the
    [CircuitPython library bundle](https://circuitpython.org/libraries) matching
    your firmware major version (10.x here) if you don't have it.

The final `code.py` (abridged — full file is `circuitpy/code.py`):

```python
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
```

> ℹ️ Color names in the firmware and daemon are **Italian**
> (`blu`, `giallo`, `rosso`, `verde`, `bianco`). The serial protocol uses those
> exact strings, so keep them consistent across `code.py` and `daemon.py`.

To sanity-check wiring before wiring in the Mac, temporarily add a color-cycle
loop, or just use `test_leds.py` from the host later (Session 3).

> ✅ CHECK: each of the 5 LEDs lights when its channel is driven high; a dead
> LED points at that one circuit.

**🔧 If stuck:**
- One LED stays off → anode/cathode swapped on that LED, or a cold solder joint / wrong resistor. Test that circuit in isolation.
- All off → common GND not connected, or the `pins` dict doesn't match your actual wiring.

Resistor note: 220–330 Ω is fine on all five even though forward voltage varies
by color (red ~1.8–2.2 V, blue/white ~3.0–3.4 V) — at 3.3 V the margin holds
everywhere, no per-channel calculation needed.

---

## 📡 Session 3 — The board listens to the Mac (15 min)

Goal: send a command over USB serial, the matching LED turns on/off.

1. [ ] Create `boot.py` at the CIRCUITPY root (already in `circuitpy/boot.py`):

```python
import usb_cdc
usb_cdc.enable(console=True, data=True)
```

This exposes **two** USB CDC serial ports: a console (REPL) and a data channel.

2. [ ] Make sure `code.py` (from Session 2) is on the board.

**⚠️ Changed from the original guide — serial protocol.** The original guide
used bare color names (`printf 'rosso\n'`) and a single "one LED on, rest off"
behavior. The real firmware uses an explicit, per-LED command protocol so
multiple LEDs can be on at once (one per unread app):

```
on <color>     # turn one LED on   e.g. "on rosso"
off <color>    # turn one LED off  e.g. "off rosso"
off            # turn ALL LEDs off
```

The firmware also runs a non-blocking **heartbeat**: the onboard WS2812 blinks a
dim green flash every 5 s so you can see the board is alive. And it sets
`usb_cdc.data.timeout = 0.1` so `readline()` never blocks the loop (this was the
root cause of the "serial channel is mute" bug documented in `STATUS.md`).

3. [ ] **Unplug and replug USB** — `boot.py` is read only at power-on, not on save.
4. [ ] Find the ports:

```bash
ls /dev/tty.usbmodem*
```

Two ports appear. The **data** channel is typically the higher-numbered one
(e.g. `...21203` vs the console `...21201`). If unsure, the daemon and
`test_leds.py` both auto-pick the last (`sorted(...)[-1]`) — see below.

5. [ ] Manual test (close the daemon first if it's running — it holds the port):

```bash
printf 'on rosso\n'  > /dev/tty.usbmodemXXXX   # data port
printf 'off rosso\n' > /dev/tty.usbmodemXXXX
printf 'off\n'       > /dev/tty.usbmodemXXXX
```

Or use the included host tester, which cycles all 5 LEDs using the same
protocol (`test_leds.py`):

```bash
python3 test_leds.py
```

> ✅ CHECK: `on rosso` lights only the red LED, `off rosso` turns it off, `off` clears everything.

**🔧 If stuck:**
- Only one port → `boot.py` not loaded (wrong name, or USB not physically replugged after editing it).
- No reaction → you're writing to the console port; use the data port. Or the board didn't reload `code.py` (check the console for the soft-reboot message on save).
- Buffer not flushed with shell redirection → use explicit pyserial with `.flush()`:
  ```python
  import serial, time
  s = serial.Serial('/dev/tty.usbmodemXXXX', 115200, timeout=1)
  s.write(b'on rosso\n'); s.flush(); time.sleep(0.5); s.close()
  ```

---

## 🖥 Session 4 — The daemon (30 min)

Goal: a notification arrives → the right LED turns on by itself; you read it →
the LED turns off.

1. [ ] Environment:

```bash
mkdir -p ~/led-daemon && cd ~/led-daemon
python3 -m venv venv
./venv/bin/pip install pyserial
```

2. [ ] Use `daemon.py` from this repo. The key facts:

**⚠️ Changed from the original guide — notification database.** The original
guide read `~/Library/Group Containers/group.com.apple.usernotificationcenter/db2/db`.
The correct container on modern macOS is **`group.com.apple.usernoted`**:

```python
DB = os.path.expanduser("~/Library/Group Containers/"
    "group.com.apple.usernoted/db2/db")
```

**⚠️ Changed from the original guide — DB access strategy.** The original opened
the DB read-only (`?mode=ro`). That misses fresh notifications: `usernoted`
keeps new rows in the **WAL** and doesn't commit them to the main DB until you
open Notification Center. The daemon instead opens read-write and forces a
passive checkpoint so it sees notifications in real time:

```python
con = sqlite3.connect(DB, timeout=1)
con.execute("PRAGMA wal_checkpoint(PASSIVE)")   # materialize fresh WAL rows
```

**⚠️ Changed from the original guide — behavior & app mapping.** The original
polled the single most-recent row and lit one LED (with a `DEFAULT` white for
unmapped apps). The real daemon instead diffs the **set of apps that currently
have notifications** against what's already lit, so each mapped app drives its
own LED independently, and unmapped apps are simply ignored (no default):

```python
COLORS = {
    "com.tdesktop.telegram":     "blu",
    "net.whatsapp.whatsapp":     "verde",
    "com.hnc.discord":           "giallo",
    "com.tinyspeck.slackmacgap": "rosso",
    "ch.protonmail.desktop":     "bianco",
}
```

Adjust the bundle IDs / colors to your apps. To discover an app's identifier,
add a `print(rows)` after the query and trigger a notification.

The daemon queries the distinct set of apps with notification records, computes
`present - active` (new → send `on <color>`) and `active - present` (cleared →
send `off <color>`), and reconnects the serial port if it drops.

3. [ ] **Full Disk Access** for the venv's python binary (without it the DB won't open):
   - System Settings → Privacy & Security → Full Disk Access
   - Find the real path (resolve symlinks):

```bash
readlink -f ~/led-daemon/venv/bin/python3
```

   - `+` → Cmd+Shift+G → paste that path → add. Toggle it on.
   - Add **Terminal** too, for manual tests.

4. [ ] Run it:

```bash
~/led-daemon/venv/bin/python3 ~/led-daemon/daemon.py
```

5. [ ] Trigger a notification from a mapped app.

> ✅ CHECK: notification arrives → the right LED turns on; you read it → the LED turns off. Ctrl+C to stop.

**🔧 If stuck:**
- `unable to open database file` → Full Disk Access not enabled on the right binary (that's why `readlink -f`).
- No reaction, no error → the app's identifier isn't in `COLORS` (unmapped apps are ignored). Add `print(rows)` after the query to see the real identifiers.
- Notifications only show up when you open Notification Center → the WAL checkpoint isn't running; confirm you're opening the DB read-write, not `mode=ro`.

---

## 🚀 Session 5 — Autostart (10 min)

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
        <string>/Users/YOURUSER/led-daemon/venv/bin/python3</string>
        <string>/Users/YOURUSER/led-daemon/daemon.py</string>
    </array>
    <key>KeepAlive</key>
    <true/>
    <key>StandardErrorPath</key>
    <string>/tmp/leddaemon.err</string>
</dict>
</plist>
```

2. [ ] Replace **YOURUSER** (twice) with the output of `whoami`.
3. [ ] Load it:

```bash
launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/sh.tcsenpai.leddaemon.plist
```

> ✅ CHECK: a notification with no terminal open still drives the LEDs.

**🔧 If stuck:**
- `cat /tmp/leddaemon.err` for diagnosis. If it's the DB → Full Disk Access on the python binary.
- Stop/reload: `launchctl bootout gui/$(id -u)/sh.tcsenpai.leddaemon`

---

## ⚠️ Known fragility

The `usernoted` `db2` notification schema is not a public API. A major macOS
update can break it — if after an update the LEDs stop reacting and
`/tmp/leddaemon.err` shows SQL errors, that's the cause.

---

## 📁 Repo layout

- `circuitpy/` — exact snapshot of the board's `CIRCUITPY` drive (`boot.py`, `code.py`, `lib/neopixel.mpy`, `settings.toml`, `sd/`). Copy these to the board.
- `docs/` — wiring diagram sources + exports: `wiring.excalidraw` (Excalidraw source) → `wiring-excalidraw.svg`/`.png`; `wiring.mmd` (Mermaid source) → `wiring-mermaid.png`.
- `daemon.py` — the macOS host daemon (reads the notification DB, drives the LEDs over serial).
- `test_leds.py` — host-side hardware tester; cycles all 5 LEDs using the serial protocol.
- `ORIGINAL_GUIDE.md` — the original Italian guide (kept for reference; superseded by this file where they diverge).
- `STATUS.md` — a historical debug handoff for the "mute serial channel" bug (now fixed via `usb_cdc.data.timeout`). Historical only.
