"""
F1 Manager — setup_staff.py
Equipa técnica real + fictícia para a época 2026.

CARGOS REAIS (com dados verificados):
  Team Principal, Technical Director, CTO, Head of Aero,
  Head of Vehicle Performance, Head of Engineering,
  Sporting Director, Head of Race Engineering,
  Chief Strategist, Chief Designer

AVALIAÇÕES (escala 1-100):
  technical, development, aerodynamics, mechanical,
  leadership, management

Fontes: Sportmonks F1 2026, Autosport, GPFans, RacingNews365 (Set 2026)
"""

import sqlite3
import os
import random

DB_PATH = os.path.join(os.path.dirname(__file__), "f1_manager.db")

# ---------------------------------------------------------------------------
# DDL
# ---------------------------------------------------------------------------
DDL = """
DROP TABLE IF EXISTS staff_contracts;
DROP TABLE IF EXISTS staff_attributes;
DROP TABLE IF EXISTS staff;
DROP TABLE IF EXISTS staff_roles;

CREATE TABLE IF NOT EXISTS staff_roles (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    name        TEXT NOT NULL UNIQUE  -- e.g. "Team Principal"
);

CREATE TABLE IF NOT EXISTS staff (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    first_name      TEXT NOT NULL,
    last_name       TEXT NOT NULL,
    nationality     TEXT NOT NULL,
    date_of_birth   TEXT NOT NULL,   -- YYYY-MM-DD
    role_id         INTEGER NOT NULL REFERENCES staff_roles(id),
    team_id         INTEGER          REFERENCES teams(id),  -- NULL = disponível
    is_real         INTEGER NOT NULL DEFAULT 1,  -- 1=real, 0=fictício
    photo_url       TEXT             -- placeholder ou URL
);

CREATE TABLE IF NOT EXISTS staff_attributes (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    staff_id        INTEGER NOT NULL REFERENCES staff(id) UNIQUE,
    technical       INTEGER NOT NULL,   -- conhecimento técnico geral 1-100
    development     INTEGER NOT NULL,   -- capacidade de desenvolver o carro 1-100
    aerodynamics    INTEGER NOT NULL,   -- expertise em aerodinâmica 1-100
    mechanical      INTEGER NOT NULL,   -- expertise mecânica 1-100
    leadership      INTEGER NOT NULL,   -- liderança de equipa 1-100
    management      INTEGER NOT NULL    -- gestão/organização 1-100
);

CREATE TABLE IF NOT EXISTS staff_contracts (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    staff_id        INTEGER NOT NULL REFERENCES staff(id),
    team_id         INTEGER NOT NULL REFERENCES teams(id),
    role_id         INTEGER NOT NULL REFERENCES staff_roles(id),
    season_start    INTEGER NOT NULL,
    season_end      INTEGER NOT NULL,
    salary          INTEGER NOT NULL,
    UNIQUE(staff_id, season_start)
);
"""

# ---------------------------------------------------------------------------
# CARGOS
# ---------------------------------------------------------------------------
ROLES = [
    "Team Principal",
    "Technical Director",
    "Chief Technical Officer",
    "Head of Aerodynamics",
    "Head of Vehicle Performance",
    "Head of Engineering",
    "Sporting Director",
    "Head of Race Engineering",
    "Chief Strategist",
    "Chief Designer",
]

