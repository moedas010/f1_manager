"""
F1 Manager — setup_finances.py
Sistema financeiro completo para a época 2026.

ESTRUTURA:
  - finances         : orçamento base e tetos por equipa/época
  - finance_revenue  : receitas por categoria (prize money, patrocinadores, etc.)
  - finance_expenses : gastos por categoria (carro, staff, operações)
  - sponsors         : patrocinadores reais por equipa

TETOS DE CUSTO (FIA 2026):
  - Cost Cap global       : $215M  (tudo incluído)
  - Technical cost cap    : $145M  (apenas custos técnicos: carro + aero + eng.)

DADOS REAIS:
  - Prize money baseado em resultados do Campeonato de Construtores 2025
    (McLaren 1º, Mercedes 2º, Red Bull 3º, Ferrari 4º, Williams 5º, ...)
  - Patrocinadores reais: Oracle/Red Bull ($110M), HP/Ferrari ($100M),
    Mastercard/McLaren ($90M), Petronas/Mercedes ($80M), Aramco/Aston Martin ($75M)
  - Receitas estimadas: Sportico, RacingNews365, The-Race (Set 2026)
"""

import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "f1_manager.db")

# ---------------------------------------------------------------------------
# DDL
# ---------------------------------------------------------------------------
DDL = """
DROP TABLE IF EXISTS sponsors;
DROP TABLE IF EXISTS finance_expenses;
DROP TABLE IF EXISTS finance_revenue;
DROP TABLE IF EXISTS finances;

-- Orçamento base e tetos por equipa/época
CREATE TABLE finances (
    id                      INTEGER PRIMARY KEY AUTOINCREMENT,
    team_id                 INTEGER NOT NULL REFERENCES teams(id),
    season                  INTEGER NOT NULL,

    -- Tetos FIA
    cost_cap_global         INTEGER NOT NULL DEFAULT 215000000,  -- $215M
    cost_cap_technical      INTEGER NOT NULL DEFAULT 145000000,  -- $145M

    -- Resumo financeiro (calculado no fim da época)
    total_revenue           INTEGER NOT NULL DEFAULT 0,
    total_expenses          INTEGER NOT NULL DEFAULT 0,
    balance                 INTEGER NOT NULL DEFAULT 0,   -- revenue - expenses
    cash_reserve            INTEGER NOT NULL DEFAULT 0,   -- reserva inicial

    UNIQUE(team_id, season)
);

-- Receitas por categoria
CREATE TABLE finance_revenue (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    team_id         INTEGER NOT NULL REFERENCES teams(id),
    season          INTEGER NOT NULL,
    category        TEXT NOT NULL,  -- 'prize_money','sponsorship','merchandising','manufacturer','other'
    amount          INTEGER NOT NULL,
    notes           TEXT
);

-- Gastos por categoria
CREATE TABLE finance_expenses (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    team_id         INTEGER NOT NULL REFERENCES teams(id),
    season          INTEGER NOT NULL,
    category        TEXT NOT NULL,  -- 'car_development','staff_salaries','operations','travel','facilities','marketing'
    amount          INTEGER NOT NULL,
    counts_technical INTEGER NOT NULL DEFAULT 0,  -- 1 = conta para o teto técnico
    notes           TEXT
);

-- Patrocinadores
CREATE TABLE sponsors (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    team_id         INTEGER NOT NULL REFERENCES teams(id),
    name            TEXT NOT NULL,
    tier            TEXT NOT NULL,  -- 'title','principal','official','supplier'
    annual_value    INTEGER NOT NULL,
    season_start    INTEGER NOT NULL,
    season_end      INTEGER NOT NULL,
    category        TEXT,           -- 'technology','energy','finance','automotive',...
    logo_url        TEXT
);
"""

