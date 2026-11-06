"""
F1 Manager — setup_attributes.py
Atributos realistas de carros e pilotos para a época 2026.

CARROS (por equipa):
  - chassis, aero, gearbox, brakes, reliability, fuel_efficiency
  - engine (separado, reflecte o fornecedor)

MOTORES (fornecedor, usado por várias equipas):
  - Mercedes > Ferrari > Audi > Honda (Ford)
  - Valores em escala 1-100

PILOTOS:
  - pace, racecraft, tyre_management, wet_weather,
    consistency, experience, fitness, aggression
  - Baseado em dados reais 2025-26

Fontes: GPFans, Autosport, MotorSport Magazine, F1Oversteer
"""

import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "f1_manager.db")


# ---------------------------------------------------------------------------
# MOTORES — escala 1-100
# Hierarquia 2026: Mercedes > Ferrari ≈ Audi > Honda/Ford
# ---------------------------------------------------------------------------
ENGINES = {
    # (fabricante, power, driveability, reliability, fuel_efficiency)
    "Mercedes": dict(
        manufacturer="Mercedes",
        power=98,           # melhor motor da grelha, híbrido revolucionário
        driveability=92,    # entrega de potência suave
        reliability=90,
        fuel_efficiency=88,
    ),
    "Ferrari": dict(
        manufacturer="Ferrari",
        power=91,
        driveability=86,
        reliability=85,
        fuel_efficiency=84,
    ),
    "Audi": dict(
        manufacturer="Audi",    # estreia 2026, motor sólido mas não top
        power=87,
        driveability=83,
        reliability=80,         # primeiro ano, margem de erro maior
        fuel_efficiency=85,
    ),
    "Honda": dict(
        manufacturer="Honda",   # fornece Red Bull + Racing Bulls
        power=84,               # regulamento 2026 penalizou-os
        driveability=80,
        reliability=86,
        fuel_efficiency=82,
    ),
}

# Mapeamento equipa -> fornecedor motor
TEAM_ENGINE = {
    "Mercedes":       "Mercedes",
    "Williams":       "Mercedes",
    "Aston Martin":   "Mercedes",   # mudança para 2026
    "Ferrari":        "Ferrari",
    "Haas":           "Ferrari",
    "McLaren":        "Mercedes",   # manteve Mercedes
    "Red Bull Racing":"Honda",
    "Racing Bulls":   "Honda",
    "Alpine":         "Mercedes",   # mudança para 2026 (saída da Renault)
    "Audi":           "Audi",       # motor próprio
    "Cadillac":       "Ferrari",    # acordo motor Ferrari
}


# ---------------------------------------------------------------------------
# CARROS — atributos do chassis (sem motor)
# Escala 1-100
# Ordem esperada 2026: Mercedes > Ferrari > McLaren > Red Bull > Racing Bulls
#                     > Alpine > Haas > Audi > Williams > Aston Martin > Cadillac
# ---------------------------------------------------------------------------
CARS = [
    # Formato: (team_name, season, chassis, aero, gearbox, brakes, reliability, fuel_efficiency_chassis)
    # Mercedes — chassi diferente com regulamento 2026, melhor pacote geral
    ("Mercedes",        2026, 95, 94, 88, 90, 89, 87),

    # Ferrari — MELHOR chassi da grelha, motor um passo atrás
    ("Ferrari",         2026, 98, 92, 86, 88, 86, 85),

    # McLaren — evoluiu muito, gearbox problemática (problemas reais 2024-25)
    ("McLaren",         2026, 92, 93, 74, 87, 84, 86),

    # Red Bull — dominador até 2025, motor Honda perdeu terreno
    ("Red Bull Racing", 2026, 90, 89, 88, 86, 87, 83),

    # Racing Bulls — irmã mais nova da Red Bull, bom chassi de base
    ("Racing Bulls",    2026, 78, 76, 85, 82, 85, 80),

    # Alpine — projecto novo com motor Mercedes, chassi médio-alto
    ("Alpine",          2026, 76, 78, 82, 80, 81, 79),

    # Haas — chassi competitivo com motor Ferrari, pouco desenvolvimento
    ("Haas",            2026, 74, 72, 80, 81, 79, 78),

    # Audi — primeiro ano, chassi promissor mas em desenvolvimento
    ("Audi",            2026, 72, 74, 78, 70, 72, 76),

    # Williams — progresso mas ainda midfield baixo
    ("Williams",        2026, 70, 71, 79, 76, 78, 75),

    # Aston Martin — queda acentuada face ao pico de 2023
    ("Aston Martin",    2026, 68, 66, 82, 78, 77, 74),

    # Cadillac — estreante, travões os piores, tudo em desenvolvimento
    ("Cadillac",        2026, 62, 63, 72, 55, 68, 70),
]


