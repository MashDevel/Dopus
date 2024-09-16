from dopus.core import Convo

import pytest
import datetime
from typing import List, Dict, Any


@pytest.fixture
def empty_convo() -> Convo:
    """Fixture for an empty Convo instance."""
    return Convo()

@pytest.fixture
def initial_messages() -> List[Dict[str, Any]]:
    """Fixture for a list of initial messages."""
    return [
        {
            "role": "user",
            "content": {"text": "Hello"},
            "timestamp": "2024-01-01T10:00:00",
            "type": "default"
        },
        {
            "role": "assistant",
            "content": {"text": "Hi there!"},
            "timestamp": "2024-01-01T10:00:01",
            "type": "default"
        }
    ]


@pytest.fixture
def populated_convo(initial_messages: List[Dict[str, Any]]) -> Convo:
    """Fixture for a Convo instance initialized with some messages."""
    return Convo(messages=initial_messages)


def test_init_empty(empty_convo: Convo):
    """Test initializing Convo with no messages."""
    assert empty_convo.get_messages() == []


def test_init_with_messages(populated_convo: Convo, initial_messages: List[Dict[str, Any]]):
    """Test initializing Convo with a list of messages."""
    assert populated_convo.get_messages() == initial_messages


def test_clear(populated_convo: Convo):
    """Test clearing messages in Convo."""
    populated_convo.clear()
    assert populated_convo.get_messages() == []


def test_append(empty_convo: Convo):
    """Test appending a single message."""
    message = {"text": "Test message"}
    empty_convo.append("user", message)
    messages = empty_convo.get_messages()
    assert len(messages) == 1
    assert messages[0]["role"] == "user"
    assert messages[0]["content"] == message
    assert messages[0]["type"] == "default"
    # Verify timestamp is correctly formatted
    datetime.datetime.fromisoformat(messages[0]["timestamp"])


def test_append_with_type(empty_convo: Convo):
    """Test appending a message with a specific type."""
    message = {"text": "Tool call"}
    empty_convo.append("assistant", message, msg_type="tool_call")
    messages = empty_convo.get_messages()
    assert len(messages) == 1
    assert messages[0]["type"] == "tool_call"


def test_add_tool_call(empty_convo: Convo):
    """Test adding a tool call and its result."""
    metadata = {
        "id": "tool_123",
        "args": {"param": "value"},
        "name": "TestTool"
    }
    result = {"output": "Success"}
    empty_convo.add_tool_call(metadata, result)
    messages = empty_convo.get_messages()
    assert len(messages) == 2

    tool_call = messages[0]
    tool_result = messages[1]

    # Verify tool_call message
    assert tool_call["role"] == "assistant"
    assert tool_call["type"] == "tool_call"
    assert tool_call["content"] == {
        "type": "tool_call",
        "id": metadata['id'],
        "args": metadata['args'],
        "name": metadata['name']
    }

    # Verify tool_result message
    assert tool_result["role"] == "user"
    assert tool_result["type"] == "tool_result"
    assert tool_result["content"] == {
        "type": "tool_result",
        "id": metadata['id'],
        "result": result,
    }


def test_get_all_of_type(populated_convo: Convo):
    """Test retrieving all messages of a specific type."""
    # Add a tool_call to have different types
    metadata = {
        "id": "tool_456",
        "args": {"query": "data"},
        "name": "DataTool"
    }
    result = {"data": [1, 2, 3]}
    populated_convo.add_tool_call(metadata, result)

    default_messages = populated_convo.get_all_of_type("default")
    tool_call_messages = populated_convo.get_all_of_type("tool_call")
    tool_result_messages = populated_convo.get_all_of_type("tool_result")

    assert len(default_messages) == 2  # Initial messages
    assert len(tool_call_messages) == 1
    assert len(tool_result_messages) == 1


