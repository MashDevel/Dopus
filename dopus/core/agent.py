from abc import ABC, abstractmethod
from . import Convo, ToolRunner, tool_registry, Provider
import inspect
import json
from .. import logger
from ..util import get_tool_str

class Agent(ABC):
    """
    Abstract base class of an agent capable of running tools
    and managing conversations. The agent interfaces with a language model (LLM) and 
    has access to various tools through the tool registry. It is designed to handle conversations
    where tools may be called upon dynamically.
    
    Attributes:
        provider (Provider): The language model provider used by the agent.
        name (str): The name of the agent.
        convo (Convo): Conversation handler that manages the dialogue context.
        registry: A registry of tools that can be utilized by the agent.
        tool_manager (ToolRunner): Manager that handles tool execution and lifecycle events.
    """
    
    def __init__(self, provider: Provider, name: str = "Agent", convo: Convo = None, registry: dict = None, tool_manager: ToolRunner = None):
        """
        Initializes the agent with a name and an optional language model (LLM).
        
        Args:
            name (str): Name of the agent.
            provider: language model provider instance.
        """
        self.__name = name
        self.__provider = provider
        self.__convo = convo or Convo()
        self.__registry = registry or tool_registry
        self.__tool_manager = tool_manager or ToolRunner(registry=self.__registry)
        self.__tool_manager.on_event(ToolRunner.Event.STOP, self.__on_stop)
        self.__tool_manager.on_event(ToolRunner.Event.TOOL_FAILED, self.__on_tool_failed)
        self.__tool_manager.on_event(ToolRunner.Event.TOOL_CALL_COMPLETED, self.__post_tool_call_callback)
        self.__tool_manager.on_event(ToolRunner.Event.PRE_TOOL_CALL, self.__pre_tool_call_callback)
        self.__add_tools_in_class()

    def get_actions(self):
        """
        Get the list of actions the agent has taken
        """
        return self.__tool_manager.actions

    def reset(self):
        """
        Resets the conversation context for the agent. 
        Clears the current conversation history.
        """
        self.__convo.clear()

    def run(self, message : str = None):
        """
        Runs the agent, initiating a conversation or tool execution loop. 
        If a message is provided, it appends it to the conversation.
        
        Args:
            message (str, optional): Message from the user to be processed by the agent.
        
        Returns:
            Result of the tool execution loop managed by the tool manager.
        """
        if message is not None:
            self.__convo.append("user", message)
        return self.__tool_manager.loop(self.__convo, self.__provider, self)

    def stop(self, result=None):
        """
        Stops the current tool execution or conversation flow and returns a result.
        
        Args:
            result: Optional result to return when stopping.
        """
        self.__tool_manager.stop(result)

    def on_tool_use(self, tool: str, func):
        """
        Registers a callback function to be triggered when a tool is used.
        
        Args:
            tool (str): Name of the tool.
            func: Function to be called when the tool is triggered.
        """
        self.__tool_manager.on(tool, func)

    def add_tool(self, tool: str):
        """
        Adds a tool by name to the tool manager, making it available for the agent to use.
        
        Args:
            tool (str): Name of the tool to add.
        """
        self.__tool_manager.add_tool(tool, self)

    def add_tools(self, tools: list):
        """
        Adds a list of tools to the tool manager
        
        Args:
            tools (list): List of tool names to add.
        """
        self.__tool_manager.add_tools(tools)

    @abstractmethod
    def prompt(self) -> str:
        """
        Abstract method to provide the agent's system prompt or message. 
        Must be implemented by subclasses.

        Returns:
            str: The prompt or message that represents the agent's behavior.
        """
        return ""
    
    def __on_stop(self, result: str=None):
        self.__provider.on_stop(self.__convo, result)

    def __pre_tool_call_callback(self, tool_call):
        pass

    def __add_tools_in_class(self):
        for name, method in inspect.getmembers(self, predicate=inspect.ismethod):
            if hasattr(method, "is_tool"):
                self.add_tool(method.tool_name)
    
    def __on_tool_failed(self, name: str, args: dict, msg: str):
        err = f"Error calling tool: {name}. Are you sure the tool is loaded?"
        return err

    def __post_tool_call_callback(self, result, metadata):
        logger.debug(f"{metadata}\nResult: {result})")
        self.__convo.add_tool_call(metadata, result)
