
def get_weather(location: str) -> str:
    """Returns mock weather data for a given location.

    Args:
        location: The name of the city or region.
    """
    # Mock data for demonstration
    weather_data = {
        "london": "Sunny, 10°C",
        "new york": "Sunny, 25°C",
        "tokyo": "Cloudy, 20°C",
        "paris": "Windy, 18°C",
    }
    return weather_data.get(location.lower(), "Unknown location. I only know weather for London, New York, Tokyo, and Paris.")

def calculator(expression: str) -> str:
    """Evaluates a simple mathematical expression.

    Args:
        expression: The mathematical expression to evaluate (e.g., '2 + 2', '10 * 5').
    """
    try:
        # malicious use warning: mostly for demo purposes
        allowed_chars = "0123456789+-*/(). "
        if not all(c in allowed_chars for c in expression):
            return "Error: Invalid characters in expression."
        
        result = eval(expression, {"__builtins__": None}, {})
        return str(result)
    except Exception as e:
        return f"Error calculating expression: {e}"
