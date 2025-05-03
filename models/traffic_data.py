"""
This module defines the TrafficData model, which represents traffic density and light timings.
"""

from pydantic import BaseModel
from typing import Dict

class TrafficData(BaseModel):
    """
    A model representing traffic data.

    Attributes:
        traffic_density (float): The density of traffic.
        light_timings (Dict[str, int]): A dictionary mapping light names to their timings in seconds.
    """
    traffic_density: float
    light_timings: Dict[str, int]