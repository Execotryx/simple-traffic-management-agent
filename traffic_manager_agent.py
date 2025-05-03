import json
from typing import Dict, Union, List, Optional, Any
import pandas as pd
from jsonschema import validate, ValidationError
from openai import OpenAI
from openai.types.chat import ChatCompletion
from supabase import Client, create_client
from config import Config
from functools import cached_property
from json.decoder import JSONDecodeError
from models.traffic_data import TrafficData
from models.optimized_timings import OptimizedTimings

class TrafficManagerAgent:
    """
    TrafficManagerAgent manages traffic light optimization
    and decision-making for urban traffic control.
    """

    #region Constants
    class Tables:
        INTERSECTIONS = "intersections"
        TRAFFIC_DATA = "traffic_data"
        LOGS = "logs"
    #endregion

    #region Traffic Data
    __traffic_data: pd.DataFrame = None

    @property
    def traffic_data(self) -> pd.DataFrame:
        """
        Get the traffic data.
        :return: DataFrame containing traffic data.
        """
        if self.__traffic_data is None:
            self.__traffic_data = pd.DataFrame()
        return self.__traffic_data
    
    #endregion

    #region Schema
    __schema: Dict[str, Union[str, List[str]]] = {
        "type": "object",
        "properties": {
            "intersection_id": {"type": "string"},
            "traffic_density": {"type": "number"},
            "light_timings": { "type": "object"}
        },
        "required": ["intersection_id", "traffic_density", "light_timings"]
    }

    __response_schema: Dict[str, Union[str, List[str]]] = {
        "type": "object",
        "properties": {
            "green": {"type": "integer"},
            "red": {"type": "integer"}
        },
        "required": ["green", "red"],
        "additionalProperties": False
    }

    @property
    def schema(self) -> Dict[str, Union[str, List[str]]]:
        """
        Get the schema for traffic data validation.
        :return: JSON schema as a dictionary.
        """
        return self.__schema

    @property
    def response_schema(self) -> Dict[str, Union[str, List[str]]]:
        return self.__response_schema
    
    #endregion

    #region Utility Functions
    @staticmethod
    def validate_traffic_density(traffic_density: Any):
        if isinstance(traffic_density, str):
            try:
                traffic_density = float(traffic_density)
            except ValueError:
                raise ValueError("Traffic density must be a numeric value.")
        if not isinstance(traffic_density, (int, float)) or traffic_density < 0:
            raise ValueError("Traffic density must be a non-negative numeric value.")
        return traffic_density

    @staticmethod
    def validate_light_timings(light_timings: Dict[str, int]):
        if not isinstance(light_timings, dict):
            raise ValueError("Light timings must be a dictionary.")
        for key in ["green", "red"]:
            if key not in light_timings or not isinstance(light_timings[key], int) or light_timings[key] < 0:
                raise ValueError(f"Invalid value for {key} in light timings.")
        return light_timings
    #endregion

    #region Lazy Initialization
    @cached_property
    def client(self) -> OpenAI:
        return OpenAI(api_key=self.config.openai_api_key)

    @cached_property
    def supabase_client(self) -> Client:
        return create_client(self.config.supabase_url, self.config.supabase_api_key)

    @cached_property
    def system_behavior(self) -> dict:
        return {
            "role": "system",
            "content": (
                "You are a traffic manager agent. Your task is to optimize traffic light timings "
                "based on real-time traffic density data."
            )
        }
    #endregion

    #region Config
    __config: Config = None

    @property
    def config(self) -> Config:
        """
        Get the configuration settings.
        :return: Config object.
        """
        if self.__config is None:
            self.__config = Config()
        return self.__config
    #endregion

    def optimize_traffic_lights(self, traffic_density: float, light_timings: TrafficData, recommended: Optional[OptimizedTimings]) -> OptimizedTimings:
        traffic_density = self.validate_traffic_density(traffic_density)
        light_timings_dict = light_timings.light_timings

        if recommended:
            light_timings_dict = recommended.dict()
        else:
            if traffic_density > 50:
                light_timings_dict["green"] += 10
                light_timings_dict["red"] -= 5
            elif traffic_density < 20:
                light_timings_dict["green"] -= 5
                light_timings_dict["red"] += 5

            light_timings_dict["green"] = max(10, light_timings_dict["green"])
            light_timings_dict["red"] = max(5, light_timings_dict["red"])

        return OptimizedTimings(**light_timings_dict)

    def fetch_intersections(self):
        """
        Fetch all intersections from the database.
        :return: List of intersections data.
        """
        response = self.supabase_client.table(self.Tables.INTERSECTIONS).select("*").execute()
        return response.data

    def fetch_intersection(self, intersection_id: str) -> Optional[Dict[str, Any]]:
        """
        Fetch a specific intersection by ID.
        :param intersection_id: ID of the intersection.
        :return: Intersection data.
        """
        response = self.supabase_client.table(self.Tables.INTERSECTIONS).select("*").eq("id", intersection_id).execute()
        return response.data[0] if response.data else None

    def add_traffic_data(self, intersection_id: str, traffic_data: TrafficData):
        """
        Add traffic data to the database.
        :param intersection_id: ID of the intersection.
        :param traffic_data: TrafficData object containing traffic density and light timings.
        :return: Response data from the database.
        """
        data = {
            "intersection_id": intersection_id,
            "traffic_density": traffic_data.traffic_density,
            "light_timings": traffic_data.light_timings.dict()
        }
        response = self.supabase_client.table(self.Tables.TRAFFIC_DATA).insert(data).execute()
        return response.data

    def log_message(self, traffic_data_id: str, message: str):
        """
        Log a message related to traffic data.
        :param traffic_data_id: ID of the traffic data entry.
        :param message: Log message to be recorded.
        :return: Response data from the database.
        """
        log_entry = {
            "traffic_data_id": traffic_data_id,
            "log_message": message
        }
        response = self.supabase_client.table(self.Tables.LOGS).insert(log_entry).execute()
        return response.data

    def generate_prompt(self, template: str, **kwargs) -> str:
        return template.format(**kwargs)

    def generate_traffic_report(self, traffic_density: float, intersection_name: str) -> str:
        prompt = self.generate_prompt(
            template=(
                "The traffic density at the intersection named \"{intersection_name}\" is {traffic_density}. "
                "Considering current conditions, provide a detailed and actionable traffic management report "
                "that includes recommended adjustments for optimizing traffic flow and safety."
            ),
            traffic_density=traffic_density,
            intersection_name=intersection_name
        )

        response: ChatCompletion = self.client.chat.completions.create(
            model=self.config.openai_gpt_model,
            messages=[self.system_behavior, {"role": "user", "content": prompt}],
            max_tokens=150,
            temperature=0.5,
            n=1
        )
        return response.choices[0].message.content

    def recommend_traffic_strategy(self, traffic_density: float, current_light_timings: TrafficData) -> OptimizedTimings:
        raw_light_timings: str = json.dumps(current_light_timings.light_timings)

        prompt = self.generate_prompt(
            template=(
                "The traffic density is currently {traffic_density}. "
                "Suggest the best traffic light strategy to minimize congestion and maximize safety, "
                "including recommendations for adjusting green and red light durations. Note that only red/green lights are available for adjustment.\n"
                "Respond with only the adjusted scenario in the following format:\n"
                "{{\n"
                "  \"green\": <int>,\n"
                "  \"red\": <int>\n"
                "}}\n"
                "Current light timings: {raw_light_timings}\n"
                "Adjusted light timings for Density Level {traffic_density}:\n"
            ),
            traffic_density=traffic_density,
            raw_light_timings=raw_light_timings
        )

        response: ChatCompletion = self.client.chat.completions.create(
            model=self.config.openai_gpt_model,
            messages=[self.system_behavior, {"role": "user", "content": prompt}],
            max_tokens=150,
            temperature=0.5,
            n=1
        )

        try:
            raw_response: Dict = json.loads(response.choices[0].message.content)
        except JSONDecodeError as e:
            raise ValueError(f"Invalid JSON response: {e.msg}")

        try:
            validate(instance=raw_response, schema=self.response_schema)
        except ValidationError as e:
            raise ValueError(f"Invalid response format: {e.message}")

        return OptimizedTimings(**raw_response)

    def manage_intersection(self, intersection_id: str) -> Dict[str, Union[str, Dict[str, int]]]:
        """
        Manage traffic at a specific intersection by optimizing light timings.
        :param intersection_id: ID of the intersection.
        :return: Dictionary containing the recommended strategy and optimized timings.
        """
        # 1. Fetch current state
        current = self.supabase_client \
            .table(self.Tables.TRAFFIC_DATA) \
            .select("*") \
            .eq("intersection_id", intersection_id) \
            .order("timestamp", desc=True) \
            .limit(1) \
            .execute().data[0]
        density: float = float(current["traffic_density"])
        timings: Dict = json.loads(current["light_timings"])

        # 2. Recommend strategy (LLM narrative)
        recommended_strategy: Dict[str, int] = self.recommend_traffic_strategy(density, TrafficData(traffic_density=density, light_timings=timings))
        print("Strategy:", recommended_strategy)

        # 3. Compute optimized timings (rule-based or parsed from strategy)
        optimized: Dict[str, int] = self.optimize_traffic_lights(density, TrafficData(traffic_density=density, light_timings=timings), recommended_strategy)

        # 4. Apply & log
        response = self.add_traffic_data(intersection_id, TrafficData(traffic_density=density, light_timings=optimized.dict()))
        self.log_message(response[0]["id"], f"Applied optimized timings: {optimized}")

        return {"strategy": recommended_strategy, "optimized_timings": optimized.dict()}


    def __init__(self):
        self.__config = Config()
        self.__traffic_data = None
        self.__client = None
        self.__supabase_client = None
        self.__system_behavior = None
