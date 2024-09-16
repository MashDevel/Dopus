### Overview

In this tutorial, we'll build an agent that manages a todo list. The full code can be found at the bottom of this page.

### Installation

To install dopus run:

```bash
pip install dopus
```

Let's also install `python-dotenv` and `openai`:

```bash
pip install python-dotenv openai
```

### Setup

Create a `.env` file with your OpenAI API key:

```bash
OPENAI_API_KEY={YOUR_API_KEY_HERE}
```

### Define the Agent

Let's define our todo list agent with some fake TODO todos:

```python
# First load the environment variables
import os
import dotenv
dotenv.load_dotenv()

from dopus.provider import OpenAI
from dopus.core import Agent, tool

class TodoAgent(Agent):
    def __init__(self):
        super().__init__()  # initialize the base Agent class
        # fake todos
        self.todos = [
            {"todo": "Buy groceries", "completed": False},
            {"todo": "Wash dishes", "completed": False}
            {"todo": "Finish project report", "completed": False}
        ]
```

### Setting the Prompt

All agents must override the `prompt` function. This sets the top-level or system prompt for the LLM.

```python
class TodoAgent(Agent):

    # Previous code...

    def prompt(self):
        return "You are an AI that manages a to-do list."
```

### Giving the Agent Tools

The Dopus framework is built around defining tools for an agent to use. A tool is essentially a function using the `@tool` decorator.

Here's an example of creating an `add_todos` tool:

```python
class TodoAgent(Agent):

    # Previous code...

    @tool
    def add_todo(self, todo):
        """
        Add a new todo to the list
        
        Args:
            todo (str): The todo to add to the list.
        """
        self.todos.append({"todo": todo, "completed": False})
        return f"Todo '{todo}' added to the list."
```

!!! info "Info"
    The **return** of a tool function is a **string** representing the **result of the tool call**.
    This result is **automatically** added to the **context window** of the LLM.
    
    So in this case:
    ```python
    return f"Todo '{todo}' added to the list."
    ```
     We are telling the LLM that the tool call was successful, and the todo has been added to the list.

Let's give the agent two more tools. A `send_message` tool so the agent to communitcate with the user and a `wait` tool to break out of the **agentic loop**.

```python
class TodoAgent(Agent):

    # Previous code...

    @tool
    def send_message(self, message):
        """
        Communicate with the user by sending a message
        
        Args:
            message (str): The message to send
        """
        print(f"\nAgent: {message}")
        return "Message Sent Successfully"

    @tool
    def wait(self):
        """
        Call this when you are done with the todo 
        or need to wait for the user
        """
        self.stop() # break the agentic loop
```

!!! Warning "Warning"
    At **least one** of the agents tools **must call** `self.stop()` in order to break the **agentic loop**.
    If there are no tools that call `self.stop()` or if the LLM never calls a tool containing `self.stop()`,
    the agent will **loop infinitely**.

### Running the Agent

Let's write a quick loop so we can try out our agent.

```python

# TodoAgent class above ^^

provider = OpenAI(os.getenv('OPENAI_API_KEY'))
agent = TodoAgent(provider)
while True:
    message = input("\nUser: ")
    if message:
        agent.run(message)
```

After running this code and talking with the agent, you should have output that looks something like this:

```text
User: Hello

Agent: Hello! How can I assist you with your to-do list today?

User: Can you add a todo for me?

Agent: Sure! What todo would you like to add?

User: Count the r's in strawberry     

Agent: The todo 'Count the r's in strawberry' has been added to your to-do list.
```

Now we have everything we need to complete the agent! We just need to build more tools for managing the todo list.

### Add More Tools

#### List todos Tool

```python
@tool
def list_todos(self):
    """
    List all todos in the to-do list
    """
    if not self.todos:
        return "Your to-do list is empty."
    
    todo_list = [
        f"{i}. {todo['todo']} - {'completed' if todo['completed'] else 'not completed'}"
        for i, todo in enumerate(self.todos, 1)
    ]
    return "\n".join(todo_list)
```

#### Complete todo Tool

