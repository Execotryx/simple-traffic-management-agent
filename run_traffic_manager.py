from fastapi import FastAPI, HTTPException
from traffic_manager_agent import TrafficManagerAgent
import uvicorn
from pydantic import BaseModel
from typing import Dict
from models.traffic_data import TrafficData

app: FastAPI = FastAPI()
agent: TrafficManagerAgent = TrafficManagerAgent()

@app.get("/intersections")
def run_fetch_intersections():
    try:
        response = agent.fetch_intersections()
        return { "intersections": response }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/intersections/{intersection_id}")
def run_fetch_intersection(intersection_id: str):
    try:
        response = agent.fetch_intersection(intersection_id)
        if not response:
            raise HTTPException(status_code=404, detail="Intersection not found")
        return { "intersection": response }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/intersections/{intersection_id}/traffic_data")
def run_add_traffic_data(intersection_id: str, traffic_data: TrafficData):
    try:
        response = agent.add_traffic_data(
            intersection_id,
            traffic_data.traffic_density,
            traffic_data.light_timings
        )
        return {"id": response[0]['id']}
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid traffic density value")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/report")
def run_generate_traffic_report(traffic_density: float, intersection_name: str):
    try:
        response = agent.generate_traffic_report(traffic_density, intersection_name)
        return {"report": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/intersections/{intersection_id}/optimize")
def run_optimize_traffic_lights_autonomously(intersection_id: str):
    try:
        response = agent.manage_intersection(intersection_id)
        if not response:
            raise HTTPException(status_code=404, detail="Optimization data not found")
        return { "optimized_timings": response }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run("run_traffic_manager:app", host="127.0.0.1", port=8000, reload=True, log_level="info")