import pytest
from traffic_manager_agent import TrafficManagerAgent, Config
import os
from unittest.mock import patch, MagicMock

def test_optimize_high_density_traffic_lights():
    agent: TrafficManagerAgent = TrafficManagerAgent()

    high_density = 60
    light_timings: dict = {"green": 30, "red": 30}
    optimized_timings = agent.optimize_traffic_lights(high_density, light_timings)
    assert optimized_timings["green"] == 40
    assert optimized_timings["red"] == 25

def test_optimize_low_density_traffic_lights():
    agent: TrafficManagerAgent = TrafficManagerAgent()
    
    low_density = 10
    light_timings = {"green": 30, "red": 30}
    optimized_timings = agent.optimize_traffic_lights(low_density, light_timings)
    assert optimized_timings["green"] == 25
    assert optimized_timings["red"] == 35

def test_simulate_decision_valid_scenario():
    agent: TrafficManagerAgent = TrafficManagerAgent()

    scenario: dict = {
        "intersection_id": "A1",
        "traffic_density": 45,
        "light_timings": {"green": 30, "red": 30}
    }
    decision = agent.simulate_decision(scenario)
    assert decision is True

def test_simulate_decision_invalid_scenario():
    agent: TrafficManagerAgent = TrafficManagerAgent()

    scenario: dict = {
        "intersection_id": "A1",
        "light_timings": {"green": 30, "red": 30}
    }
    decision = agent.simulate_decision(scenario)
    assert decision is False

def test_optimize_traffic_lights_zero_density():
    agent: TrafficManagerAgent = TrafficManagerAgent()

    zero_density = 0
    light_timings = {"green": 30, "red": 30}
    optimized_timings = agent.optimize_traffic_lights(zero_density, light_timings)
    assert optimized_timings["green"] == 25
    assert optimized_timings["red"] == 35

def test_optimize_traffic_lights_boundary_high_density():
    agent: TrafficManagerAgent = TrafficManagerAgent()

    boundary_high_density = 50
    light_timings = {"green": 30, "red": 30}
    optimized_timings = agent.optimize_traffic_lights(boundary_high_density, light_timings)
    assert optimized_timings["green"] == 30
    assert optimized_timings["red"] == 30

def test_optimize_traffic_lights_extreme_high_density():
    agent: TrafficManagerAgent = TrafficManagerAgent()

    extreme_high_density = 1000
    light_timings = {"green": 30, "red": 30}
    optimized_timings = agent.optimize_traffic_lights(extreme_high_density, light_timings)
    assert optimized_timings["green"] == 40
    assert optimized_timings["red"] == 25

def test_optimize_traffic_lights_non_integer_density():
    agent: TrafficManagerAgent = TrafficManagerAgent()

    non_integer_density = 25.5
    light_timings = {"green": 30, "red": 30}
    optimized_timings = agent.optimize_traffic_lights(non_integer_density, light_timings)
    assert optimized_timings["green"] == 30
    assert optimized_timings["red"] == 30

def test_simulate_decision_missing_traffic_density():
    agent: TrafficManagerAgent = TrafficManagerAgent()

    scenario = {
        "intersection_id": "A1",
        "light_timings": {"green": 30, "red": 30}
    }
    decision = agent.simulate_decision(scenario)
    assert decision is False

def test_simulate_decision_invalid_light_timings():
    agent: TrafficManagerAgent = TrafficManagerAgent()

    scenario = {
        "intersection_id": "A1",
        "traffic_density": 45,
        "light_timings": {"green": -10, "red": 30}
    }
    with pytest.raises(ValueError):
        decision = agent.simulate_decision(scenario)
        assert decision is False

def test_optimize_traffic_lights_negative_density():
    agent: TrafficManagerAgent = TrafficManagerAgent()

    negative_density = -10
    light_timings = {"green": 30, "red": 30}
    with pytest.raises(ValueError, match="Traffic density cannot be negative."):
        agent.optimize_traffic_lights(negative_density, light_timings)

def test_optimize_traffic_lights_invalid_light_timings():
    agent: TrafficManagerAgent = TrafficManagerAgent()

    traffic_density = 30
    invalid_light_timings = {"green": -5, "red": 30}  # Negative green light duration
    with pytest.raises(ValueError, match="Invalid value for green in light timings."):
        agent.optimize_traffic_lights(traffic_density, invalid_light_timings)

def test_traffic_data_initialization():
    agent: TrafficManagerAgent = TrafficManagerAgent()

    # Ensure traffic_data initializes as an empty DataFrame
    assert agent.traffic_data.empty

def test_simulate_decision_invalid_schema():
    agent: TrafficManagerAgent = TrafficManagerAgent()

    invalid_scenario = {"traffic_density": 30}  # Missing required fields
    decision = agent.simulate_decision(invalid_scenario)
    assert decision is False