```python
@tool
def complete_todo(self, todo_number: int):
    """
    Mark a todo as completed
    
    Args:
        todo_number (int): The number of the todo to mark as completed
    """
    if not self._is_valid_todo_number(todo_number):
        return self._print_message("Error: Invalid todo number.")
    
    todo = self.todos[todo_number - 1]
    todo["completed"] = True
    return f"todo '{todo['todo']}' marked as completed."

# Helper function
def _is_valid_todo_number(self, todo_number: int) -> bool:
    return 0 < todo_number <= len(self.todos)
```

#### Delete todo Tool

```python
@tool
def delete_todo(self, todo_number: int) -> str:
    """
    Delete a todo from the to-do list
    
    Args:
        todo_number (int): The number of the todo to delete
    """
    if not self._is_valid_todo_number(todo_number):
        return "Error: Invalid todo number."
```

### Conclusion

Putting it all together and running the agent your conversation should look something like this:

```text
User: Show me my todos

Agent: Here are your todos:

1. Buy groceries - not completed
2. Finish project report - not completed
3. Call mom - not completed
4. Schedule dentist appointment - not completed

User: I called my mom earlier today

Agent: todo 'Call mom' has been marked as completed.

User: The project report got cancelled, oh and my boss wants to do dinner tonight 

Agent: todo 'Finish project report' has been deleted and 'Dinner with boss' has been added to your to-do list.

User: Can you show me the updated list?

Agent: Here is your updated to-do list:

1. Buy groceries - not completed
2. Call mom - completed
3. Schedule dentist appointment - not completed
4. Dinner with boss - not completed
```

In this tutorial, we built a to-do list manager using the Dopus framework. We covered environment setup, defining the agent, and creating tools for adding, listing, completing, and deleting todos. Thank you for following along, enjoy using Dopus!

### Full Code
```python
import os
import dotenv
dotenv.load_dotenv()

from dopus.provider import OpenAI
from dopus.core import Agent, tool

class TodoAgent(Agent):
    def __init__(self, provider):
        super().__init__(provider)
        self.todos = [
            {"todo": "Buy groceries", "completed": False},
            {"todo": "Wash dishes", "completed": False},
            {"todo": "Finish project report", "completed": False}
        ]

    @tool
    def add_todo(self, todo):
        """
        Add a new todo to the to-do list
        
        Args:
            todo (str): The todo to add to the list.
        """
        self.todos.append({"todo": todo, "completed": False})
        return f"todo '{todo}' added to the list."

    @tool
    def list_todos(self):
        """
        List all todos in the to-do list
        """
        if not self.todos:
            return "Your to-do list is empty."

        todo_list = [
            f"{i}. {todo['todo']} - {'completed' if todo['completed'] else 'not completed'}"
            for i, todo in enumerate(self.todos, 1)
        ]
        return "\n".join(todo_list)

    @tool
    def complete_todo(self, todo_number: int):
        """
        Mark a todo as completed
        
        Args:
            todo_number (int): The number of the todo to mark as completed
        """
        if not self._is_valid_todo_number(todo_number):
            return self._print_message("Error: Invalid todo number.")

        todo = self.todos[todo_number - 1]
        todo["completed"] = True
        return f"todo '{todo['todo']}' marked as completed."

    @tool
    def delete_todo(self, todo_number: int) -> str:
        """
        Delete a todo from the to-do list
        
        Args:
            todo_number (int): The number of the todo to delete
        """
        if not self._is_valid_todo_number(todo_number):
            return "Error: Invalid todo number."

        deleted_todo = self.todos.pop(todo_number - 1)
        return f"todo '{deleted_todo['todo']}' deleted from the list."

    @tool
    def wait(self) -> None:
        """
        Call this when you are done with your todo or need to wait for the user
        """
        self.stop()

    @tool
    def send_message(self, message):
        """
        Communicate with the user by sending a message
        
        Args:
            message (str): The message to send
        """
        print(f"\nAgent: {message}")
        return "Message Sent Successfully"

    def prompt(self) -> str:
        return "You are an AI that manages a to-do list."

    def _is_valid_todo_number(self, todo_number: int) -> bool:
        return 0 < todo_number <= len(self.todos)

provider = OpenAI(os.getenv('OPENAI_API_KEY'))
agent = TodoAgent(provider)
while True:
    message = input("\nUser: ")
    if message:
        agent.run(message)
```

