import requests
import os

SIM_URL = os.getenv("SIMULATION_URL")
AI_URL = os.getenv("AI_URL")


def get_simulation_data():
    try:
        vehicles = requests.get(f"{SIM_URL}/simulation/vehicles", timeout=5).json()
        traffic = requests.get(f"{SIM_URL}/simulation/traffic-lights", timeout=5).json()

        return {
            "vehicles": vehicles,
            "traffic_lights": traffic
        }

    except Exception as e:
        return {"error": f"Simulation error: {str(e)}"}


def get_ai_prediction(sim_data):
    try:
        response = requests.post(
            f"{AI_URL}/predict",
            json=sim_data,
            timeout=5
        )
        return response.json()

    except Exception as e:
        return {"error": f"AI error: {str(e)}"}