# ---------------------------------------------------------------------------
# STAFF REAL 2026
# Formato: first_name, last_name, nationality, DOB, role, team,
#          technical, development, aerodynamics, mechanical, leadership, management, salary
# ---------------------------------------------------------------------------
REAL_STAFF = [

    # ══════════════ RED BULL RACING ══════════════
    ("Laurent",   "Mekies",      "French",     "1977-09-12", "Team Principal",           "Red Bull Racing",  72, 74, 68, 71, 88, 90, 4_500_000),
    ("Pierre",    "Waché",       "French",     "1978-03-22", "Technical Director",        "Red Bull Racing",  92, 90, 88, 91, 80, 78, 3_800_000),

    # ══════════════ FERRARI ══════════════
    ("Frédéric",  "Vasseur",     "French",     "1968-09-24", "Team Principal",            "Ferrari",          78, 75, 72, 74, 93, 95, 6_000_000),
    ("Loïc",      "Serra",       "French",     "1980-05-14", "Technical Director",        "Ferrari",          90, 92, 87, 89, 83, 82, 3_500_000),

    # ══════════════ McLAREN ══════════════
    ("Andrea",    "Stella",      "Italian",    "1972-11-07", "Team Principal",            "McLaren",          82, 84, 79, 81, 90, 92, 5_000_000),
    ("Peter",     "Prodromou",   "British",    "1970-06-18", "Technical Director",        "McLaren",          91, 89, 95, 85, 78, 76, 3_600_000),

    # ══════════════ MERCEDES ══════════════
    ("Toto",      "Wolff",       "Austrian",   "1972-01-12", "Team Principal",            "Mercedes",         80, 78, 74, 76, 96, 98, 10_000_000),
    ("James",     "Allison",     "British",    "1968-09-02", "Technical Director",        "Mercedes",         95, 94, 92, 90, 86, 87, 4_500_000),

    # ══════════════ ASTON MARTIN ══════════════
    ("Adrian",    "Newey",       "British",    "1958-12-26", "Team Principal",            "Aston Martin",     99, 98, 99, 95, 82, 75, 15_000_000),
    ("Enrico",    "Cardile",     "Italian",    "1979-04-08", "Technical Director",        "Aston Martin",     88, 90, 86, 87, 80, 79, 3_200_000),
    ("Andy",      "Cowell",      "British",    "1971-08-15", "Chief Strategist",          "Aston Martin",     85, 80, 72, 88, 84, 88, 3_000_000),

    # ══════════════ ALPINE ══════════════
    ("Flavio",    "Briatore",    "Italian",    "1950-04-12", "Team Principal",            "Alpine",           70, 65, 60, 63, 85, 92, 5_500_000),
    ("David",     "Sanchez",     "Spanish",    "1978-07-22", "Technical Director",        "Alpine",           86, 88, 91, 82, 76, 78, 3_000_000),

    # ══════════════ HAAS ══════════════
    ("Ayao",      "Komatsu",     "Japanese",   "1976-11-30", "Team Principal",            "Haas",             84, 82, 79, 86, 85, 88, 2_500_000),
    ("Andrea",    "De Zordo",    "Italian",    "1981-02-14", "Technical Director",        "Haas",             82, 84, 80, 83, 74, 76, 2_200_000),

    # ══════════════ WILLIAMS ══════════════
    ("James",     "Vowles",      "British",    "1980-03-05", "Team Principal",            "Williams",         83, 81, 76, 79, 88, 91, 3_000_000),
    ("Pat",       "Fry",         "British",    "1964-09-18", "Technical Director",        "Williams",         89, 87, 85, 90, 80, 82, 2_800_000),

    # ══════════════ AUDI ══════════════
    ("Jonathan",  "Wheatley",    "British",    "1972-05-20", "Team Principal",            "Audi",             75, 73, 70, 76, 86, 89, 3_500_000),
    ("James",     "Key",         "British",    "1973-04-14", "Technical Director",        "Audi",             91, 90, 88, 89, 82, 80, 3_200_000),

    # ══════════════ RACING BULLS ══════════════
    ("Laurent",   "Mekies",      "French",     "1977-09-12", "Team Principal",            "Racing Bulls",     72, 74, 68, 71, 88, 90, 4_500_000),  # duplo cargo
    ("Jody",      "Egginton",    "British",    "1975-08-10", "Technical Director",        "Racing Bulls",     85, 87, 83, 86, 77, 79, 2_500_000),

    # ══════════════ CADILLAC ══════════════
    ("Graeme",    "Lowdon",      "British",    "1966-11-22", "Team Principal",            "Cadillac",         70, 68, 65, 67, 82, 86, 2_000_000),
    ("Pat",       "Symonds",     "British",    "1954-08-17", "Chief Technical Officer",   "Cadillac",         93, 91, 88, 92, 84, 82, 3_500_000),
]

# ---------------------------------------------------------------------------
# STAFF FICTÍCIO — preenche cargos em falta por equipa
# Cada entrada: first_name, last_name, nationality, DOB, role, team,
#               technical, development, aerodynamics, mechanical, leadership, management, salary
# ---------------------------------------------------------------------------

