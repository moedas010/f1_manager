"""
F1 Manager — add_contracts.py
Contratos reais da época 2026:
  - 22 pilotos titulares com salários e datas reais
  - Pilotos reserva e de simulador por equipa
  - Fontes: GPFans, MotorSport Magazine, RacingNews365, F1Oversteer (Set 2026)
"""

import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "f1_manager.db")


RESERVAS = [
    ("Yuki",      "Tsunoda",    "TSU", 22, "Japanese",   "2000-05-11", 1),
    ("Ayumu",     "Iwasa",      "IWA", 19, "Japanese",   "2002-03-08", 1),
    ("Antonio",   "Giovinazzi", "GIO", 99, "Italian",    "1993-12-14", 1),
    ("Pato",      "O'Ward",     "OWA", 85, "Mexican",    "2000-03-06", 1),
    ("Leonardo",  "Fornaroli",  "FOR", 88, "Italian",    "2005-02-16", 1),
    ("Frederik",  "Vesti",      "VES", 70, "Danish",     "2002-04-18", 1),
    ("Doriane",   "Pin",        "PIN", 41, "French",     "2004-06-07", 1),
    ("Theo",      "Pourchaire", "POU", 98, "French",     "2003-08-20", 1),
    ("Luke",      "Browning",   "BRO", 34, "British",    "2002-02-19", 1),
    ("Victor",    "Martins",    "MAR", 46, "French",     "2001-06-25", 1),
    ("Jak",       "Crawford",   "CRA", 37, "American",   "2003-05-02", 1),
    ("Stoffel",   "Vandoorne",  "VAN",  2, "Belgian",    "1992-03-26", 1),
    ("Paul",      "Aron",       "ARO", 42, "Estonian",   "2003-07-14", 1),
    ("Kush",      "Maini",      "MAI", 29, "Indian",     "2001-03-21", 1),
    ("Jack",      "Doohan",     "DOO",  7, "Australian", "2003-01-20", 1),
    ("Ryo",       "Hirakawa",   "HIR", 53, "Japanese",   "1994-07-19", 1),
    ("Freddie",   "Slater",     "SLA", 62, "British",    "2005-06-19", 1),
    ("Zhou",      "Guanyu",     "ZHO", 24, "Chinese",    "1999-05-30", 1),
    ("Colton",    "Herta",      "HER", 26, "American",   "2000-03-11", 1),
    ("Pietro",    "Fittipaldi", "FIT", 51, "Brazilian",  "1996-06-17", 1),
]


def inserir_pilotos_reserva(cursor):
    cursor.executemany("""
        INSERT OR IGNORE INTO drivers
            (first_name, last_name, code, number, nationality, date_of_birth, active)
        VALUES (?,?,?,?,?,?,?)
    """, RESERVAS)
    print(f"  {len(RESERVAS)} pilotos reserva/sim inseridos.")