# ---------------------------------------------------------------------------
# PILOTOS — atributos individuais
# Escala 1-100 por métrica
# pace            = velocidade pura de qualificação (uma volta)
# racecraft       = gestão de corrida, ultrapassagens, defesa
# tyre_management = preservação de pneus (crítico com Pirellis 2026)
# wet_weather     = desempenho com chuva
# consistency     = regularidade ao longo da época
# experience      = anos e conhecimento acumulado
# fitness         = condição física (factor nas corridas longas)
# aggression      = agressividade nas corridas (pode causar acidentes)
# ---------------------------------------------------------------------------
DRIVERS = [
    # código, pace, racecraft, tyre_mgmt, wet, consistency, experience, fitness, aggression
    # ---- RED BULL ----
    ("VER", 99, 98, 91, 97, 95, 90, 95, 92),   # Verstappen — o melhor
    ("HAD", 82, 78, 76, 78, 74, 40, 84, 80),   # Hadjar — estreante promissor

    # ---- FERRARI ----
    ("HAM", 94, 95, 93, 96, 88, 99, 88, 78),   # Hamilton — veterano elite
    ("LEC", 96, 87, 82, 88, 84, 82, 90, 83),   # Leclerc — talento puro

    # ---- McLAREN ----
    ("NOR", 95, 92, 88, 90, 91, 78, 92, 80),   # Norris — top 3
    ("PIA", 89, 86, 91, 83, 87, 62, 90, 72),   # Piastri — técnico, bom nos pneus

    # ---- MERCEDES ----
    ("RUS", 91, 89, 86, 87, 89, 76, 91, 79),   # Russell — muito completo
    ("ANT", 86, 81, 80, 82, 79, 30, 88, 77),   # Antonelli — estreante talentoso

    # ---- ASTON MARTIN ----
    ("ALO", 90, 97, 90, 92, 86, 99, 82, 88),   # Alonso — lenda, crafty
    ("STR", 76, 74, 73, 79, 71, 72, 80, 74),   # Stroll — paga o lugar

    # ---- ALPINE ----
    ("GAS", 84, 83, 80, 85, 80, 78, 88, 82),   # Gasly — sólido
    ("COL", 78, 74, 72, 75, 72, 32, 86, 76),   # Colapinto — estreante

    # ---- HAAS ----
    ("OCO", 85, 82, 79, 83, 78, 80, 87, 83),   # Ocon — experiente
    ("BEA", 80, 77, 75, 76, 74, 36, 85, 79),   # Bearman — jovem promessa

    # ---- WILLIAMS ----
    ("ALB", 84, 85, 87, 82, 83, 76, 88, 78),   # Albon — grande gestor
    ("SAI", 92, 88, 89, 88, 90, 84, 91, 79),   # Sainz — muito completo

    # ---- AUDI ----
    ("HUL", 82, 84, 83, 84, 80, 88, 84, 80),   # Hülkenberg — experiente midfield
    ("BOR", 76, 73, 72, 74, 70, 28, 83, 75),   # Bortoleto — estreante

    # ---- RACING BULLS ----
    ("LAW", 83, 80, 78, 79, 77, 48, 87, 81),   # Lawson — a melhorar
    ("LIN", 77, 74, 73, 75, 71, 30, 85, 74),   # Lindblad — estreante

    # ---- CADILLAC ----
    ("PER", 84, 85, 88, 82, 82, 90, 82, 74),   # Pérez — experiente nos pneus
    ("BOT", 84, 82, 86, 83, 80, 90, 83, 68),   # Bottas — consistente
]


