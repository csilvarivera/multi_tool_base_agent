# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from google.genai import types
from google.adk.agents import Agent
from google.adk.apps import App
from .tools import get_weather, calculator
from dotenv import load_dotenv
from google.adk.plugins import ReflectAndRetryToolPlugin

# load the environment
load_dotenv()


root_agent = Agent(
    model='gemini-2.5-pro',
    name='multi_tool_agent',
    instruction="You are a helpful assistant with access to weather and calculator tools. Use them to answer user questions.",
    tools=[get_weather, calculator],
    generate_content_config=types.GenerateContentConfig(temperature=0.01),
)

app = App(root_agent=root_agent, 
name="multi_tool_base_agent", 
plugins=[
        ReflectAndRetryToolPlugin(max_retries=3),
    ],)