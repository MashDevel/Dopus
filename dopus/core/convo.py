import datetime
from typing import List, Dict, Any, Optional
from .. import logger

class Convo:
    """
    A class to manage the conversational context window.

    Attributes:
        __messages (List[Dict[str, Any]]): A list of messages.
    """

    def __init__(self):
        """
        Initializes the Convo instance.
        """
        self.__messages = []
        self.clear()

    def clear(self) -> None:
        """
        Clears all messages in the conversation.
        """
        self.__messages = []

    def add_tool_call(self, metadata: Dict[str, Any], result: Any) -> None:
        """
        Adds a tool call and its result to the conversation.

        Args:
            metadata (Dict[str, Any]): Metadata about the tool call.
            result (Any): The result of the tool call.
        """
        self.append("assistant", {
            "type": "tool_call",
            "id": metadata['id'],
            "args": metadata['args'],
            "name": metadata['name']
        }, msg_type="tool_call")
        self.append("user", {
            "type": "tool_result",
            "id": metadata['id'],
            "result": result,
        }, msg_type="tool_result")

    def append(self, role: str, message: Dict[str, Any], msg_type: str = "default") -> None:
        """
        Appends a message to the conversation.

        Args:
            role (str): The role of the message sender (e.g., 'user', 'assistant').
            message (Dict[str, Any]): The message content.
            msg_type (str): The type of the message. Defaults to "default".
        """
        timestamp = datetime.datetime.now().isoformat()
        self.__messages.append(self._create_message(role, message, timestamp, msg_type))

    def get_all_of_type(self, msg_type: str) -> List[Dict[str, Any]]:
        """
        Retrieves all messages of a specific type.

        Args:
            msg_type (str): The type of messages to retrieve.

        Returns:
            List[Dict[str, Any]]: A list of messages of the specified type.
        """
        return [message for message in self.__messages if message['type'] == msg_type]

    def remove_all_of_type(self, msg_type: str) -> None:
        """
        Removes all messages of a specific type.

        Args:
            msg_type (str): The type of messages to remove.
        """
        self.__messages = [message for message in self.__messages if message['type'] != msg_type]

    def get_messages(self) -> List[Dict[str, Any]]:
        """
        Retrieves all messages in the conversation.

        Returns:
            List[Dict[str, Any]]: A list of all messages.
        """
        return self.__messages

    def _create_message(self, role: str, message: Dict[str, Any], timestamp: str, msg_type: str) -> Dict[str, Any]:
        """
        Creates a message dictionary.

        Args:
            role (str): The role of the message sender.
            message (Dict[str, Any]): The message content.
            timestamp (str): The timestamp of the message.
            msg_type (str): The type of the message.

        Returns:
            Dict[str, Any]: A dictionary representing the message.
        """
        return {
            "role": role,
            "content": message,
            "timestamp": timestamp,
            "type": msg_type
        }