# ---------------------------------------------------------------------------
# DDL — criar tabelas se não existirem
# ---------------------------------------------------------------------------
DDL = """
CREATE TABLE IF NOT EXISTS engines (
    id                INTEGER PRIMARY KEY AUTOINCREMENT,
    manufacturer      TEXT    NOT NULL UNIQUE,
    power             INTEGER NOT NULL,  -- potência bruta 1-100
    driveability      INTEGER NOT NULL,  -- facilidade de utilização 1-100
    reliability       INTEGER NOT NULL,  -- fiabilidade 1-100
    fuel_efficiency   INTEGER NOT NULL   -- eficiência combustível 1-100
);

CREATE TABLE IF NOT EXISTS car_attributes (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    team_id             INTEGER NOT NULL REFERENCES teams(id),
    season              INTEGER NOT NULL,
    engine_id           INTEGER NOT NULL REFERENCES engines(id),
    chassis             INTEGER NOT NULL,  -- estrutura/rigidez 1-100
    aero                INTEGER NOT NULL,  -- pacote aerodinâmico 1-100
    gearbox             INTEGER NOT NULL,  -- caixa de velocidades 1-100
    brakes              INTEGER NOT NULL,  -- sistema de travagem 1-100
    reliability         INTEGER NOT NULL,  -- fiabilidade geral chassi 1-100
    fuel_efficiency     INTEGER NOT NULL,  -- eficiência combustível chassi 1-100
    UNIQUE(team_id, season)
);

CREATE TABLE IF NOT EXISTS driver_attributes (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    driver_id           INTEGER NOT NULL REFERENCES drivers(id) UNIQUE,
    pace                INTEGER NOT NULL,  -- velocidade pura 1-100
    racecraft           INTEGER NOT NULL,  -- inteligência de corrida 1-100
    tyre_management     INTEGER NOT NULL,  -- gestão de pneus 1-100
    wet_weather         INTEGER NOT NULL,  -- desempenho na chuva 1-100
    consistency         INTEGER NOT NULL,  -- regularidade 1-100
    experience          INTEGER NOT NULL,  -- experiência/anos 1-100
    fitness             INTEGER NOT NULL,  -- condição física 1-100
    aggression          INTEGER NOT NULL   -- agressividade 1-100
);
"""


def create_tables(cursor):
    cursor.executescript(DDL)
    print("  Tabelas criadas (ou já existentes).")


def inserir_motores(cursor):
    for eng in ENGINES.values():
        cursor.execute("""
            INSERT INTO engines (manufacturer, power, driveability, reliability, fuel_efficiency)
            VALUES (:manufacturer, :power, :driveability, :reliability, :fuel_efficiency)
            ON CONFLICT(manufacturer) DO UPDATE SET
                power           = excluded.power,
                driveability    = excluded.driveability,
                reliability     = excluded.reliability,
                fuel_efficiency = excluded.fuel_efficiency
        """, eng)
    print(f"  {len(ENGINES)} motores inseridos/actualizados.")