# ---------------------------------------------------------------------------
# PRIZE MONEY 2026
# Baseado nos resultados do Campeonato de Construtores 2025:
# 1º McLaren, 2º Mercedes, 3º Red Bull, 4º Ferrari, 5º Williams,
# 6º Racing Bulls, 7º Aston Martin, 8º Haas, 9º Sauber→Audi, 10º Alpine
# Cadillac estreante → recebe pagamento mínimo de novo entrant ($40M)
# Fontes: aol.com/f1-prize-money, driverdb.com, sportico.com (Set 2026)
# ---------------------------------------------------------------------------
PRIZE_MONEY_2026 = {
    # Posição 2025 → prize money 2026 (aprox. $9M por posição, base $140M para 1º)
    "McLaren":          140_000_000,   # 1º 2025
    "Mercedes":         131_000_000,   # 2º 2025
    "Red Bull Racing":  122_000_000,   # 3º 2025
    "Ferrari":          113_000_000,   # 4º 2025
    "Williams":         104_000_000,   # 5º 2025
    "Racing Bulls":      95_000_000,   # 6º 2025
    "Aston Martin":      87_000_000,   # 7º 2025
    "Haas":              78_000_000,   # 8º 2025
    "Audi":              69_000_000,   # 9º 2025 (ex-Sauber/Kick)
    "Alpine":            60_000_000,   # 10º 2025
    "Cadillac":          40_000_000,   # estreante — pagamento de novo entrant
}