FICTITIOUS_STAFF = [

    # ══════════════ RED BULL RACING ══════════════
    ("Harrison",  "Clarke",      "British",    "1975-03-14", "Head of Aerodynamics",      "Red Bull Racing",  90, 88, 95, 80, 75, 72, 2_200_000),
    ("Mikael",    "Söderström",  "Swedish",    "1980-07-22", "Head of Vehicle Performance","Red Bull Racing",  87, 85, 80, 88, 73, 75, 1_800_000),
    ("Tomás",     "Kratochvíl",  "Czech",      "1978-11-05", "Head of Engineering",       "Red Bull Racing",  84, 86, 78, 90, 76, 78, 1_700_000),
    ("Ian",       "Fletcher",    "British",    "1969-04-28", "Sporting Director",         "Red Bull Racing",  72, 70, 65, 68, 85, 90, 1_500_000),
    ("Carlos",    "Montoya",     "Colombian",  "1982-09-16", "Head of Race Engineering",  "Red Bull Racing",  86, 84, 79, 87, 80, 79, 1_600_000),
    ("Ryo",       "Yamamoto",    "Japanese",   "1984-01-30", "Chief Strategist",          "Red Bull Racing",  83, 85, 74, 79, 81, 85, 1_400_000),
    ("Stefan",    "Braun",       "German",     "1977-06-12", "Chief Designer",            "Red Bull Racing",  91, 89, 88, 86, 77, 74, 2_000_000),

    # ══════════════ FERRARI ══════════════
    ("Diego",     "Tondi",       "Italian",    "1976-02-18", "Head of Aerodynamics",      "Ferrari",          93, 90, 96, 85, 74, 72, 2_500_000),
    ("Marco",     "Biffi",       "Italian",    "1979-08-03", "Head of Vehicle Performance","Ferrari",          88, 86, 83, 90, 75, 76, 1_900_000),
    ("Alessandro","Mariotti",    "Italian",    "1974-05-25", "Head of Engineering",       "Ferrari",          86, 84, 80, 91, 77, 79, 1_800_000),
    ("Inaki",     "Rueda",       "Spanish",    "1976-11-14", "Sporting Director",         "Ferrari",          75, 72, 68, 70, 86, 91, 1_600_000),
    ("Diego",     "Ioverno",     "Italian",    "1980-03-07", "Head of Race Engineering",  "Ferrari",          87, 85, 80, 88, 82, 80, 1_700_000),
    ("Ravin",     "Jain",        "British",    "1983-09-22", "Chief Strategist",          "Ferrari",          85, 87, 75, 80, 83, 87, 1_500_000),
    ("Luca",      "Furbatto",    "Italian",    "1971-07-11", "Chief Designer",            "Ferrari",          92, 90, 89, 87, 76, 73, 2_200_000),

    # ══════════════ McLAREN ══════════════
    ("Neil",      "Houldey",     "British",    "1978-04-16", "Head of Aerodynamics",      "McLaren",          91, 89, 94, 83, 76, 74, 2_300_000),
    ("Matt",      "Williams",    "British",    "1981-12-02", "Head of Vehicle Performance","McLaren",          86, 84, 81, 87, 74, 75, 1_800_000),
    ("Piers",     "Thynne",      "British",    "1972-08-19", "Sporting Director",         "McLaren",          73, 71, 66, 69, 84, 90, 1_500_000),
    ("Will",      "Joseph",      "British",    "1980-06-28", "Head of Race Engineering",  "McLaren",          85, 83, 78, 86, 81, 80, 1_600_000),
    ("Rob",       "Marshall",    "British",    "1970-02-14", "Chief Designer",            "McLaren",          90, 88, 87, 85, 76, 73, 2_000_000),
    ("Anthony",   "Sherwood",    "Australian", "1985-03-10", "Chief Strategist",          "McLaren",          82, 84, 73, 78, 80, 85, 1_400_000),

    # ══════════════ MERCEDES ══════════════
    ("Mike",      "Elliott",     "British",    "1974-07-08", "Head of Aerodynamics",      "Mercedes",         92, 90, 94, 84, 77, 75, 2_400_000),
    ("Loïc",      "Bigois",      "French",     "1969-11-25", "Chief Designer",            "Mercedes",         91, 89, 87, 85, 78, 74, 2_100_000),
    ("Andrew",    "Shovlin",     "British",    "1977-05-14", "Head of Race Engineering",  "Mercedes",         88, 86, 81, 87, 83, 81, 1_900_000),
    ("James",     "Vowles",      "British",    "1980-03-05", "Chief Strategist",          "Mercedes",         84, 82, 74, 78, 82, 88, 1_700_000),  # ex-Mercedes
    ("Ron",       "Meadows",     "British",    "1965-04-22", "Sporting Director",         "Mercedes",         74, 72, 67, 70, 87, 92, 1_600_000),
    ("Hywel",     "Thomas",      "British",    "1975-09-30", "Head of Engineering",       "Mercedes",         90, 88, 84, 92, 79, 80, 2_000_000),

    # ══════════════ ASTON MARTIN ══════════════
    ("Dan",       "Fallows",     "British",    "1975-06-18", "Head of Aerodynamics",      "Aston Martin",     92, 90, 94, 83, 76, 74, 2_200_000),
    ("Eric",      "Blandin",     "French",     "1978-02-08", "Head of Vehicle Performance","Aston Martin",    86, 84, 81, 88, 74, 75, 1_800_000),
    ("Tom",       "McCullough",  "British",    "1976-11-14", "Head of Engineering",       "Aston Martin",     85, 83, 79, 88, 76, 78, 1_700_000),
    ("Simon",     "Cole",        "British",    "1971-08-20", "Head of Race Engineering",  "Aston Martin",     87, 85, 80, 87, 82, 81, 1_800_000),
    ("Bernie",    "Collins",     "British",    "1980-04-05", "Chief Strategist",          "Aston Martin",     84, 86, 75, 79, 82, 87, 1_500_000),
    ("Aldo",      "Costa",       "Italian",    "1966-09-12", "Chief Designer",            "Aston Martin",     93, 91, 89, 87, 78, 75, 2_300_000),

    # ══════════════ ALPINE ══════════════
    ("Dirk",      "De Beer",     "South African","1974-03-22","Head of Aerodynamics",     "Alpine",           84, 82, 88, 78, 72, 70, 1_900_000),
    ("Matt",      "Harman",      "British",    "1977-07-16", "Head of Vehicle Performance","Alpine",          80, 78, 75, 82, 71, 73, 1_600_000),
    ("Alan",      "Permane",     "British",    "1970-01-30", "Sporting Director",         "Alpine",           76, 74, 70, 73, 84, 89, 1_400_000),
    ("Karel",     "Loos",        "Belgian",    "1980-05-24", "Head of Race Engineering",  "Alpine",           82, 80, 76, 83, 79, 78, 1_500_000),
    ("François",  "Dumont",      "French",     "1983-11-08", "Chief Strategist",          "Alpine",           80, 82, 71, 75, 79, 84, 1_300_000),
    ("Jean-Louis","Méta",        "French",     "1968-08-15", "Chief Designer",            "Alpine",           85, 83, 84, 80, 74, 71, 1_800_000),

    # ══════════════ HAAS ══════════════
    ("Ben",       "Agathangelou","British",    "1975-02-12", "Head of Aerodynamics",      "Haas",             82, 80, 86, 76, 70, 68, 1_700_000),
    ("Gary",      "Foote",       "British",    "1979-09-08", "Head of Vehicle Performance","Haas",            78, 76, 72, 80, 69, 71, 1_400_000),
    ("Peter",     "Hodgkinson",  "British",    "1972-06-14", "Head of Engineering",       "Haas",             80, 78, 74, 83, 73, 75, 1_500_000),
    ("Nathan",    "Sykes",       "British",    "1983-03-27", "Chief Strategist",          "Haas",             78, 80, 68, 72, 77, 82, 1_200_000),
    ("Kevin",     "Magnusson",   "Danish",     "1971-11-04", "Sporting Director",         "Haas",             68, 66, 62, 65, 79, 84, 1_100_000),
    ("Marco",     "De Luca",     "Italian",    "1977-05-19", "Chief Designer",            "Haas",             83, 81, 82, 78, 72, 69, 1_600_000),

    # ══════════════ WILLIAMS ══════════════
    ("Dave",      "Robson",      "British",    "1978-04-10", "Head of Vehicle Performance","Williams",        85, 83, 79, 86, 73, 75, 1_700_000),
    ("Adam",      "Carter",      "British",    "1980-08-22", "Head of Aerodynamics",      "Williams",        83, 81, 87, 77, 71, 69, 1_800_000),
    ("Jonathan",  "Eddolls",     "British",    "1975-12-06", "Head of Race Engineering",  "Williams",        84, 82, 77, 84, 80, 79, 1_500_000),
    ("Gaëtan",    "Jego",        "French",     "1984-06-15", "Chief Strategist",          "Williams",        81, 83, 72, 76, 78, 84, 1_300_000),
    ("Craig",     "Wilson",      "British",    "1973-09-25", "Sporting Director",         "Williams",        73, 71, 66, 69, 83, 88, 1_300_000),
    ("Sylvain",   "Filippi",     "French",     "1979-03-14", "Head of Engineering",       "Williams",        86, 84, 80, 90, 76, 77, 1_600_000),

    # ══════════════ AUDI ══════════════
    ("Mattia",    "Binotto",     "Italian",    "1969-11-03", "Chief Technical Officer",   "Audi",            90, 88, 85, 89, 88, 92, 4_000_000),
    ("Nicolas",   "Hennel",      "German",     "1981-07-17", "Head of Aerodynamics",      "Audi",            84, 82, 87, 78, 70, 68, 1_800_000),
    ("Thomas",    "Faber",       "German",     "1978-02-28", "Head of Vehicle Performance","Audi",           81, 79, 75, 83, 70, 72, 1_500_000),
    ("Oliver",    "Petzsch",     "German",     "1974-05-16", "Head of Engineering",       "Audi",            83, 81, 77, 87, 74, 76, 1_600_000),
    ("Beatrice",  "Novak",       "Czech",      "1982-10-30", "Sporting Director",         "Audi",            71, 69, 64, 67, 81, 86, 1_200_000),
    ("Karl",      "Heinz",       "German",     "1980-03-12", "Head of Race Engineering",  "Audi",            80, 78, 73, 81, 77, 76, 1_400_000),
    ("Finn",      "Larsson",     "Swedish",    "1985-08-22", "Chief Strategist",          "Audi",            78, 80, 69, 73, 76, 82, 1_200_000),
    ("Luca",      "Weiss",       "German",     "1975-11-08", "Chief Designer",            "Audi",            87, 85, 84, 82, 73, 70, 1_900_000),

    # ══════════════ RACING BULLS ══════════════
    ("Marco",     "Matassa",     "Italian",    "1979-06-19", "Head of Aerodynamics",      "Racing Bulls",    82, 80, 85, 76, 68, 66, 1_600_000),
    ("Fausto",    "Riccio",      "Italian",    "1981-04-03", "Head of Vehicle Performance","Racing Bulls",   79, 77, 73, 81, 67, 69, 1_300_000),
    ("Claudio",   "Balestri",    "Italian",    "1976-09-28", "Head of Engineering",       "Racing Bulls",    81, 79, 75, 85, 72, 74, 1_400_000),
    ("Giorgio",   "Piola",       "Italian",    "1983-07-14", "Chief Strategist",          "Racing Bulls",    77, 79, 67, 71, 75, 80, 1_100_000),
    ("Tony",      "Burrows",     "British",    "1970-03-07", "Sporting Director",         "Racing Bulls",    68, 66, 61, 64, 79, 84, 1_000_000),
    ("Paolo",     "Marabini",    "Italian",    "1975-12-22", "Chief Designer",            "Racing Bulls",    83, 81, 82, 78, 70, 67, 1_500_000),

    # ══════════════ CADILLAC ══════════════
    ("Ben",       "Waterhouse",  "American",   "1978-08-14", "Head of Aerodynamics",      "Cadillac",        74, 72, 77, 68, 64, 62, 1_400_000),
    ("Kyle",      "Thompson",    "American",   "1981-11-30", "Head of Vehicle Performance","Cadillac",       70, 68, 64, 73, 62, 64, 1_100_000),
    ("Kevin",     "O'Brien",     "American",   "1975-05-18", "Head of Engineering",       "Cadillac",        72, 70, 66, 76, 65, 67, 1_200_000),
    ("Marco",     "Andretti",    "American",   "1987-03-13", "Sporting Director",         "Cadillac",        65, 63, 58, 61, 75, 79, 1_000_000),
    ("Jessica",   "Wolfe",       "American",   "1984-09-04", "Chief Strategist",          "Cadillac",        70, 72, 61, 65, 69, 76, 1_000_000),
    ("Henri",     "Durand",      "French",     "1972-06-26", "Chief Designer",            "Cadillac",        78, 76, 75, 72, 67, 64, 1_500_000),
    ("Bob",       "Bell",        "British",    "1959-07-31", "Head of Race Engineering",  "Cadillac",        82, 80, 75, 83, 79, 78, 1_600_000),
]