def inserir_carros(cursor):
    cursor.execute("SELECT id, name FROM teams")
    equipas = {nome: eid for eid, nome in cursor.fetchall()}

    cursor.execute("SELECT id, manufacturer FROM engines")
    motores = {mfr: eid for eid, mfr in cursor.fetchall()}

    inseridos = 0
    for (team_name, season, chassis, aero, gearbox, brakes, reliability, fuel_eff) in CARS:
        team_id = equipas.get(team_name)
        engine_supplier = TEAM_ENGINE.get(team_name)
        engine_id = motores.get(engine_supplier)

        if not team_id:
            print(f"  AVISO: equipa '{team_name}' não encontrada.")
            continue
        if not engine_id:
            print(f"  AVISO: motor '{engine_supplier}' não encontrado.")
            continue

        cursor.execute("""
            INSERT INTO car_attributes
                (team_id, season, engine_id, chassis, aero, gearbox, brakes, reliability, fuel_efficiency)
            VALUES (?,?,?,?,?,?,?,?,?)
            ON CONFLICT(team_id, season) DO UPDATE SET
                engine_id       = excluded.engine_id,
                chassis         = excluded.chassis,
                aero            = excluded.aero,
                gearbox         = excluded.gearbox,
                brakes          = excluded.brakes,
                reliability     = excluded.reliability,
                fuel_efficiency = excluded.fuel_efficiency
        """, (team_id, season, engine_id, chassis, aero, gearbox, brakes, reliability, fuel_eff))
        inseridos += 1

    print(f"  {inseridos} pacotes de carro inseridos/actualizados.")


def inserir_pilotos(cursor):
    cursor.execute("SELECT id, code FROM drivers")
    pilotos = {code: did for did, code in cursor.fetchall()}

    inseridos = 0
    ignorados = []
    for row in DRIVERS:
        code = row[0]
        attrs = row[1:]
        driver_id = pilotos.get(code)
        if not driver_id:
            ignorados.append(code)
            continue

        cursor.execute("""
            INSERT INTO driver_attributes
                (driver_id, pace, racecraft, tyre_management,
                 wet_weather, consistency, experience, fitness, aggression)
            VALUES (?,?,?,?,?,?,?,?,?)
            ON CONFLICT(driver_id) DO UPDATE SET
                pace            = excluded.pace,
                racecraft       = excluded.racecraft,
                tyre_management = excluded.tyre_management,
                wet_weather     = excluded.wet_weather,
                consistency     = excluded.consistency,
                experience      = excluded.experience,
                fitness         = excluded.fitness,
                aggression      = excluded.aggression
        """, (driver_id, *attrs))
        inseridos += 1

    print(f"  {inseridos} conjuntos de atributos de piloto inseridos/actualizados.")
    if ignorados:
        print(f"  Ignorados (não encontrados na BD): {ignorados}")


# ---------------------------------------------------------------------------
# RELATÓRIO — visão geral bonita no terminal
# ---------------------------------------------------------------------------