def test_optimize_traffic_lights_non_numeric_density():
    agent: TrafficManagerAgent = TrafficManagerAgent()

    non_numeric_density = "high"  # Non-numeric value
    light_timings = {"green": 30, "red": 30}
    with pytest.raises(ValueError, match="Traffic density must be a numeric value."):
        agent.optimize_traffic_lights(non_numeric_density, light_timings)

def test_optimize_traffic_lights_non_dict_timings():
    agent: TrafficManagerAgent = TrafficManagerAgent()
    
    traffic_density = 30
    invalid_light_timings = "not a dictionary"
    with pytest.raises(ValueError, match="Light timings must be a dictionary."):
        agent.optimize_traffic_lights(traffic_density, invalid_light_timings)

def test_optimize_traffic_lights_missing_key():
    agent: TrafficManagerAgent = TrafficManagerAgent()
    
    traffic_density = 30
    incomplete_light_timings = {"green": 30}  # Missing "red" key
    with pytest.raises(ValueError, match="Invalid value for red in light timings."):
        agent.optimize_traffic_lights(traffic_density, incomplete_light_timings)

def test_schema_validation():
    agent: TrafficManagerAgent = TrafficManagerAgent()
    
    # Test that schema has the correct structure
    assert "properties" in agent.schema
    assert "intersection_id" in agent.schema["properties"]
    assert "traffic_density" in agent.schema["properties"]
    assert "light_timings" in agent.schema["properties"]
    assert "required" in agent.schema
    
def test_system_behavior():
    agent: TrafficManagerAgent = TrafficManagerAgent()
    
    # Test that system behavior is properly defined
    assert "role" in agent.system_behavior
    assert agent.system_behavior["role"] == "system"
    assert "content" in agent.system_behavior
    assert "traffic manager agent" in agent.system_behavior["content"].lower()

@patch('openai.OpenAI')
def test_recommend_traffic_strategy(mock_openai):
    # Setup mock response
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_choice = MagicMock()
    mock_message = MagicMock()
    mock_message.content = "Recommended strategy: Increase green light duration"
    mock_choice.message = mock_message
    mock_response.choices = [mock_choice]
    mock_client.chat.completions.create.return_value = mock_response
    
    with patch.object(TrafficManagerAgent, 'client', mock_client, create=True):
        agent = TrafficManagerAgent()
        result = agent.recommend_traffic_strategy(45.5)
        
        # Verify the result
        assert result == "Recommended strategy: Increase green light duration"
        # Verify the API was called with correct parameters
        mock_client.chat.completions.create.assert_called_once()

@patch('openai.OpenAI')
def test_generate_traffic_report(mock_openai):
    # Setup mock response
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_choice = MagicMock()
    mock_message = MagicMock()
    mock_message.content = "Traffic report for intersection"
    mock_choice.message = mock_message
    mock_response.choices = [mock_choice]
    mock_client.chat.completions.create.return_value = mock_response
    
    with patch.object(TrafficManagerAgent, 'client', mock_client, create=True):
        agent = TrafficManagerAgent()
        result = agent.generate_traffic_report(30.0, "Main Street")
        
        # Verify the result
        assert result == "Traffic report for intersection"
        # Verify the API was called with correct parameters
        mock_client.chat.completions.create.assert_called_once()

@patch.dict(os.environ, {
    "OPENAI_API_KEY": "test_key", 
    "GPT_MODEL": "gpt-4", 
    "O1_MODEL": "o1-preview",
    "SUPABASE_KEY": "test_supabase_key",
    "SUPABASE_URL": "https://test.supabase.co"
})
def test_config_with_env_variables():
    config = Config()
    assert config.openai_api_key == "test_key"
    assert config.openai_gpt_model == "gpt-4"
    assert config.openai_o1_model == "o1-preview"
    assert config.supabase_api_key == "test_supabase_key"
    assert config.supabase_url == "https://test.supabase.co"

def test_optimize_traffic_lights_minimum_values():
    agent: TrafficManagerAgent = TrafficManagerAgent()
    
    # Test that values don't go below minimum thresholds
    light_timings = {"green": 12, "red": 7}
    optimized_timings = agent.optimize_traffic_lights(10, light_timings)
    assert optimized_timings["green"] == 10  # Should hit minimum of 10
    assert optimized_timings["red"] == 12    # Increased by 5

def test_optimize_traffic_lights_with_recommendation():
    agent: TrafficManagerAgent = TrafficManagerAgent()

    traffic_density = 30
    light_timings = {"green": 30, "red": 30}
    recommended_timings = {"green": 35, "red": 25}

    optimized_timings = agent.optimize_traffic_lights(traffic_density, light_timings, recommended=recommended_timings)
    assert optimized_timings["green"] == 35
    assert optimized_timings["red"] == 25

if __name__ == "__main__":
    pytest.main()