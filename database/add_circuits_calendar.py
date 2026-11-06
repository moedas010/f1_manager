"""
F1 Manager — add_circuits_calendar.py
Adiciona os 24 circuitos e o calendário da época 2026.
"""

import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "f1_manager.db")


def inserir_circuitos(cursor):
    circuitos = [
        # (name, country, locality, laps, lap_record, first_gp)
        ("Melbourne Grand Prix Circuit",    "Australia",    "Melbourne",        58,  "1:20.235",  1996),
        ("Shanghai International Circuit",  "China",        "Shanghai",         56,  "1:32.238",  2004),
        ("Suzuka International Racing Course", "Japan",     "Suzuka",           53,  "1:30.983",  1987),
        ("Bahrain International Circuit",   "Bahrain",      "Sakhir",           57,  "1:31.447",  2004),
        ("Jeddah Corniche Circuit",         "Saudi Arabia", "Jeddah",           50,  "1:30.734",  2021),
        ("Miami International Autodrome",   "USA",          "Miami",            57,  "1:29.708",  2022),
        ("Circuit Gilles Villeneuve",       "Canada",       "Montreal",         70,  "1:13.078",  1978),
        ("Circuit de Monaco",               "Monaco",       "Monte Carlo",      78,  "1:14.260",  1950),
        ("Circuit de Barcelona-Catalunya",  "Spain",        "Barcelona",        66,  "1:18.183",  1991),
        ("Red Bull Ring",                   "Austria",      "Spielberg",        71,  "1:05.619",  1970),
        ("Silverstone Circuit",             "UK",           "Silverstone",      52,  "1:27.097",  1950),
        ("Circuit de Spa-Francorchamps",    "Belgium",      "Spa",              44,  "1:46.286",  1950),
        ("Hungaroring",                     "Hungary",      "Budapest",         70,  "1:16.627",  1986),
        ("Circuit Park Zandvoort",          "Netherlands",  "Zandvoort",        72,  "1:11.097",  1952),
        ("Autodromo Nazionale Monza",       "Italy",        "Monza",            53,  "1:21.046",  1950),
        ("Circuito de Madrid",              "Spain",        "Madrid",           55,  "N/A",        2026),
        ("Baku City Circuit",               "Azerbaijan",   "Baku",             51,  "1:43.009",  2016),
        ("Marina Bay Street Circuit",       "Singapore",    "Singapore",        62,  "1:41.905",  2008),
        ("Circuit of the Americas",         "USA",          "Austin",           56,  "1:36.169",  2012),
        ("Autodromo Hermanos Rodriguez",    "Mexico",       "Mexico City",      71,  "1:17.774",  1963),
        ("Autodromo Jose Carlos Pace",      "Brazil",       "Sao Paulo",        71,  "1:10.540",  1973),
        ("Las Vegas Street Circuit",        "USA",          "Las Vegas",        50,  "1:35.490",  2023),
        ("Lusail International Circuit",    "Qatar",        "Lusail",           57,  "1:24.319",  2021),
        ("Yas Marina Circuit",              "Abu Dhabi",    "Abu Dhabi",        58,  "1:26.103",  2009),
    ]
    cursor.executemany("""
        INSERT INTO circuits (name, country, locality, laps, lap_record, first_gp)
        VALUES (?,?,?,?,?,?)
    """, circuitos)
    print(f"  {len(circuitos)} circuitos inseridos.")


