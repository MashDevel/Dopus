from .tool_registry import tool_registry
from ..util import get_tool_str
from .. import logger
from .provider import Provider
import types
import json
import time
from enum import Enum
import inspect
from pydantic import BaseModel

class ToolRunner:
    """
    A class for managing and executing tools from LLM requests.

    This class handles tool execution for a set of tools
    that can be used by an AI agent in a conversation.
    """

    def __init__(self, tools=None, registry=None):
        """
        Initialize the ToolRunner.

        Args:
            tools (list, optional): Initial list of tools to add.
            registry (dict, optional): Custom tool registry to use.
        """
        self.__registry = registry or tool_registry
        self.__tools = set()
        self.__tool_use_callbacks = {}
        self.__event_callbacks = {}
        self.__looping = False
        self.actions = []
        self.__ret = None
        self.add_tools(tools or [])

    class Event(Enum):
        """Enum defining various events that can occur during tool execution."""
        TOOL_FAILED = "Tool call failed"
        TOOL_NOT_FOUND = "Tool not found"
        TOOL_CALL_COMPLETED = "Tool call completed"
        STOP = "Tool Runner Stopped"
        PRE_TOOL_CALL = "Pre Tool Call"
    
    def on_event(self, event : Event, callback):
        """
        Register a callback function for a specific event.

        Args:
            event (Event): The event to listen for.
            callback (callable): The function to call when the event occurs.
        """
        self.__event_callbacks.setdefault(event, []).append(callback)

    def _trigger_event(self, event : Event, *args, **kwargs):
        """
        Trigger an event and call all registered callbacks for that event.

        Args:
            event (Event): The event to trigger.
            *args: Positional arguments to pass to the callbacks.
            **kwargs: Keyword arguments to pass to the callbacks.
        """
        if event in self.__event_callbacks:
            for callback in self.__event_callbacks[event]:
                callback(*args, **kwargs)

    def on(self, tool, callback):
        """
        Register a callback function for a specific tool.

        Args:
            tool (str): The name of the tool.
            callback (callable): The function to call when the tool is used.
        """
        tool_str = get_tool_str(tool)
        if tool_str and tool_str in self.__registry and tool_str in self.__tools:
            self.__tool_use_callbacks.setdefault(tool_str, []).append(callback)
        else:
            logger.debug(f"Tool '{tool_str}' not found in registry. Cannot add callback.")

    def add_tool(self, tool, agent=None):
        """
        Add a tool to the ToolRunner.

        Args:
            tool (str): The name of the tool to add.
            agent (object, optional): The agent object to attach the tool to.
        """
        if tool:
            self.__tools.add(get_tool_str(tool))
            self._add_tool_funcs(tool, agent)

    def add_tools(self, tools, agent=None):
        """
        Add multiple tools to the ToolRunner.

        Args:
            tools (list): A list of tool names to add.
            agent (object, optional): The agent object to attach the tools to.
        """
        [self.add_tool(tool, agent) for tool in tools]

    def remove_tool(self, tool):
        """
        Remove a tool from the ToolRunner.

        Args:
            tool (str): The name of the tool to remove.
        """
        if tool:
            self.__tools.discard(get_tool_str(tool))

    def loop(self, convo, llm, agent=None):
        """
        Start the main execution loop for processing conversations.

        Args:
            convo (object): The conversation object.
            llm (object): The language model object.
            agent (object, optional): The agent object.

        Returns:
            tuple: A tuple containing the final result and a list of actions performed.
        """
        self.actions = []
        self.__looping = True
        while self.__looping:
            result, dlog = self.execute(convo, llm, agent)
            self.actions.append(dlog)
        self._trigger_event(ToolRunner.Event.STOP, result)
        return self.__ret, self.actions

    def execute(self, convo, llm, agent=None):
        """
        Execute a single step in the conversation processing.

        Args:
            convo (object): The conversation object.
            llm (object): The language model object.
            agent (object, optional): The agent object.

        Returns:
            tuple: A tuple containing the result and a log of the execution.
        """
        messages = convo.get_messages()
        resp = llm.request(messages, self.__registry, self.__tools, agent.prompt() if agent else "")
        tool_calls = llm.get_tool_calls(resp)
        if tool_calls is not None:
            result = self._call_tools(tool_calls, llm)
            dlog = llm.build_log(resp, messages, result, self.__tools, agent)
            return result, dlog
        else:
            return None, None

    def stop(self, result=None):
        """
        Stop the execution loop.

        Args:
            result (any, optional): The final result to return.
        """
        self.__ret = result, self.actions
        self.__looping = False

    def _add_tool_funcs(self, tool: str, agent=None):
        """
        Add tool functions to the ToolRunner or agent.

        Args:
            tool (str): The name of the tool to add functions for.
            agent (object, optional): The agent object to attach the functions to.
        """
        tool_str = get_tool_str(tool)
        tool_info = self.__registry.get(tool_str)
        if tool_info and tool_info.get('function'):
            obj = agent or self
            method_name = f"on_{tool_str}"
            setattr(obj, method_name, types.MethodType(tool_info['function'], obj))
            obj.on_tool_use(tool, getattr(obj, method_name))
        else:
            logger.debug("Tool not found or has no callback")

    def _call_tool(self, tool_name, tool_args):
        """
        Call a specific tool with the given arguments.

        Args:
            tool_name (str): The name of the tool to call.
            tool_args (dict): The arguments to pass to the tool.

        Returns:
            any: The result of the tool execution.
        """
        if tool_name not in self.__registry or tool_name not in self.__tools:
            self._trigger_event(
                ToolRunner.Event.TOOL_NOT_FOUND, 
                tool_name, 
                tool_args, 
                ToolRunner.Event.TOOL_NOT_FOUND.value
            )
            return None
        try:
            for callback in self.__tool_use_callbacks[tool_name]:                
                sig = inspect.signature(callback)
                instantiated_args = {}
                
                for name, param in sig.parameters.items():
                    if name == 'self':
                        continue
                    if name in tool_args:
                        arg_value = tool_args[name]
                        if isinstance(param.annotation, type) and issubclass(param.annotation, BaseModel):
                            try:
                                instantiated_args[name] = param.annotation(**arg_value)
                            except Exception as e:
                                logger.error(f"Error instantiating {name}: {e}")
                                self._trigger_event(
                                    ToolRunner.Event.TOOL_FAILED, 
                                    tool_name, 
                                    tool_args, 
                                    f"{ToolRunner.Event.TOOL_FAILED.value}: {e}"
                                )
                                return None
                        else:
                            instantiated_args[name] = arg_value
                res = callback(**instantiated_args) or ''
            return res
        except Exception as e:
            logger.error(e)
            self._trigger_event(
                ToolRunner.Event.TOOL_FAILED, 
                tool_name, 
                tool_args, 
                f"{ToolRunner.Event.TOOL_FAILED.value}: {e}"
            )

    def _call_tools(self, tool_calls, llm):
        """
        Process and execute a list of tool calls.

        Args:
            tool_calls (list): A list of tool calls to execute.
            llm (object): The language model object.

        Returns:
            any: The result of the tool execution.
        """
        if not tool_calls:
            return None
        tool_call = tool_calls[0]
        self._trigger_event(ToolRunner.Event.PRE_TOOL_CALL, tool_call)
        tool_data = llm.extract_tool_call_data(tool_call)
        result = self._call_tool(tool_data['name'], tool_data['args'])
        self._trigger_event(ToolRunner.Event.TOOL_CALL_COMPLETED, result, tool_data)
        return result