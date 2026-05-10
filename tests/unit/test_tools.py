from multi_tool_base_agent.tools import get_weather, calculator

def test_get_weather_known_locations() -> None:
    """Test weather lookup for known cities."""
    assert "10°C" in get_weather("London")
    assert "25°C" in get_weather("New York")
    assert "20°C" in get_weather("Tokyo")
    assert "18°C" in get_weather("Paris")

def test_get_weather_unknown_location() -> None:
    """Test weather lookup for unknown city."""
    result = get_weather("Sydney")
    assert "Unknown location" in result

def test_calculator_valid_expressions() -> None:
    """Test valid math expressions."""
    assert calculator("2 + 2") == "4"
    assert calculator("10 * 5") == "50"
    assert calculator("15 / 3") == "5.0"

def test_calculator_invalid_characters() -> None:
    """Test calculator characters block list."""
    assert "Error" in calculator("import os")
    assert "Error" in calculator("2 + 2; print('hack')")