def inserir_calendario(cursor):
    # Buscar o id da época 2026
    cursor.execute("SELECT id FROM seasons WHERE year = 2026")
    season = cursor.fetchone()
    if not season:
        print("ERRO: época 2026 não encontrada. Corre primeiro o setup_db.py.")
        return
    season_id = season[0]

    # Buscar ids dos circuitos por nome
    cursor.execute("SELECT id, name FROM circuits")
    circuitos = {nome: cid for cid, nome in cursor.fetchall()}

    corridas = [
        # (round, name, circuit_name, date)
        (1,  "Australian Grand Prix",      "Melbourne Grand Prix Circuit",       "2026-03-08"),
        (2,  "Chinese Grand Prix",         "Shanghai International Circuit",     "2026-03-15"),
        (3,  "Japanese Grand Prix",        "Suzuka International Racing Course", "2026-03-29"),
        (4,  "Bahrain Grand Prix",         "Bahrain International Circuit",      "2026-04-12"),
        (5,  "Saudi Arabian Grand Prix",   "Jeddah Corniche Circuit",            "2026-04-19"),
        (6,  "Miami Grand Prix",           "Miami International Autodrome",      "2026-05-03"),
        (7,  "Canadian Grand Prix",        "Circuit Gilles Villeneuve",          "2026-05-24"),
        (8,  "Monaco Grand Prix",          "Circuit de Monaco",                  "2026-06-07"),
        (9,  "Spanish Grand Prix",         "Circuit de Barcelona-Catalunya",     "2026-06-14"),
        (10, "Austrian Grand Prix",        "Red Bull Ring",                      "2026-06-28"),
        (11, "British Grand Prix",         "Silverstone Circuit",                "2026-07-05"),
        (12, "Belgian Grand Prix",         "Circuit de Spa-Francorchamps",       "2026-07-19"),
        (13, "Hungarian Grand Prix",       "Hungaroring",                        "2026-07-26"),
        (14, "Dutch Grand Prix",           "Circuit Park Zandvoort",             "2026-08-23"),
        (15, "Italian Grand Prix",         "Autodromo Nazionale Monza",          "2026-09-06"),
        (16, "Madrid Grand Prix",          "Circuito de Madrid",                 "2026-09-13"),
        (17, "Azerbaijan Grand Prix",      "Baku City Circuit",                  "2026-09-26"),
        (18, "Singapore Grand Prix",       "Marina Bay Street Circuit",          "2026-10-11"),
        (19, "United States Grand Prix",   "Circuit of the Americas",            "2026-10-25"),
        (20, "Mexico City Grand Prix",     "Autodromo Hermanos Rodriguez",       "2026-11-01"),
        (21, "São Paulo Grand Prix",       "Autodromo Jose Carlos Pace",         "2026-11-08"),
        (22, "Las Vegas Grand Prix",       "Las Vegas Street Circuit",           "2026-11-21"),
        (23, "Qatar Grand Prix",           "Lusail International Circuit",       "2026-11-29"),
        (24, "Abu Dhabi Grand Prix",       "Yas Marina Circuit",                 "2026-12-06"),
    ]

    for ronda, nome, circuito_nome, data in corridas:
        circuit_id = circuitos.get(circuito_nome)
        if not circuit_id:
            print(f"  AVISO: circuito '{circuito_nome}' não encontrado.")
            continue
        cursor.execute("""
            INSERT INTO races (season_id, circuit_id, round, name, date)
            VALUES (?,?,?,?,?)
        """, (season_id, circuit_id, ronda, nome, data))

    print(f"  {len(corridas)} corridas inseridas para a época 2026.")


def main():
    if not os.path.exists(DB_PATH):
        print("ERRO: f1_manager.db não encontrado. Corre primeiro o setup_db.py.")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print("A inserir circuitos...")
    inserir_circuitos(cursor)

    print("A inserir calendário 2026...")
    inserir_calendario(cursor)

    conn.commit()

    # Confirmação
    cursor.execute("SELECT COUNT(*) FROM circuits")
    print(f"\n✓ Total circuitos na BD: {cursor.fetchone()[0]}")
    cursor.execute("SELECT COUNT(*) FROM races WHERE season_id = (SELECT id FROM seasons WHERE year = 2026)")
    print(f"✓ Total corridas 2026:   {cursor.fetchone()[0]}")

    conn.close()
    print("\nPróximo passo: contratos pilotos ↔ equipas")


if __name__ == "__main__":
    main()
