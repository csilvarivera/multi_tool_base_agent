from google.adk.agents.run_config import RunConfig, StreamingMode
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from multi_tool_base_agent.agent import root_agent

def test_agent_weather_tool_integration() -> None:
    """Test that the agent successfully uses the weather tool."""
    session_service = InMemorySessionService()
    session = session_service.create_session_sync(user_id="test_user", app_name="test")
    runner = Runner(agent=root_agent, session_service=session_service, app_name="test")

    message = types.Content(
        role="user", parts=[types.Part.from_text(text="What is the weather in Tokyo?")]
    )

    events = list(
        runner.run(
            new_message=message,
            user_id="test_user",
            session_id=session.id,
            run_config=RunConfig(streaming_mode=StreamingMode.SSE),
        )
    )
    
    assert len(events) > 0
    
    has_tool_output = False
    for event in events:
        if event.content and event.content.parts:
            text = "".join(part.text or "" for part in event.content.parts)
            if "20°C" in text or "Cloudy" in text or "tokyo" in text.lower():
                has_tool_output = True
                break
    assert has_tool_output, "Expected agent to reply with Tokyo weather data"

def test_agent_calculator_tool_integration() -> None:
    """Test that the agent successfully uses the calculator tool."""
    session_service = InMemorySessionService()
    session = session_service.create_session_sync(user_id="test_user", app_name="test")
    runner = Runner(agent=root_agent, session_service=session_service, app_name="test")

    message = types.Content(
        role="user", parts=[types.Part.from_text(text="What is 125 * 4?")]
    )

    events = list(
        runner.run(
            new_message=message,
            user_id="test_user",
            session_id=session.id,
            run_config=RunConfig(streaming_mode=StreamingMode.SSE),
        )
    )
    
    assert len(events) > 0
    
    has_calc_output = False
    for event in events:
        if event.content and event.content.parts:
            text = "".join(part.text or "" for part in event.content.parts)
            if "500" in text:
                has_calc_output = True
                break
    assert has_calc_output, "Expected agent to calculate and reply with 500"

