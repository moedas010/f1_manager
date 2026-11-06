import fastf1

session = fastf1.get_session(2025, "Monza", "R")
session.load(telemetry=False, weather=False, messages=False)

circuit = session.get_circuit_info()
print(circuit)