# ---------------------------------------------------------------------------
# PATROCINADORES REAIS 2026
# Formato: (equipa, nome, tier, valor_anual, época_início, época_fim, categoria)
# Fontes: RacingNews365, The-Race, Crash.net, Sportico (Set 2026)
# ---------------------------------------------------------------------------
SPONSORS_DATA = [
    # ══ RED BULL RACING ══
    ("Red Bull Racing", "Oracle",           "title",     110_000_000, 2026, 2028, "technology"),
    ("Red Bull Racing", "Red Bull",         "principal",  35_000_000, 2026, 2030, "energy"),
    ("Red Bull Racing", "Ford",             "principal",  25_000_000, 2026, 2030, "automotive"),
    ("Red Bull Racing", "Visa",             "official",   15_000_000, 2026, 2027, "finance"),
    ("Red Bull Racing", "Bybit",            "official",   12_000_000, 2026, 2027, "crypto"),
    ("Red Bull Racing", "ExxonMobil",       "supplier",    8_000_000, 2026, 2027, "energy"),
    ("Red Bull Racing", "Pirelli",          "supplier",    3_000_000, 2026, 2026, "automotive"),

    # ══ FERRARI ══
    ("Ferrari",         "HP",               "title",     100_000_000, 2026, 2028, "technology"),
    ("Ferrari",         "Shell",            "principal",  50_000_000, 2026, 2030, "energy"),
    ("Ferrari",         "Santander",        "principal",  30_000_000, 2026, 2028, "finance"),
    ("Ferrari",         "Ray-Ban",          "official",   15_000_000, 2026, 2027, "lifestyle"),
    ("Ferrari",         "Lenovo",           "official",   12_000_000, 2026, 2027, "technology"),
    ("Ferrari",         "Velas",            "official",    8_000_000, 2026, 2027, "crypto"),
    ("Ferrari",         "Pirelli",          "supplier",    3_000_000, 2026, 2026, "automotive"),

    # ══ McLAREN ══
    ("McLaren",         "Mastercard",       "title",      90_000_000, 2026, 2028, "finance"),
    ("McLaren",         "OKX",              "principal",  35_000_000, 2026, 2027, "crypto"),
    ("McLaren",         "Dell Technologies","principal",  20_000_000, 2026, 2027, "technology"),
    ("McLaren",         "Splunk",           "official",   12_000_000, 2026, 2027, "technology"),
    ("McLaren",         "Huski Chocolate",  "official",    5_000_000, 2026, 2027, "food"),
    ("McLaren",         "Google",           "official",   18_000_000, 2026, 2028, "technology"),
    ("McLaren",         "Pirelli",          "supplier",    3_000_000, 2026, 2026, "automotive"),

    # ══ MERCEDES ══
    ("Mercedes",        "Petronas",         "title",      80_000_000, 2026, 2030, "energy"),
    ("Mercedes",        "INEOS",            "principal",  35_000_000, 2026, 2028, "energy"),
    ("Mercedes",        "Adidas",           "principal",  25_000_000, 2026, 2028, "apparel"),
    ("Mercedes",        "CrowdStrike",      "official",   20_000_000, 2026, 2028, "technology"),
    ("Mercedes",        "Microsoft",        "official",   18_000_000, 2026, 2027, "technology"),
    ("Mercedes",        "Meta AI",          "official",   12_000_000, 2026, 2027, "technology"),
    ("Mercedes",        "Nasdaq",           "official",   10_000_000, 2026, 2027, "finance"),
    ("Mercedes",        "Pirelli",          "supplier",    3_000_000, 2026, 2026, "automotive"),

    # ══ ASTON MARTIN ══
    ("Aston Martin",    "Aramco",           "title",      75_000_000, 2026, 2030, "energy"),
    ("Aston Martin",    "Honda",            "principal",  20_000_000, 2026, 2030, "automotive"),
    ("Aston Martin",    "Cognizant",        "official",   10_000_000, 2026, 2027, "technology"),
    ("Aston Martin",    "Puma",             "official",    8_000_000, 2026, 2027, "apparel"),
    ("Aston Martin",    "Pirelli",          "supplier",    3_000_000, 2026, 2026, "automotive"),

    # ══ ALPINE ══
    ("Alpine",          "BWT",              "title",      25_000_000, 2026, 2027, "technology"),
    ("Alpine",          "Renault",          "principal",  15_000_000, 2026, 2027, "automotive"),
    ("Alpine",          "Castrol",          "official",    8_000_000, 2026, 2027, "energy"),
    ("Alpine",          "Pirelli",          "supplier",    3_000_000, 2026, 2026, "automotive"),

    # ══ HAAS ══
    ("Haas",            "MoneyGram",        "title",      20_000_000, 2026, 2027, "finance"),
    ("Haas",            "Toyota GR",        "principal",  15_000_000, 2026, 2028, "automotive"),
    ("Haas",            "Alpinestars",      "official",    5_000_000, 2026, 2027, "apparel"),
    ("Haas",            "Pirelli",          "supplier",    3_000_000, 2026, 2026, "automotive"),

    # ══ WILLIAMS ══
    ("Williams",        "Atlassian",        "title",      30_000_000, 2026, 2028, "technology"),
    ("Williams",        "Gulf Oil",         "principal",  12_000_000, 2026, 2027, "energy"),
    ("Williams",        "Duracell",         "official",    8_000_000, 2026, 2027, "technology"),
    ("Williams",        "Pirelli",          "supplier",    3_000_000, 2026, 2026, "automotive"),

    # ══ AUDI ══
    ("Audi",            "Audi AG",          "principal",  40_000_000, 2026, 2030, "automotive"),
    ("Audi",            "Castrol",          "official",    8_000_000, 2026, 2027, "energy"),
    ("Audi",            "SAP",              "official",   10_000_000, 2026, 2028, "technology"),
    ("Audi",            "Pirelli",          "supplier",    3_000_000, 2026, 2026, "automotive"),

    # ══ RACING BULLS ══
    ("Racing Bulls",    "Visa",             "title",      15_000_000, 2026, 2027, "finance"),
    ("Racing Bulls",    "Cash App",         "principal",  10_000_000, 2026, 2027, "finance"),
    ("Racing Bulls",    "Red Bull",         "official",    5_000_000, 2026, 2026, "energy"),
    ("Racing Bulls",    "Pirelli",          "supplier",    3_000_000, 2026, 2026, "automotive"),

    # ══ CADILLAC ══
    ("Cadillac",        "General Motors",   "principal",  30_000_000, 2026, 2030, "automotive"),
    ("Cadillac",        "Cadillac",         "title",      20_000_000, 2026, 2030, "automotive"),
    ("Cadillac",        "Goodyear",         "official",    5_000_000, 2026, 2027, "automotive"),
    ("Cadillac",        "Pirelli",          "supplier",    3_000_000, 2026, 2026, "automotive"),
]

