"""
F1 Manager — extract_track_coords.py
Extrai coordenadas reais do traçado via FastF1.
"""

import sqlite3
import os
import json
import math
import fastf1
import numpy as np

DB_PATH = os.path.join(os.path.dirname(__file__), "database", "f1_manager.db")
fastf1.Cache.enable_cache("fastf1_cache")

CIRCUITOS = {
    "Melbourne Grand Prix Circuit":        ("Melbourne",    2025),
    "Shanghai International Circuit":      ("Shanghai",     2025),
    "Suzuka International Racing Course":  ("Suzuka",       2025),
    "Bahrain International Circuit":       ("Bahrain",      2025),
    "Jeddah Corniche Circuit":             ("Jeddah",       2025),
    "Miami International Autodrome":       ("Miami",        2025),
    "Circuit Gilles Villeneuve":           ("Montreal",     2025),
    "Circuit de Monaco":                   ("Monaco",       2025),
    "Circuit de Barcelona-Catalunya":      ("Barcelona",    2025),
    "Red Bull Ring":                       ("Spielberg",    2025),
    "Silverstone Circuit":                 ("Silverstone",  2025),
    "Circuit de Spa-Francorchamps":        ("Spa",          2025),
    "Hungaroring":                         ("Budapest",     2025),
    "Circuit Park Zandvoort":              ("Zandvoort",    2025),
    "Autodromo Nazionale Monza":           ("Monza",        2025),
    "Baku City Circuit":                   ("Baku",         2025),
    "Marina Bay Street Circuit":           ("Singapore",    2025),
    "Circuit of the Americas":             ("Austin",       2025),
    "Autodromo Hermanos Rodriguez":        ("Mexico City",  2025),
    "Autodromo Jose Carlos Pace":          ("Sao Paulo",    2025),
    "Las Vegas Street Circuit":            ("Las Vegas",    2024),
    "Lusail International Circuit":        ("Lusail",       2025),
    "Yas Marina Circuit":                  ("Abu Dhabi",    2025),
    "Circuito de Madrid":                  None,
}


def criar_tabela(cursor):
    cursor.executescript("""
        CREATE TABLE IF NOT EXISTS circuit_coords (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            circuit_id  INTEGER REFERENCES circuits(id) UNIQUE,
            track_x     TEXT,
            track_y     TEXT,
            corners     TEXT,
            rotation    REAL
        );
    """)


def normalizar(coords, inverter=False):
    arr = np.array(coords, dtype=float)
    if inverter:
        arr = -arr
    mn, mx = arr.min(), arr.max()
    if mx - mn == 0:
        return [500.0] * len(coords)
    return ((arr - mn) / (mx - mn) * 1000).tolist()


def placeholder_oval():
    x, y = [], []
    for i in range(200):
        angle = 2 * math.pi * i / 200
        x.append(500 + 400 * math.cos(angle))
        y.append(500 + 250 * math.sin(angle))
    return x, y, [], 0.0


def extrair_tracado(nome_f1, ano):
    try:
        # Carregar qualificação com telemetria
        session = fastf1.get_session(ano, nome_f1, "Q")
        session.load(telemetry=True, weather=False, messages=False)

        fastest = session.laps.pick_fastest()
        tel = fastest.get_telemetry()

        x_raw = tel["X"].dropna().tolist()
        y_raw = tel["Y"].dropna().tolist()

        if len(x_raw) < 10:
            print(f"    AVISO: poucos pontos ({len(x_raw)}), a usar placeholder.")
            return placeholder_oval()

        # Subsampling para máx 500 pontos
        step = max(1, len(x_raw) // 500)
        x_raw = x_raw[::step]
        y_raw = y_raw[::step]

        x_norm = normalizar(x_raw)
        y_norm = normalizar(y_raw, inverter=True)

        # Corners
        corners = []
        try:
            circuit_info = session.get_circuit_info()
            rotation = float(circuit_info.rotation)
            cx = normalizar(circuit_info.corners["X"].tolist())
            cy = normalizar(circuit_info.corners["Y"].tolist(), inverter=True)
            nums = circuit_info.corners["Number"].tolist()
            for i in range(len(cx)):
                corners.append({"x": round(cx[i], 2), "y": round(cy[i], 2), "n": int(nums[i])})
        except Exception as e:
            print(f"    AVISO corners: {e}")
            rotation = 0.0

        return (
            [round(v, 2) for v in x_norm],
            [round(v, 2) for v in y_norm],
            corners,
            rotation
        )

    except Exception as e:
        print(f"    ERRO: {e}")
        return placeholder_oval()


def main():
    if not os.path.exists(DB_PATH):
        print("ERRO: f1_manager.db não encontrado.")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    criar_tabela(cursor)

    cursor.execute("SELECT id, name FROM circuits")
    circuitos_bd = {nome: cid for cid, nome in cursor.fetchall()}

    total_reais = 0
    total_placeholder = 0

    for nome_bd, info in CIRCUITOS.items():
        circuit_id = circuitos_bd.get(nome_bd)
        if not circuit_id:
            print(f"AVISO: '{nome_bd}' não encontrado na BD.")
            continue

        print(f"\n→ {nome_bd}")

        if info is None:
            print("  Sem dados FastF1 — placeholder.")
            x, y, corners, rotation = placeholder_oval()
            total_placeholder += 1
        else:
            nome_f1, ano = info
            print(f"  A descarregar {nome_f1} {ano}...")
            x, y, corners, rotation = extrair_tracado(nome_f1, ano)
            if len(x) == 200 and len(corners) == 0:
                total_placeholder += 1
            else:
                total_reais += 1

        cursor.execute("""
            INSERT OR REPLACE INTO circuit_coords
                (circuit_id, track_x, track_y, corners, rotation)
            VALUES (?, ?, ?, ?, ?)
        """, (circuit_id, json.dumps(x), json.dumps(y), json.dumps(corners), rotation))
        conn.commit()
        print(f"  ✓ {len(x)} pontos, {len(corners)} curvas.")

    conn.close()
    print(f"\n{'='*50}")
    print(f"  Traçados reais:       {total_reais}")
    print(f"  Placeholders:         {total_placeholder}")
    print(f"  Total processados:    {total_reais + total_placeholder}")


if __name__ == "__main__":
    main()
