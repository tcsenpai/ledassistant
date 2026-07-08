import sqlite3, serial, glob, time, os, sys

DB = os.path.expanduser("~/Library/Group Containers/"
    "group.com.apple.usernoted/db2/db")

# app identifier -> colore LED. Non mappate = ignorate (LED restano spenti).
COLORS = {
    "com.tdesktop.telegram":  "blu",
    "net.whatsapp.whatsapp":  "verde",
    "com.hnc.discord":        "giallo",
    "com.tinyspeck.slackmacgap": "rosso",
    "ch.protonmail.desktop":  "bianco",
}


def get_port():
    while True:
        ports = sorted(glob.glob("/dev/tty.usbmodem*"))
        if ports:
            try:
                return serial.Serial(ports[-1], 115200, timeout=1)
            except serial.SerialException:
                pass
        time.sleep(5)


class Reconnect(Exception):
    """Segnala port perso: forza riconnessione + risync stato."""


def send(port, cmd):
    try:
        port.write((cmd + "\n").encode())
        print(f"-> {cmd}", file=sys.stderr)
    except (serial.SerialException, OSError):
        raise Reconnect


port = get_port()
active = set()  # identifier mappati con LED acceso (secondo il daemon)

while True:
    try:
        # Apertura read-write + checkpoint: usernoted tiene le notif fresche nel
        # WAL e non le committa finche' non apri il Centro Notifiche. Il checkpoint
        # PASSIVE forza la materializzazione cosi' le vediamo in tempo reale.
        con = sqlite3.connect(DB, timeout=1)
        try:
            con.execute("PRAGMA wal_checkpoint(PASSIVE)")
        except sqlite3.OperationalError:
            pass
        rows = con.execute(
            "SELECT DISTINCT a.identifier FROM record r "
            "JOIN app a ON r.app_id = a.app_id").fetchall()
        con.close()

        present = {r[0] for r in rows if r[0] in COLORS}

        for ident in present - active:      # nuova notif per app mappata
            print(f"[on ] {ident} -> {COLORS[ident]}", file=sys.stderr)
            send(port, "on " + COLORS[ident])
        for ident in active - present:      # notif letta per app mappata
            print(f"[off] {ident} -> {COLORS[ident]}", file=sys.stderr)
            send(port, "off " + COLORS[ident])
        active = present

    except sqlite3.OperationalError as e:
        print(f"DB error (Full Disk Access?): {e}", file=sys.stderr)
        time.sleep(30)
    except Reconnect:
        print("port perso, riconnetto...", file=sys.stderr)
        port = get_port()
        active = set()  # board ripartita spenta: ricostruisci diff al prossimo giro
    time.sleep(1)