def mostrar_relatorio(cursor):
    VERDE  = "\033[92m"
    AMARELO= "\033[93m"
    RESET  = "\033[0m"

    def barra(val, largura=20):
        filled = int(val / 100 * largura)
        return "█" * filled + "░" * (largura - filled)

    def cor(val):
        if val >= 90: return VERDE
        if val >= 75: return AMARELO
        return RESET

    print("\n" + "=" * 72)
    print("  MOTORES 2026")
    print("=" * 72)
    cursor.execute("""
        SELECT manufacturer, power, driveability, reliability, fuel_efficiency
        FROM engines ORDER BY power DESC
    """)
    print(f"  {'Fornecedor':<12} {'Potência':>8} {'Resposta':>8} {'Fiab.':>6} {'Combust.':>8}")
    print("  " + "-" * 50)
    for mfr, pwr, drv, rel, fue in cursor.fetchall():
        overall = round((pwr + drv + rel + fue) / 4)
        c = cor(overall)
        print(f"  {c}{mfr:<12}{RESET}  {pwr:>6}/100   {drv:>5}/100  {rel:>4}/100   {fue:>5}/100  (média: {c}{overall}{RESET})")

    print("\n" + "=" * 72)
    print("  CARROS 2026  (chassi + motor combinados)")
    print("=" * 72)
    cursor.execute("""
        SELECT t.name, e.manufacturer,
               ca.chassis, ca.aero, ca.gearbox, ca.brakes,
               ca.reliability, e.power,
               ROUND((ca.chassis + ca.aero + ca.gearbox + ca.brakes +
                      ca.reliability + e.power + e.reliability) / 7.0) AS overall
        FROM car_attributes ca
        JOIN teams   t ON t.id  = ca.team_id
        JOIN engines e ON e.id  = ca.engine_id
        WHERE ca.season = 2026
        ORDER BY overall DESC
    """)
    print(f"  {'Pos':>3} {'Equipa':<20} {'Motor':<11} {'Chs':>4} {'Aero':>5} {'Cxv':>4} {'Trv':>4} {'Rel':>4} {'Mot':>4} {'OVR':>4}")
    print("  " + "-" * 68)
    for pos, (team, eng, chs, aero, gbox, brk, rel, mtr_pwr, ovr) in enumerate(cursor.fetchall(), 1):
        c = cor(int(ovr))
        nota = ""
        if gbox < 80: nota += " ⚠ CXV"
        if brk < 65:  nota += " ⚠ TRV"
        if rel < 75:  nota += " ⚠ REL"
        print(f"  {pos:>3}. {c}{team:<20}{RESET} {eng:<10}  {chs:>3}  {aero:>4}  {gbox:>3}  {brk:>3}  {rel:>3}  {mtr_pwr:>3}  {c}{int(ovr):>3}{RESET}{nota}")

    print("\n" + "=" * 72)
    print("  PILOTOS TITULARES 2026")
    print("=" * 72)
    cursor.execute("""
        SELECT d.code, d.first_name || ' ' || d.last_name,
               t.name,
               da.pace, da.racecraft, da.tyre_management, da.wet_weather,
               da.consistency, da.experience, da.fitness, da.aggression,
               ROUND((da.pace + da.racecraft + da.tyre_management + da.wet_weather +
                      da.consistency + da.experience + da.fitness) / 7.0) AS overall
        FROM driver_attributes da
        JOIN drivers  d ON d.id = da.driver_id
        JOIN contracts c ON c.driver_id = d.id
            AND c.season_start = 2026 AND c.person_type = 'driver'
        JOIN teams    t ON t.id = c.team_id
        ORDER BY overall DESC
    """)
    print(f"  {'Pos':>3} {'Piloto':<25} {'Equipa':<20} {'Pac':>4} {'RC':>4} {'Pnu':>4} {'Chu':>4} {'Cst':>4} {'Exp':>4} {'Fit':>4} {'OVR':>4}")
    print("  " + "-" * 82)
    for pos, row in enumerate(cursor.fetchall(), 1):
        code, nome, team, pac, rc, tyr, wet, cst, exp, fit, agg, ovr = row
        c = cor(int(ovr))
        print(f"  {pos:>3}. {c}{nome:<25}{RESET} {team:<20} {pac:>3}  {rc:>3}  {tyr:>3}  {wet:>3}  {cst:>3}  {exp:>3}  {fit:>3}  {c}{int(ovr):>3}{RESET}")

    print("\n  Legenda: Pac=Pace  RC=Racecraft  Pnu=Pneus  Chu=Chuva  Cst=Consistência  Exp=Experiência  Fit=Físico  OVR=Geral")
    print("  ⚠ = ponto fraco notável (baseado em dados reais 2025-26)")


def main():
    if not os.path.exists(DB_PATH):
        print("ERRO: f1_manager.db não encontrado. Corre primeiro o setup_db.py e add_contracts.py.")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = ON")

    print("A criar tabelas de atributos...")
    create_tables(cursor)

    print("A inserir motores...")
    inserir_motores(cursor)

    print("A inserir atributos de carros...")
    inserir_carros(cursor)

    print("A inserir atributos de pilotos...")
    inserir_pilotos(cursor)

    conn.commit()
    mostrar_relatorio(cursor)
    conn.close()

    print("\n✓ Atributos 2026 inseridos com sucesso.")
    print("Próximo passo: motor de simulação de corrida / qualificação")


if __name__ == "__main__":
    main()
