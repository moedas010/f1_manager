"""
F1 Manager 2026 — race_server.py
Servidor WebSocket que liga o motor de simulação ao HTML.
"""

import asyncio
import websockets
import json
import sys
import os
import traceback

sys.path.insert(0, os.path.dirname(__file__))
from race_engine import RaceSimulator


async def run_race(websocket, race_id, player_team_id, state, dev_bonus=None):
    try:
        simulator = RaceSimulator(race_id, player_team_id, dev_bonus)
    except Exception as e:
        traceback.print_exc()
        await websocket.send(json.dumps({'type': 'error', 'msg': f'Erro ao carregar corrida: {str(e)}'}))
        return

    state['simulator'] = simulator

    if not simulator.standings:
        await websocket.send(json.dumps({
            'type': 'error',
            'msg': 'Nenhum piloto encontrado. Verifica se os contratos e atributos de 2026 estão na base de dados.'
        }))
        return

    # ── QUALIFYING: envia Q1, Q2 e Q3 — cada sessão espera o jogador clicar "Continuar" ──
    qs = simulator.quali_sessions

    async def wait_continue():
        state['quali_event'] = asyncio.Event()
        try:
            await asyncio.wait_for(state['quali_event'].wait(), timeout=120)
        except asyncio.TimeoutError:
            pass

    await websocket.send(json.dumps({
        'type': 'quali_session', 'session': 'Q1', 'results': qs['q1'],
        'race_name': simulator.race_data.get('name') or 'Grand Prix',
        'circuit': simulator.race_data.get('circuit_name') or '',
    }))
    await wait_continue()

    await websocket.send(json.dumps({'type': 'quali_session', 'session': 'Q2', 'results': qs['q2']}))
    await wait_continue()

    await websocket.send(json.dumps({'type': 'quali_session', 'session': 'Q3', 'results': qs['q3']}))
    await wait_continue()

    quali = {
        'type': 'qualifying',
        'grid': simulator.standings,
        'race_name': simulator.race_data.get('name') or 'Grand Prix',
        'circuit': simulator.race_data.get('circuit_name') or '',
        'total_laps': simulator.total_laps,
        'track_x': simulator.track_x,
        'track_y': simulator.track_y,
        'player_team_id': player_team_id,
    }
    await websocket.send(json.dumps(quali))

    # ── ESTRATÉGIA: espera o jogador definir os pneus/plano antes da corrida ──
    await websocket.send(json.dumps({'type': 'await_strategy'}))
    try:
        await asyncio.wait_for(state['strategy_event'].wait(), timeout=180)
    except asyncio.TimeoutError:
        pass  # segue com estratégia por defeito (M, balanced) se o jogador não responder

    simulator.apply_strategy(state.get('strategy'))

    await websocket.send(json.dumps({'type': 'lights_out'}))

    last_result = None
    try:
        while simulator.current_lap < simulator.total_laps:
            result = simulator.simulate_lap()
            last_result = result
            await websocket.send(json.dumps({'type': 'lap', **result}))
            if result['finished']:
                break
            await asyncio.sleep(max(0.3, state['delay']))

        final_standings = last_result['standings'] if last_result else []
        final = simulator.get_final_points([r for r in final_standings if not r['retired']])
        await websocket.send(json.dumps({
            'type': 'race_over',
            'results': final,
            'fastest_lap': simulator.fastest_lap,
        }))
    except Exception as e:
        traceback.print_exc()
        await websocket.send(json.dumps({'type': 'error', 'msg': f'Erro durante a corrida: {str(e)}'}))


async def handle(websocket):
    print("[WS] Cliente conectado")
    state = {'delay': 3.5, 'strategy_event': asyncio.Event(), 'strategy': None, 'quali_event': asyncio.Event()}
    race_task = None

    try:
        async for message in websocket:
            data = json.loads(message)
            cmd = data.get('cmd')

            if cmd == 'start_race':
                race_id = data.get('race_id', 1)
                player_team_id = data.get('player_team_id')
                dev_bonus = data.get('dev_bonus')
                state['delay'] = max(0.3, data.get('speed', 3.5))
                state['strategy_event'] = asyncio.Event()
                state['strategy'] = None
                race_task = asyncio.create_task(run_race(websocket, race_id, player_team_id, state, dev_bonus))

            elif cmd == 'quali_continue':
                ev = state.get('quali_event')
                if ev:
                    ev.set()

            elif cmd == 'set_strategy':
                # data['strategy'] = { driver_id(str): {'tyre': 'S'|'M'|'H', 'mode': '...'} }
                state['strategy'] = data.get('strategy') or {}
                state['strategy_event'].set()

            elif cmd == 'radio_command':
                sim = state.get('simulator')
                if sim:
                    sim.radio_command(data.get('driver_id'), data.get('action'))

            elif cmd == 'set_speed':
                state['delay'] = max(0.3, data.get('speed', 3.5))

            elif cmd == 'ping':
                await websocket.send(json.dumps({'type': 'pong'}))

    except websockets.exceptions.ConnectionClosed:
        print("[WS] Cliente desconectado")
    except Exception as e:
        traceback.print_exc()
    finally:
        if race_task and not race_task.done():
            race_task.cancel()


async def main():
    print("[WS] Servidor a correr em ws://localhost:8765")
    async with websockets.serve(handle, "localhost", 8765):
        await asyncio.Future()


if __name__ == "__main__":
    asyncio.run(main())