def inserir_contratos(cursor):
    cursor.execute("SELECT id, name FROM teams")
    equipas = {nome: eid for eid, nome in cursor.fetchall()}

    cursor.execute("SELECT id, code FROM drivers")
    pilotos = {code: did for did, code in cursor.fetchall()}

    titulares = [
        ("VER", "Red Bull Racing",  2026, 2028, 70_000_000, "driver"),
        ("HAD", "Red Bull Racing",  2026, 2026,  5_000_000, "driver"),
        ("HAM", "Ferrari",          2026, 2027, 60_000_000, "driver"),
        ("LEC", "Ferrari",          2026, 2030, 34_000_000, "driver"),
        ("NOR", "McLaren",          2026, 2028, 30_000_000, "driver"),
        ("PIA", "McLaren",          2026, 2028, 13_000_000, "driver"),
        ("RUS", "Mercedes",         2026, 2027, 34_000_000, "driver"),
        ("ANT", "Mercedes",         2026, 2029, 12_500_000, "driver"),
        ("ALO", "Aston Martin",     2026, 2026, 20_000_000, "driver"),
        ("STR", "Aston Martin",     2026, 2026, 13_500_000, "driver"),
        ("GAS", "Alpine",           2026, 2028, 12_000_000, "driver"),
        ("COL", "Alpine",           2026, 2026,  3_000_000, "driver"),
        ("OCO", "Haas",             2026, 2026,  7_000_000, "driver"),
        ("BEA", "Haas",             2026, 2026,  2_000_000, "driver"),
        ("ALB", "Williams",         2026, 2027,  8_000_000, "driver"),
        ("SAI", "Williams",         2026, 2026, 13_000_000, "driver"),
        ("HUL", "Audi",             2026, 2026,  6_000_000, "driver"),
        ("BOR", "Audi",             2026, 2026,  2_000_000, "driver"),
        ("LAW", "Racing Bulls",     2026, 2026,  3_000_000, "driver"),
        ("LIN", "Racing Bulls",     2026, 2026,  1_000_000, "driver"),
        ("PER", "Cadillac",         2026, 2027,  5_000_000, "driver"),
        ("BOT", "Cadillac",         2026, 2027,  5_000_000, "driver"),
    ]

    reservas = [
        ("TSU", "Red Bull Racing",  2026, 2026,  3_000_000, "reserve"),
        ("TSU", "Racing Bulls",     2026, 2026,  3_000_000, "reserve"),
        ("IWA", "Racing Bulls",     2026, 2026,    500_000, "simulator"),
        ("GIO", "Ferrari",          2026, 2026,    800_000, "reserve"),
        ("OWA", "McLaren",          2026, 2026,  1_000_000, "reserve"),
        ("FOR", "McLaren",          2026, 2026,    300_000, "simulator"),
        ("VES", "Mercedes",         2026, 2026,  1_500_000, "reserve"),
        ("PIN", "Mercedes",         2026, 2026,    250_000, "simulator"),
        ("POU", "Mercedes",         2026, 2026,    250_000, "simulator"),
        ("BRO", "Williams",         2026, 2026,    400_000, "reserve"),
        ("MAR", "Williams",         2026, 2026,    300_000, "simulator"),
        ("CRA", "Aston Martin",     2026, 2026,    600_000, "reserve"),
        ("VAN", "Aston Martin",     2026, 2026,    500_000, "reserve"),
        ("ARO", "Alpine",           2026, 2026,    500_000, "reserve"),
        ("MAI", "Alpine",           2026, 2026,    400_000, "reserve"),
        ("DOO", "Haas",             2026, 2026,    800_000, "reserve"),
        ("HIR", "Haas",             2026, 2026,    600_000, "reserve"),
        ("SLA", "Audi",             2026, 2026,    200_000, "simulator"),
        ("ZHO", "Cadillac",         2026, 2026,  1_500_000, "reserve"),
        ("HER", "Cadillac",         2026, 2026,    800_000, "simulator"),
        ("FIT", "Cadillac",         2026, 2026,    300_000, "simulator"),
    ]

    todos = titulares + reservas
    inseridos = 0
    for code, team_name, s_start, s_end, salary, role in todos:
        driver_id = pilotos.get(code)
        team_id   = equipas.get(team_name)
        if not driver_id:
            print(f"  AVISO: piloto '{code}' não encontrado.")
            continue
        if not team_id:
            print(f"  AVISO: equipa '{team_name}' não encontrada.")
            continue
        cursor.execute("""
            INSERT INTO contracts
                (person_type, driver_id, team_id, season_start, season_end, salary)
            VALUES (?,?,?,?,?,?)
        """, (role, driver_id, team_id, s_start, s_end, salary))
        inseridos += 1

    print(f"  {inseridos} contratos inseridos ({len(titulares)} titulares + {len(reservas)} reservas/sim).")


def mostrar_grelha(cursor):
    print("\n" + "=" * 60)
    print("  GRELHA TITULARES 2026")
    print("=" * 60)
    cursor.execute("""
        SELECT t.name, d.code, d.first_name || ' ' || d.last_name,
               c.salary, c.season_end
        FROM contracts c
        JOIN drivers d ON d.id = c.driver_id
        JOIN teams   t ON t.id = c.team_id
        WHERE c.season_start = 2026 AND c.person_type = 'driver'
        ORDER BY t.name, c.salary DESC
    """)
    equipa_atual = ""
    for equipa, code, nome, salario, fim in cursor.fetchall():
        if equipa != equipa_atual:
            print(f"\n  {equipa}")
            equipa_atual = equipa
        print(f"    [{code}] {nome:<28} ${salario:>12,.0f}   ate {fim}")

    print("\n" + "=" * 60)
    print("  RESERVAS & SIMULADORES 2026")
    print("=" * 60)
    cursor.execute("""
        SELECT t.name, c.person_type, d.code, d.first_name || ' ' || d.last_name, c.salary
        FROM contracts c
        JOIN drivers d ON d.id = c.driver_id
        JOIN teams   t ON t.id = c.team_id
        WHERE c.season_start = 2026 AND c.person_type IN ('reserve','simulator')
        ORDER BY t.name, c.person_type, d.last_name
    """)
    equipa_atual = ""
    for equipa, role, code, nome, salario in cursor.fetchall():
        if equipa != equipa_atual:
            print(f"\n  {equipa}")
            equipa_atual = equipa
        label = "Reserva " if role == "reserve" else "Sim     "
        print(f"    {label} [{code}] {nome:<28} ${salario:>8,.0f}")


def main():
    if not os.path.exists(DB_PATH):
        print("ERRO: f1_manager.db nao encontrado. Corre primeiro o setup_db.py.")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Limpar dados anteriores para evitar duplicados
    cursor.execute("DELETE FROM contracts WHERE season_start = 2026")
    reserva_codes = "','".join([r[2] for r in RESERVAS])
    cursor.execute(f"DELETE FROM drivers WHERE code IN ('{reserva_codes}')")

    print("A inserir pilotos reserva/sim...")
    inserir_pilotos_reserva(cursor)

    print("A inserir contratos 2026...")
    inserir_contratos(cursor)

    conn.commit()
    mostrar_grelha(cursor)
    conn.close()

    print("\n✓ Contratos 2026 atualizados com dados reais.")
    print("Proximo passo: atributos de carro por equipa")


if __name__ == "__main__":
    main()
