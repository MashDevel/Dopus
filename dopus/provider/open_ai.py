from openai import OpenAI as OAI
import json
from ..core.provider import Provider
from .. import logger

class OpenAI(Provider):
    def __init__(self, api_key, model="gpt-4o"):
        self.client = OAI(api_key=api_key)
        super().__init__(model)

    def on_stop(self, convo, result=None):
        pass

    def get_embedding(self, text, model="text-embedding-3-small"):
        response = self.client.embeddings.create(
            input=text,
            model=model
        )
        return response.data[0].embedding

    def extract_tool_call_data(self, tool_call):
        tool_name = tool_call.function.name
        try:
            tool_args = json.loads(tool_call.function.arguments)
        except Exception as e:
            logger.error(f"Failed to parse tool arguments: {tool_call.function.arguments}")
            return None
        return {
            'id': tool_call.id,
            'args': tool_args,
            'name': tool_name
        }
    
    def get_tool_calls(self, response):
        return response.choices[0].message.tool_calls

    def _create_tool(self, name=None, description=None, parameters=None, required=None):
        return {
            "type": "function",
            "strict": True,
            "function": {
                "name": name or "default_name",
                "description": description or "default_description",
                "parameters": {
                    "type": "object",
                    "properties": parameters or {},
                    "additionalProperties": False,
                    "required": required or []
                }
            }
        }

    def _create_tool_call_message(self, message):
        return {
            "role": "assistant",
            "timestamp": message['timestamp'],
            "type": "tool",
            "tool_calls": [
                {
                    "id": message['content']['id'],
                    "type": "function",
                    "function": {
                        "name": message['content']['name'],
                        "arguments": str(message['content']['args'])
                    }
                }
            ]
        }

    def _create_tool_result_message(self, message):
        return {
            "role": "tool",
            "timestamp": message['timestamp'],
            "type": "tool_output",
            "content": message['content']['result'],
            "tool_call_id": message['content']['id']
        }

    def request(self, messages, registry, tools=None, system_prompt=""):
        formatted_messages = self.format_messages(messages)
        formatted_messages.insert(0, {"role": "system", "content": system_prompt})
        if tools is not None:
            tools = self.get_tools(tools, registry)
            response = self.client.chat.completions.create(
                messages=formatted_messages,
                model=self._model,
                tool_choice="required",
                parallel_tool_calls=False,
                n=1,
                tools=tools
            )
        else:
            response = self.client.chat.completions.create(
                messages=formatted_messages,
                model=self.model,
                n=1,
            )
        return response

    def get_tools(self, tools, registry):
        return [
            self._create_tool(
                name=tool,
                description=registry[tool]["description"],
                parameters=registry[tool]["properties"],
                required=registry[tool]["required"]
            )
            for tool in tools if tool in registry
        ]

    def build_log(self, resp, messages, result, tools, agent=None):
        message = resp.choices[0].message
        return {
            'id': resp.id,
            'messages': messages,
            'created': resp.created,
            'model': resp.model,
            'messages': messages,
            'available_tools': tools,
            'tool_called': {
                'id': message.tool_calls[0].id,
                'name': message.tool_calls[0].function.name,
                'arguments': json.loads(message.tool_calls[0].function.arguments or {}),
                'result': result
            },
            'usage': {
                'completion_tokens': resp.usage.completion_tokens,
                'prompt_tokens': resp.usage.prompt_tokens,
                'total_tokens': resp.usage.total_tokens
            },
            'system_fingerprint': resp.system_fingerprint
        }