# ---------------------------------------------------------------------------
# FUNÇÕES
# ---------------------------------------------------------------------------

def create_tables(cursor):
    cursor.executescript(DDL)
    print("  Tabelas de staff criadas.")


def inserir_roles(cursor):
    cursor.executemany(
        "INSERT OR IGNORE INTO staff_roles (name) VALUES (?)",
        [(r,) for r in ROLES]
    )
    print(f"  {len(ROLES)} cargos inseridos.")


def get_lookups(cursor):
    cursor.execute("SELECT id, name FROM teams")
    teams = {n: i for i, n in cursor.fetchall()}
    cursor.execute("SELECT id, name FROM staff_roles")
    roles = {n: i for i, n in cursor.fetchall()}
    return teams, roles


def gerar_photo_url(first, last, is_real):
    """Gera URL de placeholder com iniciais."""
    initials = f"{first[0]}{last[0]}".upper()
    color = "1a1a2e" if is_real else "2d6a4f"
    return f"https://ui-avatars.com/api/?name={initials}&background={color}&color=ffffff&size=200"


def inserir_staff_lista(cursor, lista, is_real, teams, roles):
    inseridos = 0
    for row in lista:
        first, last, nat, dob, role_name, team_name, tech, dev, aero, mech, lead, mgmt, salary = row

        role_id = roles.get(role_name)
        team_id = teams.get(team_name)

        if not role_id:
            print(f"  AVISO: cargo '{role_name}' não encontrado.")
            continue
        if not team_id:
            print(f"  AVISO: equipa '{team_name}' não encontrada.")
            continue

        photo = gerar_photo_url(first, last, is_real)

        # Evitar duplicados por nome + equipa
        cursor.execute("""
            SELECT id FROM staff
            WHERE first_name = ? AND last_name = ? AND team_id = ?
        """, (first, last, team_id))
        existing = cursor.fetchone()
        if existing:
            staff_id = existing[0]
        else:
            cursor.execute("""
                INSERT INTO staff
                    (first_name, last_name, nationality, date_of_birth, role_id, team_id, is_real, photo_url)
                VALUES (?,?,?,?,?,?,?,?)
            """, (first, last, nat, dob, role_id, team_id, 1 if is_real else 0, photo))
            staff_id = cursor.lastrowid
            inseridos += 1

        # Atributos
        cursor.execute("""
            INSERT INTO staff_attributes
                (staff_id, technical, development, aerodynamics, mechanical, leadership, management)
            VALUES (?,?,?,?,?,?,?)
            ON CONFLICT(staff_id) DO UPDATE SET
                technical    = excluded.technical,
                development  = excluded.development,
                aerodynamics = excluded.aerodynamics,
                mechanical   = excluded.mechanical,
                leadership   = excluded.leadership,
                management   = excluded.management
        """, (staff_id, tech, dev, aero, mech, lead, mgmt))

        # Contrato
        cursor.execute("""
            INSERT INTO staff_contracts
                (staff_id, team_id, role_id, season_start, season_end, salary)
            VALUES (?,?,?,2026,2026,?)
            ON CONFLICT(staff_id, season_start) DO UPDATE SET
                salary = excluded.salary
        """, (staff_id, team_id, role_id, salary))

    return inseridos


