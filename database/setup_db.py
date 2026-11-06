"""
F1 Manager — setup_db.py
Cria e povoa a base de dados SQLite com todos os dados iniciais.
Executa este script uma vez para criar o ficheiro f1_manager.db.
"""

import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "f1_manager.db")


def criar_tabelas(cursor):
    cursor.executescript("""
        PRAGMA foreign_keys = ON;

        CREATE TABLE IF NOT EXISTS teams (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            name        TEXT NOT NULL,
            full_name   TEXT,
            nationality TEXT,
            base        TEXT,
            founded     INTEGER,
            championships INTEGER DEFAULT 0,
            photo_path  TEXT
        );

        CREATE TABLE IF NOT EXISTS drivers (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name    TEXT NOT NULL,
            last_name     TEXT NOT NULL,
            code          TEXT,
            number        INTEGER,
            nationality   TEXT,
            date_of_birth TEXT,
            active        INTEGER DEFAULT 1,
            photo_path    TEXT
        );

        CREATE TABLE IF NOT EXISTS staff (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name  TEXT NOT NULL,
            last_name   TEXT NOT NULL,
            role        TEXT NOT NULL,
            team_id     INTEGER REFERENCES teams(id),
            nationality TEXT,
            age         INTEGER,
            skill       INTEGER DEFAULT 50,
            photo_path  TEXT
        );

        CREATE TABLE IF NOT EXISTS circuits (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            name        TEXT NOT NULL,
            country     TEXT,
            locality    TEXT,
            laps        INTEGER,
            lap_record  TEXT,
            first_gp    INTEGER,
            photo_path  TEXT
        );

        CREATE TABLE IF NOT EXISTS seasons (
            id   INTEGER PRIMARY KEY AUTOINCREMENT,
            year INTEGER UNIQUE NOT NULL
        );

        CREATE TABLE IF NOT EXISTS races (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            season_id  INTEGER REFERENCES seasons(id),
            circuit_id INTEGER REFERENCES circuits(id),
            round      INTEGER,
            name       TEXT,
            date       TEXT
        );

        CREATE TABLE IF NOT EXISTS race_results (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            race_id      INTEGER REFERENCES races(id),
            driver_id    INTEGER REFERENCES drivers(id),
            team_id      INTEGER REFERENCES teams(id),
            position     INTEGER,
            grid         INTEGER,
            points       REAL DEFAULT 0,
            laps         INTEGER,
            status       TEXT,
            fastest_lap  INTEGER DEFAULT 0
        );

        CREATE TABLE IF NOT EXISTS driver_standings (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            season_id INTEGER REFERENCES seasons(id),
            driver_id INTEGER REFERENCES drivers(id),
            team_id   INTEGER REFERENCES teams(id),
            position  INTEGER,
            points    REAL DEFAULT 0,
            wins      INTEGER DEFAULT 0
        );

        CREATE TABLE IF NOT EXISTS constructor_standings (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            season_id INTEGER REFERENCES seasons(id),
            team_id   INTEGER REFERENCES teams(id),
            position  INTEGER,
            points    REAL DEFAULT 0,
            wins      INTEGER DEFAULT 0
        );

        CREATE TABLE IF NOT EXISTS car_upgrades (
            id               INTEGER PRIMARY KEY AUTOINCREMENT,
            team_id          INTEGER REFERENCES teams(id),
            name             TEXT,
            component        TEXT,
            performance_gain REAL DEFAULT 0,
            cost             REAL DEFAULT 0,
            development_time INTEGER DEFAULT 0,
            installed        INTEGER DEFAULT 0
        );

        CREATE TABLE IF NOT EXISTS finances (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            team_id     INTEGER REFERENCES teams(id),
            season_id   INTEGER REFERENCES seasons(id),
            budget      REAL DEFAULT 0,
            spent       REAL DEFAULT 0,
            prize_money REAL DEFAULT 0,
            sponsorship REAL DEFAULT 0
        );

        CREATE TABLE IF NOT EXISTS contracts (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            person_type  TEXT NOT NULL,
            driver_id    INTEGER REFERENCES drivers(id),
            staff_id     INTEGER REFERENCES staff(id),
            team_id      INTEGER REFERENCES teams(id),
            season_start INTEGER,
            season_end   INTEGER,
            salary       REAL DEFAULT 0
        );

        CREATE TABLE IF NOT EXISTS game_save (
            id                INTEGER PRIMARY KEY AUTOINCREMENT,
            player_team_id    INTEGER REFERENCES teams(id),
            current_season_id INTEGER REFERENCES seasons(id),
            current_round     INTEGER DEFAULT 1,
            budget            REAL DEFAULT 0,
            created_at        TEXT DEFAULT (datetime('now')),
            updated_at        TEXT DEFAULT (datetime('now'))
        );
    """)


def inserir_seasons(cursor):
    anos = list(range(1950, 2027))
    cursor.executemany(
        "INSERT OR IGNORE INTO seasons (year) VALUES (?)",
        [(a,) for a in anos]
    )