def test_remove_all_of_type(populated_convo: Convo):
    """Test removing all messages of a specific type."""
    # Add multiple tool_calls
    metadata1 = {"id": "tool_1", "args": {}, "name": "Tool1"}
    metadata2 = {"id": "tool_2", "args": {}, "name": "Tool2"}
    populated_convo.add_tool_call(metadata1, "Result1")
    populated_convo.add_tool_call(metadata2, "Result2")

    # Remove all tool_result messages
    populated_convo.remove_all_of_type("tool_result")
    messages = populated_convo.get_messages()
    for msg in messages:
        assert msg["type"] != "tool_result"

    # Ensure other types remain
    default_messages = populated_convo.get_all_of_type("default")
    tool_call_messages = populated_convo.get_all_of_type("tool_call")
    assert len(default_messages) == 2  # Initial messages
    assert len(tool_call_messages) == 2  # Two tool_calls added
    assert len(populated_convo.get_all_of_type("tool_result")) == 0


def test_get_messages(populated_convo: Convo):
    """Test retrieving all messages."""
    messages = populated_convo.get_messages()
    assert len(messages) == 2
    assert messages[0]["role"] == "user"
    assert messages[1]["role"] == "assistant"


def test_get_messages_with_merge():
    """Test merging messages from multiple Convo instances."""
    convo1 = Convo(messages=[
        {
            "role": "user",
            "content": {"text": "Message 1"},
            "timestamp": "2024-01-01T10:00:00",
            "type": "default"
        }
    ])

    convo2 = Convo(messages=[
        {
            "role": "assistant",
            "content": {"text": "Message 2"},
            "timestamp": "2024-01-01T10:00:02",
            "type": "default"
        }
    ])

    convo3 = Convo(messages=[
        {
            "role": "user",
            "content": {"text": "Message 3"},
            "timestamp": "2024-01-01T10:00:01",
            "type": "default"
        }
    ])

    merged_convo = convo1.get_messages_with_merge([convo2, convo3])
    merged_messages = merged_convo.get_messages()

    assert len(merged_messages) == 3
    assert merged_messages[0]["content"]["text"] == "Message 1"
    assert merged_messages[1]["content"]["text"] == "Message 3"
    assert merged_messages[2]["content"]["text"] == "Message 2"


def test_create_message():
    """Test the internal _create_message method."""
    convo = Convo()
    role = "user"
    message = {"text": "Internal test"}
    timestamp = "2024-01-01T12:00:00"
    msg_type = "test_type"

    created_message = convo._create_message(role, message, timestamp, msg_type)

    expected_message = {
        "role": role,
        "content": message,
        "timestamp": timestamp,
        "type": msg_type
    }

    assert created_message == expected_message


def test_timestamp_format(empty_convo: Convo):
    """Test that timestamps are in ISO format."""
    message = {"text": "Timestamp test"}
    empty_convo.append("assistant", message)
    messages = empty_convo.get_messages()
    timestamp = messages[0]["timestamp"]
    # This will raise ValueError if the format is incorrect
    try:
        datetime.datetime.fromisoformat(timestamp)
    except ValueError:
        pytest.fail("Timestamp is not in ISO format")


def test_merge_empty_convos(empty_convo: Convo):
    """Test merging with empty Convo instances."""
    convo1 = Convo()
    convo2 = Convo()
    merged_convo = convo1.get_messages_with_merge([convo2, empty_convo])
    assert merged_convo.get_messages() == []


def test_merge_with_overlapping_timestamps():
    """Test merging conversations with overlapping timestamps."""
    convo1 = Convo(messages=[
        {
            "role": "user",
            "content": {"text": "First"},
            "timestamp": "2024-01-01T09:00:00",
            "type": "default"
        }
    ])

    convo2 = Convo(messages=[
        {
            "role": "assistant",
            "content": {"text": "Second"},
            "timestamp": "2024-01-01T09:00:00",
            "type": "default"
        }
    ])

    merged_convo = convo1.get_messages_with_merge([convo2])
    merged_messages = merged_convo.get_messages()

    # The order should preserve the original order when timestamps are equal
    assert len(merged_messages) == 2
    assert merged_messages[0]["content"]["text"] == "First"
    assert merged_messages[1]["content"]["text"] == "Second"
