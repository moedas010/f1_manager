"""
F1 Manager 2026 — race_engine.py
Motor de simulação de corrida — com Qualifying Q1/Q2/Q3 real e estratégia.
"""

import sqlite3
import random
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "database", "f1_manager.db")


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def load_track_coords(circuit_id):
    """Carrega o traçado do circuito (coordenadas normalizadas 0-1000)."""
    conn = get_db()
    row = conn.execute(
        "SELECT track_x, track_y FROM circuit_coords WHERE circuit_id = ?",
        (circuit_id,)
    ).fetchone()
    conn.close()
    if row:
        import json
        return json.loads(row['track_x']), json.loads(row['track_y'])
    return [], []


def load_race_data(race_id):
    conn = get_db()

    race = conn.execute("""
        SELECT r.*, c.id as circuit_id, c.name as circuit_name, c.laps
        FROM races r JOIN circuits c ON c.id = r.circuit_id
        WHERE r.id = ?
    """, (race_id,)).fetchone()

    drivers = conn.execute("""
        SELECT d.id, d.first_name, d.last_name, d.code, d.number,
               t.id as team_id, t.name as team_name,
               da.pace, da.racecraft, da.consistency,
               da.wet_weather, da.tyre_management, da.experience,
               ca.chassis, ca.aero, ca.gearbox, ca.brakes, ca.reliability as car_reliability,
               e.power as engine_power, e.reliability as engine_reliability
        FROM contracts c
        JOIN drivers d ON d.id = c.driver_id
        JOIN teams t ON t.id = c.team_id
        JOIN driver_attributes da ON da.driver_id = d.id
        JOIN car_attributes ca ON ca.team_id = t.id
        LEFT JOIN engines e ON e.id = ca.engine_id
        WHERE c.season_start = 2026 AND c.person_type = 'driver'
        ORDER BY d.id
    """).fetchall()

    conn.close()

    # Fallback se não houver dados suficientes
    if not race:
        race = {"name": "Grand Prix", "circuit_name": "Circuito", "laps": 58}

    return dict(race) if not isinstance(race, dict) else race, [dict(d) for d in drivers]


def _car_score(d):
    engine = d.get('engine_power') or 75
    return (
        engine * 0.30 +
        (d.get('chassis') or 70) * 0.25 +
        (d.get('aero') or 70) * 0.20 +
        (d.get('gearbox') or 70) * 0.15 +
        (d.get('brakes') or 70) * 0.10
    )


def _driver_score(d):
    return (
        (d.get('pace') or 75) * 0.55 +
        (d.get('consistency') or 75) * 0.25 +
        (d.get('experience') or 60) * 0.20
    )


def _reliability(d):
    car_rel = d.get('car_reliability') or 80
    eng_rel = d.get('engine_reliability') or 80
    return (car_rel + eng_rel) / 2


def _quali_lap_time(d, noise_scale=1.0):
    """Calcula um tempo de volta de qualificação para um piloto (dict cru da BD)."""
    car = _car_score(d)
    driver = _driver_score(d)
    combined = car * 0.65 + driver * 0.35
    noise = random.gauss(0, max(combined * 0.025, 1) * noise_scale)
    final = combined + noise

    base_time = 90000
    lap_time_ms = base_time - (final / 100) * 8000 + random.gauss(0, 120 * noise_scale)
    return lap_time_ms, car


def _make_quali_result(d, lap_time_ms, car_score):
    return {
        'driver_id': d['id'],
        'code': d['code'],
        'name': f"{d['first_name']} {d['last_name']}",
        'team': d['team_name'],
        'team_id': d['team_id'],
        'number': d['number'],
        'quali_time': lap_time_ms,
        'pace': d.get('pace') or 75,
        'consistency': d.get('consistency') or 75,
        'tyre_mgmt': d.get('tyre_management') or 75,
        'reliability': _reliability(d),
        'car_score': car_score,
    }


def calculate_qualifying(drivers):
    """Compatibilidade retroativa: quali simples de sessão única (sem Q1/Q2/Q3)."""
    results = []
    for d in drivers:
        t, car = _quali_lap_time(d)
        results.append(_make_quali_result(d, t, car))
    results.sort(key=lambda x: x['quali_time'])
    for i, r in enumerate(results):
        r['grid'] = i + 1
    return results


