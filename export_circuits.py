"""
F1 Manager 2026 — export_circuits.py

Lê a base de dados (database/f1_manager.db) e gera ui/circuits_data.js
com os traçados reais (track_x / track_y, vindos do FASTF1) de cada
circuito, indexados pelo "round" — que é o mesmo valor usado como
race_id no resto do projeto (ver index.html: `race.html?race=${game.round}`).

Corre este script sempre que atualizares/recriares a base de dados:

    python export_circuits.py

Ele escreve/atualiza automaticamente: ui/circuits_data.js
"""

import sqlite3
import json
import os

BASE = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE, "database", "f1_manager.db")
OUT_PATH = os.path.join(BASE, "ui", "circuits_data.js")


def main():
    if not os.path.exists(DB_PATH):
        raise SystemExit(f"Base de dados não encontrada em: {DB_PATH}")

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    rows = conn.execute("""
        SELECT r.id as race_id, r.circuit_id as circuit_id, c.name as circuit_name,
               cc.track_x as track_x, cc.track_y as track_y
        FROM races r
        JOIN circuits c ON c.id = r.circuit_id
        LEFT JOIN circuit_coords cc ON cc.circuit_id = r.circuit_id
        ORDER BY r.id
    """).fetchall()
    conn.close()

    tracks = {}
    missing = []
    signature_map = {}  # assinatura do traçado -> lista de "#round circuito (circuit_id)"

    for row in rows:
        if not row["track_x"] or not row["track_y"]:
            missing.append(f'#{row["race_id"]} {row["circuit_name"]}')
            continue
        tracks[str(row["race_id"])] = {
            "x": json.loads(row["track_x"]),
            "y": json.loads(row["track_y"]),
            "name": row["circuit_name"],
        }
        # Assinatura simples do traçado (para detetar circuitos com coordenadas
        # repetidas — p.ex. dois circuit_id diferentes a apontar para a mesma
        # entrada em circuit_coords, ou o mesmo circuit_id usado em 2 corridas).
        sig = (row["track_x"][:60], row["track_y"][:60], len(row["track_x"]))
        label = f'ronda {row["race_id"]} — {row["circuit_name"]} (circuit_id={row["circuit_id"]})'
        signature_map.setdefault(sig, []).append(label)

    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        f.write("// Gerado automaticamente por export_circuits.py — NÃO editar à mão.\n")
        f.write("// Traçados reais dos circuitos (FASTF1), indexados por round/race_id.\n")
        f.write("const CIRCUIT_TRACKS = ")
        f.write(json.dumps(tracks, ensure_ascii=False))
        f.write(";\n")

    print(f"[OK] {len(tracks)} circuitos exportados para {OUT_PATH}")
    if missing:
        print("[AVISO] Sem coordenadas em circuit_coords para:")
        for m in missing:
            print(f"   - {m}")

    duplicates = {sig: labels for sig, labels in signature_map.items() if len(labels) > 1}
    if duplicates:
        print("\n[AVISO] Traçados REPETIDOS encontrados — estas corridas estão a usar")
        print("        exatamente as mesmas coordenadas (verifica circuit_id em 'races'")
        print("        e os dados em 'circuit_coords' para estes casos):")
        for sig, labels in duplicates.items():
            print("   • " + "  ==  ".join(labels))


if __name__ == "__main__":
    main()