# ---------------------------------------------------------------------------
# GASTOS POR CATEGORIA (estimativas realistas baseadas em dados públicos)
# counts_technical=1 → conta para o teto técnico de $145M
# ---------------------------------------------------------------------------
# Formato: (team, category, amount, counts_technical, notes)
EXPENSES_DATA = {
    "Mercedes": [
        ("car_development",  95_000_000, 1, "Chassi, aero, CFD, wind tunnel"),
        ("staff_salaries",   85_000_000, 0, "Todos os funcionários incl. pilotos"),
        ("operations",       18_000_000, 0, "Logística, transportes, hospitality"),
        ("travel",            8_000_000, 0, "24 GPs, voos, hotéis"),
        ("facilities",       12_000_000, 0, "Manutenção fábrica Brackley"),
        ("marketing",         8_000_000, 0, "Comunicação, media, eventos"),
    ],
    "Ferrari": [
        ("car_development",  90_000_000, 1, "Chassi, aero, motor Ferrari"),
        ("staff_salaries",   88_000_000, 0, "Incl. Hamilton $60M + Leclerc $34M"),
        ("operations",       17_000_000, 0, "Logística e hospitality Maranello"),
        ("travel",            8_000_000, 0, "24 GPs"),
        ("facilities",       14_000_000, 0, "Maranello — expansão 2025"),
        ("marketing",        10_000_000, 0, "Ferrari brand — eventos mundiais"),
    ],
    "McLaren": [
        ("car_development",  88_000_000, 1, "Campeão em defesa — máx investimento"),
        ("staff_salaries",   75_000_000, 0, "Norris $30M + Piastri $13M + staff"),
        ("operations",       16_000_000, 0, "Woking operations"),
        ("travel",            8_000_000, 0, "24 GPs"),
        ("facilities",       12_000_000, 0, "MTC Woking"),
        ("marketing",         8_000_000, 0, "Campanha defesa de título"),
    ],
    "Red Bull Racing": [
        ("car_development",  92_000_000, 1, "Incl. custos motor Red Bull Ford"),
        ("staff_salaries",   80_000_000, 0, "Verstappen $70M + Hadjar $5M + staff"),
        ("operations",       18_000_000, 0, "Milton Keynes"),
        ("travel",            8_000_000, 0, "24 GPs"),
        ("facilities",       15_000_000, 0, "Nova fábrica motor RBF"),
        ("marketing",         9_000_000, 0, "Red Bull brand global"),
    ],
    "Aston Martin": [
        ("car_development",  82_000_000, 1, "Newey no comando — grande investimento"),
        ("staff_salaries",   65_000_000, 0, "Newey $15M + Alonso $20M + staff"),
        ("operations",       14_000_000, 0, "Silverstone"),
        ("travel",            8_000_000, 0, "24 GPs"),
        ("facilities",       18_000_000, 0, "Novo complexo Silverstone 2025"),
        ("marketing",         7_000_000, 0, "Aston Martin brand"),
    ],
    "Williams": [
        ("car_development",  68_000_000, 1, "Boa evolução com Mercedes power"),
        ("staff_salaries",   40_000_000, 0, "Sainz $13M + Albon $8M + staff"),
        ("operations",       12_000_000, 0, "Grove"),
        ("travel",            7_000_000, 0, "24 GPs"),
        ("facilities",        8_000_000, 0, "Grove — upgrade wind tunnel"),
        ("marketing",         5_000_000, 0, "Williams Racing brand"),
    ],
    "Alpine": [
        ("car_development",  65_000_000, 1, "Motor Mercedes cliente — poupança"),
        ("staff_salaries",   35_000_000, 0, "Gasly $12M + Colapinto $3M + staff"),
        ("operations",       12_000_000, 0, "Enstone"),
        ("travel",            7_000_000, 0, "24 GPs"),
        ("facilities",        9_000_000, 0, "Enstone factory"),
        ("marketing",         5_000_000, 0, "Alpine brand"),
    ],
    "Haas": [
        ("car_development",  55_000_000, 1, "Modelo Haas: compra peças Ferrari"),
        ("staff_salaries",   28_000_000, 0, "Ocon $7M + Bearman $2M + staff"),
        ("operations",       10_000_000, 0, "Kannapolis + Banbury"),
        ("travel",            7_000_000, 0, "24 GPs"),
        ("facilities",        6_000_000, 0, "Dual-base USA/UK"),
        ("marketing",         4_000_000, 0, "Haas F1 brand"),
    ],
    "Audi": [
        ("car_development",  75_000_000, 1, "Primeiro ano — motor Audi novo"),
        ("staff_salaries",   35_000_000, 0, "Hülkenberg $6M + Bortoleto $2M + staff"),
        ("operations",       13_000_000, 0, "Hinwil factory"),
        ("travel",            7_000_000, 0, "24 GPs"),
        ("facilities",       20_000_000, 0, "Novo campus Hinwil + Neuburg motor"),
        ("marketing",         8_000_000, 0, "Audi AG brand launch"),
    ],
    "Racing Bulls": [
        ("car_development",  58_000_000, 1, "Chassi independente de RB"),
        ("staff_salaries",   22_000_000, 0, "Lawson $3M + Lindblad $1M + staff"),
        ("operations",        9_000_000, 0, "Faenza Italy"),
        ("travel",            7_000_000, 0, "24 GPs"),
        ("facilities",        5_000_000, 0, "Faenza factory"),
        ("marketing",         3_000_000, 0, "VCARB brand"),
    ],
    "Cadillac": [
        ("car_development",  50_000_000, 1, "Estreante — chassi base, motor Ferrari"),
        ("staff_salaries",   28_000_000, 0, "Bottas $5M + Pérez $5M + staff"),
        ("operations",       12_000_000, 0, "Indianapolis + Silverstone ops"),
        ("travel",            7_000_000, 0, "24 GPs"),
        ("facilities",       22_000_000, 0, "Novo complexo Indianapolis + Silverstone"),
        ("marketing",        10_000_000, 0, "GM/Cadillac brand launch F1"),
    ],
}

