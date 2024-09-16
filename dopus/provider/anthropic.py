from anthropic import Anthropic as Anth
from ..core.provider import Provider

class Anthropic(Provider):
    def __init__(self, api_key, model="claude-3-5-sonnet-20240620"):
        super().__init__(model)
        self.client = Anth(api_key=api_key)

    def extract_tool_call_data(self, tool_call):
        return {
            'id': tool_call.id,
            'args': tool_call.input,
            'name': tool_call.name
        }

    def on_stop(self, convo, result=None):
        convo.append("assistant", "Waiting for user input...")

    def get_tool_calls(self, response):
        return response.content

    def request(self, messages, registry, tools, system_prompt):
        formatted_messages = self.format_messages(messages)
        if tools is not None:
            tools = self.get_tools(tools, registry)
            return self.client.messages.create(
                messages=formatted_messages,
                model=self.model,
                system=system_prompt,
                tool_choice={"type": "any"} if tools else None,
                max_tokens=500,
                tools=tools
            )

    def create_tool_call_message(self, message):
        return {
            "role": "assistant",
            "content": [
                {
                    "type": "tool_use",
                    "id": message['content']['id'],
                    "name": message['content']['name'],
                    "input": message['content']['args']
                }
            ]
        }

    def create_tool_result_message(self, message):
        return {
            "role": "user",
            "content": [
                {
                    "type": "tool_result",
                    "tool_use_id": message['content']['id'],
                    "content": message['content']['result']
                }
            ]
        }

    def get_tools(self, tools, registry):
        return [
            self.create_tool(
                name=tool,
                description=registry[tool]["description"],
                input_schema={
                    "type": "object",
                    "properties": registry[tool]["properties"],
                    "required": registry[tool]["required"]
                }
            )
            for tool in tools if tool in registry
        ]

    def create_tool(self, name=None, description=None, input_schema=None):
        return {
            "name": name or "default_name",
            "description": description or "default_description",
            "input_schema": input_schema or {
                "type": "object",
                "properties": {},
                "required": []
            }
        }