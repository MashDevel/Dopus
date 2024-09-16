import os
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from .convo import Convo
from ..util import strip_array

class Provider(ABC):
    """
    Abstract base class to manage requests and responses to LLM providers.
    Core responsibilities:
        - transforming Convo messages into the format the LLM expects 
        - transforming tools into the correct format for making the API request
        - extracting data from the response of the API call

    Attributes:
        __messages (List[Dict[str, Any]]): A list of messages.
    """

    def __init__(self, model: str) -> None:
        """
        Initialize the Provider with a model.

        :param model: The model to be used by the provider.
        """
        self._model = model

    @abstractmethod
    def request(self, messages: List[Dict[str, Any]], registry: Any, tools: Optional[List[Any]] = None, system_prompt: str = "") -> Any:
        """
        Make the completion request to the llm provider

        :param messages: List of message dictionaries.
        :param registry: The registry object.
        :param tools: Optional list of tools.
        :param system_prompt: Optional system prompt.
        :return: The response from the request.
        """
        raise NotImplementedError("Subclasses must implement request method")

    @abstractmethod
    def get_tools(self, tools: List[Any], registry: Any) -> List[Any]:
        """
        Get a list of tools.

        :param tools: List of tools.
        :param registry: The registry object.
        :return: List of tools.
        """
        raise NotImplementedError("Subclasses must implement get_tools method")

    @abstractmethod
    def extract_tool_call_data(self, tool_call: Dict[str, Any]) -> Any:
        """
        Extract data from a tool call.

        :param tool_call: The tool call dictionary.
        :return: Extracted data.
        """
        raise NotImplementedError("Subclasses must implement extract_tool_call_data method")

    @abstractmethod
    def build_log(self, response: Any, messages: List[Dict[str, Any]], result: Any, tools: List[Any]) -> Dict[str, Any]:
        """
        Build a log from a response, messages, result, and tools.

        :param response: The response object.
        :param messages: List of message dictionaries.
        :param result: The result object.
        :param tools: List of tools.
        :return: The log dictionary.
        """
        raise NotImplementedError("Subclasses must implement build_log method")

    @abstractmethod
    def get_tool_calls(self, response: Any) -> List[Dict[str, Any]]:
        """
        Get tool calls from a response.

        :param response: The response object.
        :return: List of tool call dictionaries.
        """
        raise NotImplementedError("Subclasses must implement get_tool_calls method")

    def on_stop(self, convo: Convo, result: Optional[Any] = None) -> None:
        """
        Handle when the agentic loop stops.

        :param convo: The conversation object.
        :param result: Optional result to be processed.
        """
        pass

    def format_messages(self, messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Format a list of messages.

        :param messages: List of message dictionaries.
        :return: List of formatted message dictionaries.
        """
        formatted_messages = []
        for message in messages:
            if 'type' in message:
                if message['type'] == "tool_call":
                    formatted_message = self._create_tool_call_message(message)
                elif message['type'] == "tool_result":
                    formatted_message = self._create_tool_result_message(message)
                else:
                    formatted_message = message
            else:
                formatted_message = message
            if formatted_message:
                formatted_messages.append(formatted_message)
        return strip_array(formatted_messages, ["type", "timestamp"])

    @abstractmethod
    def _create_tool(self, name: Optional[str] = None, description: Optional[str] = None, parameters: Optional[Dict[str, Any]] = None, required: Optional[List[str]] = None) -> Any:
        """
        Create a tool.

        :param name: Name of the tool.
        :param description: Description of the tool.
        :param parameters: Parameters for the tool.
        :param required: List of required parameters.
        :return: The created tool.
        """
        raise NotImplementedError("Subclasses must implement create_tool method")

    @abstractmethod
    def _create_tool_call_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a tool call message.

        :param message: The message dictionary.
        :return: The formatted tool call message dictionary.
        """
        raise NotImplementedError("Subclasses must implement _create_tool_call_message method")

    @abstractmethod
    def _create_tool_result_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a tool result message.

        :param message: The message dictionary.
        :return: The formatted tool result message dictionary.
        """
        raise NotImplementedError("Subclasses must implement _create_tool_result_message method")