def run_qualifying(drivers, q1_cut=15, q2_cut=10):
    """
    Simula a qualificação estilo F1: Q1 (todos), Q2 (top 15), Q3 (top 10).
    Cada sessão tem mais pressão (mais ruído/risco) que a anterior.
    Devolve dict com 'q1', 'q2', 'q3' (listas ordenadas) e 'grid' (grelha final).
    """

    def run_session(pool, noise_scale):
        results = []
        for d in pool:
            t, car = _quali_lap_time(d, noise_scale=noise_scale)
            results.append(_make_quali_result(d, t, car))
        results.sort(key=lambda x: x['quali_time'])
        return results

    # Q1 — todos os pilotos
    q1 = run_session(drivers, noise_scale=1.0)
    q1_advance = {r['code'] for r in q1[:q1_cut]}
    q1_eliminated = q1[q1_cut:]
    for i, r in enumerate(q1_eliminated):
        r['out_session'] = 'Q1'
        r['out_pos'] = q1_cut + i + 1

    # Q2 — quem passou o corte, mais um pouco de pressão
    q2_pool = [d for d in drivers if d['code'] in q1_advance]
    q2 = run_session(q2_pool, noise_scale=1.1)
    q2_advance = {r['code'] for r in q2[:q2_cut]}
    q2_eliminated = q2[q2_cut:]
    for i, r in enumerate(q2_eliminated):
        r['out_session'] = 'Q2'
        r['out_pos'] = q2_cut + i + 1

    # Q3 — a luta pela pole, máxima pressão
    q3_pool = [d for d in drivers if d['code'] in q2_advance]
    q3 = run_session(q3_pool, noise_scale=1.25)
    for i, r in enumerate(q3):
        r['out_session'] = 'Q3'
        r['out_pos'] = i + 1

    # Grelha final: Q3 (1-10), depois eliminados do Q2 (11-15º), depois Q1 (16-20º)
    grid = []
    for r in q3:
        gr = dict(r)
        gr['grid'] = len(grid) + 1
        grid.append(gr)
    for r in q2_eliminated:
        gr = dict(r)
        gr['grid'] = len(grid) + 1
        grid.append(gr)
    for r in q1_eliminated:
        gr = dict(r)
        gr['grid'] = len(grid) + 1
        grid.append(gr)

    return {'q1': q1, 'q2': q2, 'q3': q3, 'grid': grid}


def format_gap(ms_diff):
    if ms_diff <= 0:
        return "LÍDER"
    s = ms_diff / 1000
    return f"+{s:.3f}s"