def inserir_teams(cursor):
    teams = [
        ("Red Bull Racing",  "Oracle Red Bull Racing",              "Austrian",  "Milton Keynes, UK",      2005, 6),
        ("Ferrari",          "Scuderia Ferrari HP",                 "Italian",   "Maranello, Italy",       1950, 16),
        ("McLaren",          "McLaren Formula 1 Team",              "British",   "Woking, UK",             1966, 10),
        ("Mercedes",         "Mercedes-AMG Petronas F1 Team",       "German",    "Brackley, UK",           2010, 8),
        ("Aston Martin",     "Aston Martin Aramco F1 Team",         "British",   "Silverstone, UK",        2021, 0),
        ("Alpine",           "BWT Alpine F1 Team",                  "French",    "Enstone, UK",            2021, 2),
        ("Haas",             "MoneyGram Haas F1 Team",              "American",  "Kannapolis, USA",        2016, 0),
        ("Williams",         "Williams Racing",                     "British",   "Grove, UK",              1977, 7),
        ("Audi",             "Audi F1 Team",                        "German",    "Hinwil, Switzerland",    2026, 0),
        ("Racing Bulls",     "Visa Cash App Racing Bulls F1 Team",  "Italian",   "Faenza, Italy",          2006, 0),
        ("Cadillac",         "Cadillac F1 Team",                    "American",  "Concord, USA",           2026, 0),
    ]
    cursor.executemany("""
        INSERT OR IGNORE INTO teams
            (name, full_name, nationality, base, founded, championships)
        VALUES (?,?,?,?,?,?)
    """, teams)


def inserir_drivers(cursor):
    drivers = [
        # Red Bull Racing
        ("Max",         "Verstappen",  "VER",  1,  "Dutch",         "1997-09-30", 1),
        ("Isack",       "Hadjar",      "HAD",  6,  "French",        "2004-09-28", 1),
        # Ferrari
        ("Charles",     "Leclerc",     "LEC",  16, "Monegasque",    "1997-10-16", 1),
        ("Lewis",       "Hamilton",    "HAM",  44, "British",       "1985-01-07", 1),
        # McLaren
        ("Lando",       "Norris",      "NOR",  4,  "British",       "1999-11-13", 1),
        ("Oscar",       "Piastri",     "PIA",  81, "Australian",    "2001-04-06", 1),
        # Mercedes
        ("George",      "Russell",     "RUS",  63, "British",       "1998-02-15", 1),
        ("Andrea Kimi", "Antonelli",   "ANT",  12, "Italian",       "2006-08-25", 1),
        # Aston Martin
        ("Fernando",    "Alonso",      "ALO",  14, "Spanish",       "1981-07-29", 1),
        ("Lance",       "Stroll",      "STR",  18, "Canadian",      "1998-10-29", 1),
        # Alpine
        ("Pierre",      "Gasly",       "GAS",  10, "French",        "1996-02-07", 1),
        ("Franco",      "Colapinto",   "COL",  43, "Argentinian",   "2003-05-27", 1),
        # Haas
        ("Esteban",     "Ocon",        "OCO",  31, "French",        "1996-09-17", 1),
        ("Oliver",      "Bearman",     "BEA",  87, "British",       "2005-05-08", 1),
        # Williams
        ("Alexander",   "Albon",       "ALB",  23, "Thai",          "1996-03-23", 1),
        ("Carlos",      "Sainz",       "SAI",  55, "Spanish",       "1994-09-01", 1),
        # Audi
        ("Nico",        "Hulkenberg",  "HUL",  27, "German",        "1987-08-19", 1),
        ("Gabriel",     "Bortoleto",   "BOR",  5,  "Brazilian",     "2004-10-14", 1),
        # Racing Bulls
        ("Liam",        "Lawson",      "LAW",  30, "New Zealander", "2002-02-11", 1),
        ("Arvid",       "Lindblad",    "LIN",  8,  "Swedish",       "2006-06-06", 1),
        # Cadillac
        ("Sergio",      "Perez",       "PER",  11, "Mexican",       "1990-01-26", 1),
        ("Valtteri",    "Bottas",      "BOT",  77, "Finnish",       "1989-08-28", 1),
    ]
    cursor.executemany("""
        INSERT OR IGNORE INTO drivers
            (first_name, last_name, code, number, nationality, date_of_birth, active)
        VALUES (?,?,?,?,?,?,?)
    """, drivers)


def main():
    if os.path.exists(DB_PATH):
        print(f"Base de dados já existe: {DB_PATH}")
        resposta = input("Recriar do zero? (s/n): ").strip().lower()
        if resposta == "s":
            os.remove(DB_PATH)
            print("Ficheiro antigo removido.")
        else:
            print("Operação cancelada.")
            return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print("A criar tabelas...")
    criar_tabelas(cursor)

    print("A inserir temporadas (1950–2026)...")
    inserir_seasons(cursor)

    print("A inserir equipas 2026...")
    inserir_teams(cursor)

    print("A inserir pilotos 2026...")
    inserir_drivers(cursor)

    conn.commit()
    conn.close()

    tamanho = os.path.getsize(DB_PATH)
    print(f"\n✓ Base de dados criada: {DB_PATH}")
    print(f"  Tamanho: {tamanho / 1024:.1f} KB")
    print("\nTabelas criadas:")
    print("  teams, drivers, staff, circuits, seasons, races,")
    print("  race_results, driver_standings, constructor_standings,")
    print("  car_upgrades, finances, contracts, game_save")
    print("\nDados inseridos:")
    print("  77 temporadas (1950–2026)")
    print("  11 equipas da grelha 2026")
    print("  22 pilotos da grelha 2026")
    print("\nPróximos dados a adicionar:")
    print("  → circuitos e calendário 2026")
    print("  → contratos pilotos ↔ equipas")
    print("  → atributos de carro por equipa")


if __name__ == "__main__":
    main()