# Merchandising e outras receitas estimadas por equipa
MERCHANDISING = {
    "Mercedes":          45_000_000,
    "Ferrari":           55_000_000,   # maior marca de merch em F1
    "McLaren":           35_000_000,
    "Red Bull Racing":   40_000_000,
    "Aston Martin":      18_000_000,
    "Williams":          12_000_000,
    "Alpine":            10_000_000,
    "Haas":               6_000_000,
    "Audi":               8_000_000,
    "Racing Bulls":       7_000_000,
    "Cadillac":           5_000_000,
}

# Receitas de fabricante (works teams recebem suporte do fabricante)
MANUFACTURER_SUPPORT = {
    "Mercedes":          50_000_000,   # Mercedes-Benz AG suporte
    "Ferrari":           60_000_000,   # Ferrari SpA suporte directo
    "McLaren":                    0,   # cliente
    "Red Bull Racing":   30_000_000,   # Ford suporte motor
    "Aston Martin":      25_000_000,   # Honda suporte works
    "Williams":                   0,
    "Alpine":                     0,
    "Haas":                       0,
    "Audi":              50_000_000,   # Audi AG suporte total
    "Racing Bulls":               0,
    "Cadillac":          35_000_000,   # GM suporte
}

# Outras receitas (hospitality, IP, licenças, conferências)
OTHER_REVENUE = {
    "Mercedes":          20_000_000,
    "Ferrari":           25_000_000,
    "McLaren":           15_000_000,
    "Red Bull Racing":   18_000_000,
    "Aston Martin":      10_000_000,
    "Williams":           8_000_000,
    "Alpine":             6_000_000,
    "Haas":               4_000_000,
    "Audi":               5_000_000,
    "Racing Bulls":       3_000_000,
    "Cadillac":           3_000_000,
}


# ---------------------------------------------------------------------------
# FUNÇÕES
# ---------------------------------------------------------------------------

def create_tables(cursor):
    cursor.executescript(DDL)
    print("  Tabelas financeiras criadas.")


def get_teams(cursor):
    cursor.execute("SELECT id, name FROM teams")
    return {n: i for i, n in cursor.fetchall()}


def inserir_sponsors(cursor, teams):
    inseridos = 0
    for (team_name, name, tier, value, s_start, s_end, cat) in SPONSORS_DATA:
        team_id = teams.get(team_name)
        if not team_id:
            print(f"  AVISO: equipa '{team_name}' não encontrada.")
            continue
        initials = "".join(w[0] for w in name.split()[:2]).upper()
        logo = f"https://ui-avatars.com/api/?name={initials}&background=0d1117&color=ffffff&size=80"
        cursor.execute("""
            INSERT INTO sponsors
                (team_id, name, tier, annual_value, season_start, season_end, category, logo_url)
            VALUES (?,?,?,?,?,?,?,?)
        """, (team_id, name, tier, value, s_start, s_end, cat, logo))
        inseridos += 1
    print(f"  {inseridos} patrocinadores inseridos.")