def format_laptime(ms):
    mins = int(ms // 60000)
    secs = (ms % 60000) / 1000
    return f"{mins}:{secs:06.3f}"


class RaceSimulator:
    TYRE_COMPOUNDS = {
        'S': {'degradation': 0.8,  'pace_bonus': 1.8, 'laps': 18},
        'M': {'degradation': 0.45, 'pace_bonus': 0.8, 'laps': 26},
        'H': {'degradation': 0.25, 'pace_bonus': 0.0, 'laps': 38},
    }

    # Margem de voltas antes do limite do composto em que cada modo de
    # estratégia decide entrar nas boxes, e probabilidade de undercut cedo.
    STRATEGY_MODES = {
        'aggressive':   {'margin': 4, 'early_pit_chance': 0.10},
        'balanced':     {'margin': 2, 'early_pit_chance': 0.07},
        'conservative': {'margin': 0, 'early_pit_chance': 0.04},
    }

    def __init__(self, race_id, player_team_id=None, dev_bonus=None, strategy=None):
        self.race_id = race_id
        self.player_team_id = player_team_id
        self.race_data, self.all_drivers = load_race_data(race_id)

        # Aplica os upgrades de Desenvolvimento da equipa do jogador aos atributos do carro
        if dev_bonus and player_team_id:
            for d in self.all_drivers:
                if d.get('team_id') == player_team_id:
                    d['chassis'] = min(99, (d.get('chassis') or 70) + dev_bonus.get('chassis', 0) * 0.2)
                    d['aero'] = min(99, (d.get('aero') or 70) + dev_bonus.get('aero', 0) * 0.2)
                    d['engine_power'] = min(99, (d.get('engine_power') or 75) + dev_bonus.get('engine', 0) * 0.2)
                    d['car_reliability'] = min(99, (d.get('car_reliability') or 80) + dev_bonus.get('reliability', 0) * 0.15)
                    d['engine_reliability'] = min(99, (d.get('engine_reliability') or 80) + dev_bonus.get('reliability', 0) * 0.15)

        self.total_laps = self.race_data.get('laps') or 58
        self.current_lap = 0
        self.safety_car = False
        self.safety_car_laps = 0

        circuit_id = self.race_data.get('circuit_id')
        self.track_x, self.track_y = load_track_coords(circuit_id) if circuit_id else ([], [])

        # Qualifying real: Q1 -> Q2 -> Q3
        self.quali_sessions = run_qualifying(self.all_drivers)
        self.standings = self.quali_sessions['grid']

        # strategy: { driver_id: {'tyre': 'S'|'M'|'H', 'mode': 'aggressive'|'balanced'|'conservative'} }
        self.strategy = strategy or {}
        self._init_car_states()

        self.fastest_lap = {'time': 999999, 'driver': None, 'lap': 0}

    def _init_car_states(self):
        """(Re)inicializa o estado dos carros a partir da estratégia definida."""
        self.car_states = {}
        for d in self.standings:
            strat = self.strategy.get(d['driver_id']) or self.strategy.get(str(d['driver_id'])) or {}
            start_tyre = strat.get('tyre', 'M')
            if start_tyre not in self.TYRE_COMPOUNDS:
                start_tyre = 'M'
            mode = strat.get('mode', 'balanced')
            if mode not in self.STRATEGY_MODES:
                mode = 'balanced'
            self.car_states[d['driver_id']] = {
                'tyre': start_tyre, 'tyre_age': 0, 'total_time': 0.0,
                'pit_stops': 0, 'retired': False, 'mode': mode,
                'force_pit': False, 'last_radio_lap': -99,
            }

    def apply_strategy(self, strategy):
        """Aplica a estratégia escolhida pelo jogador antes do início da corrida."""
        self.strategy = strategy or {}
        self._init_car_states()

    def radio_command(self, driver_id, action):
        """
        Aplica uma ordem do jogador dada em tempo real via rádio de equipa.
        action: 'box_now' | 'push' | 'conserve' | 'balanced' | 'stay_out'
        """
        try:
            driver_id = int(driver_id)
        except (TypeError, ValueError):
            return False
        state = self.car_states.get(driver_id)
        if not state or state['retired']:
            return False

        if action == 'box_now':
            state['force_pit'] = True
        elif action == 'stay_out':
            state['force_pit'] = False
        elif action == 'push':
            state['mode'] = 'aggressive'
        elif action == 'conserve':
            state['mode'] = 'conservative'
        elif action == 'balanced':
            state['mode'] = 'balanced'
        else:
            return False
        return True

    def _tyre_deg(self, driver, state):
        compound = state['tyre']
        age = state['tyre_age']
        base_deg = self.TYRE_COMPOUNDS[compound]['degradation']
        mgmt_factor = (100 - driver['tyre_mgmt']) / 100 * 0.5
        return (base_deg + mgmt_factor) * age * 0.12

    def _base_lap_time(self, driver, state):
        car = driver['car_score']
        pace = driver['pace']
        compound = state['tyre']
        pace_bonus = self.TYRE_COMPOUNDS[compound]['pace_bonus']

        base = 90000
        performance = ((car * 0.6 + pace * 0.4) / 100) * 8000
        deg_penalty = self._tyre_deg(driver, state) * 1000
        compound_bonus = pace_bonus * 1000

        lap = base - performance + deg_penalty - compound_bonus
        lap += random.gauss(0, 80)

        if self.safety_car:
            lap += 15000

        return max(lap, 68000)

    def _check_retirement(self, driver):
        reliability = driver['reliability']
        prob = (100 - reliability) / 100 * 0.0025
        return random.random() < prob

    def _should_pit(self, driver, state, lap):
        if state.get('force_pit'):
            return True
        compound = state['tyre']
        age = state['tyre_age']
        max_laps = self.TYRE_COMPOUNDS[compound]['laps']
        mode_cfg = self.STRATEGY_MODES.get(state.get('mode', 'balanced'), self.STRATEGY_MODES['balanced'])

        if age >= max_laps - mode_cfg['margin']:
            return True
        if state['pit_stops'] == 0 and lap > self.total_laps * 0.35:
            if random.random() < mode_cfg['early_pit_chance']:
                return True
        return False

    # ── RÁDIO DE EQUIPA ──────────────────────────────────────────
    RADIO_FLAVOR = [
        "Ritmo consistente, continua assim.",
        "Motor e travões dentro dos parâmetros normais.",
        "Boa volta. A diferença para a frente está a diminuir.",
        "Mantém a concentração, faltam poucas voltas de tensão.",
    ]

    def _generate_radio(self, driver, state, standings_rows_by_id, lap):
        """Gera mensagens de rádio para os pilotos do jogador, no máximo uma a cada 4 voltas."""
        if not self.player_team_id or driver['team_id'] != self.player_team_id:
            return None
        if lap - state['last_radio_lap'] < 4:
            return None

        compound = state['tyre']
        max_laps = self.TYRE_COMPOUNDS[compound]['laps']
        laps_left_tyre = max_laps - state['tyre_age']
        row = standings_rows_by_id.get(driver['driver_id'])

        # Pneus no limite — pede decisão
        if 0 < laps_left_tyre <= 3 and not state.get('force_pit'):
            state['last_radio_lap'] = lap
            return {
                'driver_id': driver['driver_id'], 'code': driver['code'], 'lap': lap,
                'msg': f"{driver['code']}, os pneus {compound} estão no limite. Queres entrar nas boxes?",
                'actionable': True,
                'options': [
                    {'label': 'BOX, BOX', 'action': 'box_now'},
                    {'label': 'Aguentar mais uma volta', 'action': 'stay_out'},
                ],
            }

        if row:
            gap_ahead = row.get('gap_to_ahead_ms')
            gap_behind = row.get('gap_to_behind_ms')
            # Carro à frente perto — oferece modo agressivo
            if gap_ahead is not None and gap_ahead < 1000 and state.get('mode') != 'aggressive':
                state['last_radio_lap'] = lap
                return {
                    'driver_id': driver['driver_id'], 'code': driver['code'], 'lap': lap,
                    'msg': f"{driver['code']}, estás a {gap_ahead/1000:.1f}s do carro da frente. Queres atacar?",
                    'actionable': True,
                    'options': [
                        {'label': 'Modo Agressivo', 'action': 'push'},
                        {'label': 'Manter ritmo', 'action': 'balanced'},
                    ],
                }
            # Carro atrás a pressionar — oferece modo defensivo
            if gap_behind is not None and gap_behind < 1000 and state.get('mode') != 'conservative':
                state['last_radio_lap'] = lap
                return {
                    'driver_id': driver['driver_id'], 'code': driver['code'], 'lap': lap,
                    'msg': f"{driver['code']}, carro atrás a {gap_behind/1000:.1f}s. Defender a posição?",
                    'actionable': True,
                    'options': [
                        {'label': 'Modo Conservador', 'action': 'conserve'},
                        {'label': 'Manter ritmo', 'action': 'balanced'},
                    ],
                }

        # Mensagem de ambiente, ocasional
        if random.random() < 0.12:
            state['last_radio_lap'] = lap
            return {
                'driver_id': driver['driver_id'], 'code': driver['code'], 'lap': lap,
                'msg': random.choice(self.RADIO_FLAVOR),
                'actionable': False, 'options': [],
            }
        return None

    def _choose_tyre(self, laps_remaining):
        if laps_remaining > 30:
            return random.choice(['M', 'H'])
        elif laps_remaining > 15:
            return random.choice(['M', 'S'])
        return 'S'

    def simulate_lap(self):
        self.current_lap += 1
        lap_events = []

        if not self.safety_car and self.current_lap > 3:
            if random.random() < 0.035:
                self.safety_car = True
                self.safety_car_laps = random.randint(3, 5)
                lap_events.append({'type': 'safety_car', 'lap': self.current_lap,
                                    'msg': f'SAFETY CAR — Incidente na pista · Volta {self.current_lap}'})

        if self.safety_car:
            self.safety_car_laps -= 1
            if self.safety_car_laps <= 0:
                self.safety_car = False
                lap_events.append({'type': 'green_flag', 'lap': self.current_lap,
                                    'msg': 'GREEN FLAG — Pista limpa'})

        active = [d for d in self.standings if not self.car_states[d['driver_id']]['retired']]

        for driver in active:
            state = self.car_states[driver['driver_id']]
            state['tyre_age'] += 1

            if self._check_retirement(driver) and self.current_lap > 5:
                state['retired'] = True
                lap_events.append({'type': 'retirement', 'lap': self.current_lap,
                                    'msg': f"ABANDONO — {driver['code']} · Problema mecânico"})
                continue

            pit_this_lap = False
            laps_remaining = self.total_laps - self.current_lap
            if self._should_pit(driver, state, self.current_lap) and laps_remaining > 5:
                old_tyre = state['tyre']
                new_tyre = self._choose_tyre(laps_remaining)
                state['tyre'] = new_tyre
                state['tyre_age'] = 0
                state['pit_stops'] += 1
                state['force_pit'] = False
                pit_this_lap = True
                lap_events.append({'type': 'pit_stop', 'lap': self.current_lap,
                                    'msg': f"PIT STOP — {driver['code']} · {old_tyre} → {new_tyre}"})

            lap_ms = self._base_lap_time(driver, state)
            if pit_this_lap:
                lap_ms += random.randint(20000, 23000)

            state['total_time'] += lap_ms

            if lap_ms < self.fastest_lap['time'] and not pit_this_lap:
                self.fastest_lap = {'time': lap_ms, 'driver': driver['code'], 'lap': self.current_lap}
                if self.current_lap > self.total_laps * 0.5:
                    lap_events.append({'type': 'fastest_lap', 'lap': self.current_lap,
                                        'msg': f"FASTEST LAP — {driver['code']} · {format_laptime(lap_ms)}"})

        result_rows = []
        active_list = [d for d in self.standings if not self.car_states[d['driver_id']]['retired']]
        active_list.sort(key=lambda d: self.car_states[d['driver_id']]['total_time'])
        leader_time = self.car_states[active_list[0]['driver_id']]['total_time'] if active_list else 0

        for pos, driver in enumerate(active_list, 1):
            state = self.car_states[driver['driver_id']]
            gap = state['total_time'] - leader_time
            result_rows.append({
                'pos': pos, 'driver_id': driver['driver_id'], 'code': driver['code'],
                'name': driver['name'], 'team': driver['team'], 'team_id': driver['team_id'],
                'number': driver['number'], 'tyre': state['tyre'], 'tyre_age': state['tyre_age'],
                'gap': format_gap(gap), 'gap_ms': gap, 'pit_stops': state['pit_stops'], 'retired': False,
            })

        retired_list = [d for d in self.standings if self.car_states[d['driver_id']]['retired']]
        for driver in retired_list:
            state = self.car_states[driver['driver_id']]
            result_rows.append({
                'pos': len(result_rows) + 1, 'driver_id': driver['driver_id'], 'code': driver['code'],
                'name': driver['name'], 'team': driver['team'], 'team_id': driver['team_id'],
                'number': driver['number'], 'tyre': state['tyre'], 'tyre_age': state['tyre_age'],
                'gap': 'OUT', 'gap_ms': 9999999, 'pit_stops': state['pit_stops'], 'retired': True,
            })

        # Gap ao carro imediatamente à frente/atrás (para o rádio de equipa)
        for i, row in enumerate(result_rows):
            if row['retired']:
                continue
            row['gap_to_ahead_ms'] = (row['gap_ms'] - result_rows[i - 1]['gap_ms']) if i > 0 and not result_rows[i - 1]['retired'] else None
            nxt = result_rows[i + 1] if i + 1 < len(result_rows) else None
            row['gap_to_behind_ms'] = (nxt['gap_ms'] - row['gap_ms']) if nxt and not nxt['retired'] else None

        standings_rows_by_id = {r['driver_id']: r for r in result_rows}
        radio_messages = []
        for driver in active:
            state = self.car_states[driver['driver_id']]
            if state['retired']:
                continue
            msg = self._generate_radio(driver, state, standings_rows_by_id, self.current_lap)
            if msg:
                radio_messages.append(msg)

        # Posição de cada carro no traçado (baseado no gap ao líder)
        if self.track_x:
            track_len = len(self.track_x)
            for r in result_rows:
                if r['retired']:
                    r['track_pos'] = None
                    continue
                # Gap em segundos → fração de volta atrás do líder (~90s por volta)
                laps_behind = min(r['gap_ms'] / 90000, 0.95)
                progress = (1 - laps_behind) % 1.0
                idx = int(progress * track_len) % track_len
                r['track_pos'] = {'x': self.track_x[idx], 'y': self.track_y[idx]}

        return {
            'lap': self.current_lap, 'total_laps': self.total_laps,
            'standings': result_rows, 'events': lap_events, 'radio': radio_messages,
            'safety_car': self.safety_car, 'fastest_lap': self.fastest_lap,
            'finished': self.current_lap >= self.total_laps,
        }

    def get_final_points(self, standings):
        points_map = {1: 25, 2: 18, 3: 15, 4: 12, 5: 10, 6: 8, 7: 6, 8: 4, 9: 2, 10: 1}
        results = []
        for r in standings:
            pts = points_map.get(r['pos'], 0)
            if r['code'] == self.fastest_lap['driver'] and r['pos'] <= 10:
                pts += 1
            results.append({**r, 'points': pts})
        return results