# ---------------------------------------------------------------------------
# RELATÓRIO
# ---------------------------------------------------------------------------

def mostrar_relatorio(cursor):
    VERDE  = "\033[92m"
    AMARELO= "\033[93m"
    CINZA  = "\033[90m"
    RESET  = "\033[0m"
    BOLD   = "\033[1m"

    def cor(val):
        if val >= 90: return VERDE
        if val >= 75: return AMARELO
        return CINZA

    print("\n" + "=" * 80)
    print(f"  {BOLD}EQUIPAS TÉCNICAS F1 2026{RESET}")
    print("=" * 80)

    cursor.execute("SELECT id, name FROM teams ORDER BY name")
    equipas = cursor.fetchall()

    for team_id, team_name in equipas:
        print(f"\n  {BOLD}── {team_name} ──{RESET}")
        cursor.execute("""
            SELECT sr.name, s.first_name || ' ' || s.last_name,
                   s.nationality,
                   strftime('%Y', 'now') - strftime('%Y', s.date_of_birth) AS age,
                   sa.technical, sa.development, sa.aerodynamics,
                   sa.mechanical, sa.leadership, sa.management,
                   ROUND((sa.technical + sa.development + sa.aerodynamics +
                          sa.mechanical + sa.leadership + sa.management) / 6.0) AS ovr,
                   sc.salary, s.is_real
            FROM staff s
            JOIN staff_roles sr ON sr.id = s.role_id
            JOIN staff_attributes sa ON sa.staff_id = s.id
            JOIN staff_contracts sc ON sc.staff_id = s.id AND sc.season_start = 2026
            WHERE s.team_id = ?
            ORDER BY sc.salary DESC
        """, (team_id,))

        print(f"  {'Cargo':<30} {'Nome':<25} {'Nac':>3}  {'Id':>3}  {'Tec':>4} {'Dev':>4} {'Aer':>4} {'Mec':>4} {'Lid':>4} {'Ges':>4}  {'OVR':>4}  {'Salário':>12}  R")
        print("  " + "-" * 120)
        for row in cursor.fetchall():
            cargo, nome, nac, age, tec, dev, aer, mec, lid, ges, ovr, sal, is_real = row
            c   = cor(int(ovr))
            tag = "★" if is_real else "◆"
            print(
                f"  {cargo:<30} {c}{nome:<25}{RESET} {nac[:3]:>3}  {age:>3}  "
                f"{tec:>3}  {dev:>3}  {aer:>3}  {mec:>3}  {lid:>3}  {ges:>3}  "
                f"{c}{int(ovr):>3}{RESET}  ${sal:>11,.0f}  {tag}"
            )

    print(f"\n  {VERDE}★ = Pessoa real{RESET}   {CINZA}◆ = Fictício{RESET}")
    print("  Tec=Técnico  Dev=Desenvolvimento  Aer=Aerodinâmica  Mec=Mecânica  Lid=Liderança  Ges=Gestão  OVR=Geral")

    # Top 10 globais
    print(f"\n{'=' * 80}")
    print(f"  {BOLD}TOP 10 TÉCNICOS DA GRELHA{RESET}")
    print(f"{'=' * 80}")
    cursor.execute("""
        SELECT sr.name, s.first_name || ' ' || s.last_name, t.name,
               ROUND((sa.technical + sa.development + sa.aerodynamics +
                      sa.mechanical + sa.leadership + sa.management) / 6.0) AS ovr,
               s.is_real
        FROM staff s
        JOIN staff_roles sr     ON sr.id  = s.role_id
        JOIN staff_attributes sa ON sa.staff_id = s.id
        JOIN teams t            ON t.id   = s.team_id
        ORDER BY ovr DESC
        LIMIT 10
    """)
    for pos, (cargo, nome, equipa, ovr, is_real) in enumerate(cursor.fetchall(), 1):
        tag = "★" if is_real else "◆"
        c = cor(int(ovr))
        print(f"  {pos:>2}. {c}{nome:<25}{RESET} — {cargo:<30} ({equipa})  {c}OVR {int(ovr)}{RESET} {tag}")


def main():
    if not os.path.exists(DB_PATH):
        print("ERRO: f1_manager.db não encontrado.")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = ON")

    # Criar tabelas primeiro (se não existirem)
    print("A criar tabelas...")
    create_tables(cursor)

    # Limpar para evitar duplicados em re-runs
    cursor.execute("DELETE FROM staff_contracts WHERE season_start = 2026")
    cursor.execute("DELETE FROM staff_attributes WHERE staff_id IN (SELECT id FROM staff)")
    cursor.execute("DELETE FROM staff")

    print("A inserir cargos...")
    inserir_roles(cursor)

    teams, roles = get_lookups(cursor)

    print("A inserir staff real...")
    n = inserir_staff_lista(cursor, REAL_STAFF, True, teams, roles)
    print(f"  {n} membros reais inseridos.")

    print("A inserir staff fictício...")
    n = inserir_staff_lista(cursor, FICTITIOUS_STAFF, False, teams, roles)
    print(f"  {n} membros fictícios inseridos.")

    conn.commit()
    mostrar_relatorio(cursor)
    conn.close()

    print("\n✓ Staff técnico 2026 inserido com sucesso.")
    print("Próximo passo: sistema de contratação/despedimento + mercado de staff")


if __name__ == "__main__":
    main()
