"""
This module defines the OptimizedTimings model, which represents optimized traffic light timings.
"""

from pydantic import BaseModel

class OptimizedTimings(BaseModel):
    """
    A model representing optimized traffic light timings.

    Attributes:
        green (int): Duration of the green light in seconds.
        red (int): Duration of the red light in seconds.
    """
    green: int
    red: int