def inserir_receitas_gastos(cursor, teams):
    total_fin = 0
    for team_name, team_id in teams.items():

        # ── Receitas ──────────────────────────────────────────────
        prize = PRIZE_MONEY_2026.get(team_name, 0)
        merch = MERCHANDISING.get(team_name, 0)
        manuf = MANUFACTURER_SUPPORT.get(team_name, 0)
        other = OTHER_REVENUE.get(team_name, 0)

        # Soma patrocinadores desta equipa
        cursor.execute("""
            SELECT COALESCE(SUM(annual_value), 0) FROM sponsors
            WHERE team_id = ? AND season_start <= 2026 AND season_end >= 2026
        """, (team_id,))
        sponsor_total = cursor.fetchone()[0]

        receitas = [
            ("prize_money",    prize,        f"Prize money 2026 (resultado 2025)"),
            ("sponsorship",    sponsor_total, "Total patrocinadores 2026"),
            ("merchandising",  merch,         "Merchandise, licenças, loja online"),
            ("manufacturer",   manuf,         "Suporte do fabricante/works team"),
            ("other",          other,         "Hospitality, IP, licenças, conferências"),
        ]
        total_rev = 0
        for cat, amount, notes in receitas:
            if amount > 0:
                cursor.execute("""
                    INSERT INTO finance_revenue (team_id, season, category, amount, notes)
                    VALUES (?,2026,?,?,?)
                """, (team_id, cat, amount, notes))
                total_rev += amount

        # ── Gastos ────────────────────────────────────────────────
        expenses = EXPENSES_DATA.get(team_name, [])
        total_exp = 0
        for cat, amount, tech, notes in expenses:
            cursor.execute("""
                INSERT INTO finance_expenses
                    (team_id, season, category, amount, counts_technical, notes)
                VALUES (?,2026,?,?,?,?)
            """, (team_id, cat, amount, tech, notes))
            total_exp += amount

        technical_spend = sum(a for _, a, t, _ in expenses if t == 1)
        balance = total_rev - total_exp

        # ── Resumo finances ───────────────────────────────────────
        cursor.execute("""
            INSERT INTO finances
                (team_id, season, cost_cap_global, cost_cap_technical,
                 total_revenue, total_expenses, balance, cash_reserve)
            VALUES (?,2026,215000000,145000000,?,?,?,?)
            ON CONFLICT(team_id,season) DO UPDATE SET
                total_revenue  = excluded.total_revenue,
                total_expenses = excluded.total_expenses,
                balance        = excluded.balance
        """, (team_id, total_rev, total_exp, balance, max(0, balance // 5)))

        total_fin += 1

    print(f"  {total_fin} registos financeiros inseridos.")


# ---------------------------------------------------------------------------
# RELATÓRIO
# ---------------------------------------------------------------------------

def mostrar_relatorio(cursor):
    VERDE  = "\033[92m"
    VERMELHO = "\033[91m"
    AMARELO= "\033[93m"
    AZUL   = "\033[94m"
    RESET  = "\033[0m"
    BOLD   = "\033[1m"

    def fmt(v):
        return f"${v/1_000_000:.1f}M"

    def cor_bal(v):
        return VERDE if v > 0 else VERMELHO

    print("\n" + "=" * 95)
    print(f"  {BOLD}FINANÇAS F1 2026 — VISÃO GERAL{RESET}")
    print("=" * 95)

    cursor.execute("""
        SELECT t.name,
               f.total_revenue, f.total_expenses, f.balance,
               f.cost_cap_global, f.cost_cap_technical,
               (SELECT COALESCE(SUM(amount),0) FROM finance_expenses
                WHERE team_id=t.id AND season=2026 AND counts_technical=1) AS tech_spend
        FROM finances f
        JOIN teams t ON t.id = f.team_id
        WHERE f.season = 2026
        ORDER BY f.total_revenue DESC
    """)

    print(f"\n  {'Equipa':<22} {'Receitas':>10} {'Gastos':>10} {'Saldo':>10}  {'Teto Global':>11}  {'Uso%':>5}  {'Teto Tec':>9}  {'UsoTec%':>7}")
    print("  " + "-" * 93)

    for team, rev, exp, bal, cap_g, cap_t, tech_sp in cursor.fetchall():
        uso_g   = exp / cap_g * 100
        uso_t   = tech_sp / cap_t * 100
        c_bal   = cor_bal(bal)
        c_uso_g = VERMELHO if uso_g > 95 else (AMARELO if uso_g > 85 else VERDE)
        c_uso_t = VERMELHO if uso_t > 95 else (AMARELO if uso_t > 85 else VERDE)
        print(
            f"  {team:<22} {AZUL}{fmt(rev):>10}{RESET} {fmt(exp):>10} "
            f"{c_bal}{fmt(bal):>10}{RESET}  "
            f"{fmt(cap_g):>11}  {c_uso_g}{uso_g:>4.1f}%{RESET}  "
            f"{fmt(cap_t):>9}  {c_uso_t}{uso_t:>6.1f}%{RESET}"
        )

    # Receitas por categoria
    print(f"\n{'=' * 95}")
    print(f"  {BOLD}RECEITAS POR CATEGORIA{RESET}")
    print(f"{'=' * 95}")
    print(f"\n  {'Equipa':<22} {'PrizeMoney':>11} {'Sponsor':>10} {'Merch':>8} {'Fab':>8} {'Outros':>8}  {'TOTAL':>10}")
    print("  " + "-" * 85)

    cursor.execute("SELECT id, name FROM teams ORDER BY name")
    all_teams = cursor.fetchall()
    for team_id, team_name in all_teams:
        cursor.execute("""
            SELECT category, amount FROM finance_revenue
            WHERE team_id = ? AND season = 2026
        """, (team_id,))
        rev_map = {cat: amt for cat, amt in cursor.fetchall()}
        if not rev_map:
            continue
        pm   = rev_map.get("prize_money", 0)
        sp   = rev_map.get("sponsorship", 0)
        me   = rev_map.get("merchandising", 0)
        mf   = rev_map.get("manufacturer", 0)
        ot   = rev_map.get("other", 0)
        tot  = pm + sp + me + mf + ot
        print(f"  {team_name:<22} {fmt(pm):>11} {fmt(sp):>10} {fmt(me):>8} {fmt(mf):>8} {fmt(ot):>8}  {AZUL}{fmt(tot):>10}{RESET}")

    # Maiores patrocinadores
    print(f"\n{'=' * 95}")
    print(f"  {BOLD}TOP 15 PATROCINADORES 2026{RESET}")
    print(f"{'=' * 95}")
    cursor.execute("""
        SELECT s.name, t.name, s.tier, s.category, s.annual_value
        FROM sponsors s
        JOIN teams t ON t.id = s.team_id
        WHERE s.season_start <= 2026 AND s.season_end >= 2026
          AND s.tier != 'supplier'
        ORDER BY s.annual_value DESC
        LIMIT 15
    """)
    for pos, (sname, team, tier, cat, val) in enumerate(cursor.fetchall(), 1):
        tier_label = {"title": "TITLE", "principal": "PRINC", "official": "OFFIC"}.get(tier, tier)
        print(f"  {pos:>2}. {BOLD}{sname:<18}{RESET} → {team:<22}  [{tier_label}]  {cat:<14}  {VERDE}{fmt(val)}{RESET}/ano")

    print(f"\n  {BOLD}Legenda:{RESET} Teto Global=$215M  Teto Técnico=$145M  {VERDE}verde=OK{RESET}  {AMARELO}amarelo=atenção{RESET}  {VERMELHO}vermelho=em risco{RESET}")


def main():
    if not os.path.exists(DB_PATH):
        print("ERRO: f1_manager.db não encontrado.")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = ON")

    print("A criar tabelas financeiras...")
    create_tables(cursor)

    teams = get_teams(cursor)

    print("A inserir patrocinadores...")
    inserir_sponsors(cursor, teams)

    print("A inserir receitas e gastos...")
    inserir_receitas_gastos(cursor, teams)

    conn.commit()
    mostrar_relatorio(cursor)
    conn.close()

    print("\n✓ Sistema financeiro 2026 inserido com sucesso.")
    print("Próximo passo: circuitos e calendário de corridas")


if __name__ == "__main__":
    main()
