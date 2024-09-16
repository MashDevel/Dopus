### Overview

In this getting started guide we will build a basic "Hello World" agent. The full code can be found at the bottom of this page.

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
### Hello World Agent

Let's create a simple Hello World agent that uses tools and interacts with the user. 

Start by loading the environment variables:

```python
# First load the environment variables
import os
import dotenv
dotenv.load_dotenv()
```

Then let's define our agent and set the prompt:

```python
from dopus.provider import OpenAI
from dopus.core import Agent, tool

class HelloAgent(Agent):

    def prompt(self):
        return "You are a friendly AI that greets users."
```

Then we will add a tool to enable the agent to say hello:

```python
from dopus.core import Agent, tool

class HelloAgent(Agent):

    # Previous code...

    @tool
    def say_hello(self):
        """Greet the user"""
        print(f"Agent: Hello World!")
        self.stop() # Stop the agentic loop
```

Then we will instantiate the openai provider and 
run the agent and watch it say hello!

```python
provider = OpenAI(os.getenv('OPENAI_API_KEY'))
agent = HelloAgent(provider)
agent.run()
```

Full Code:

```python
# First load the environment variables
import os
import dotenv
dotenv.load_dotenv()

from dopus.provider import OpenAI
from dopus.core import Agent, tool

class HelloAgent(Agent):

    def prompt(self):
        return "You are a friendly AI that greets users."

    @tool
    def say_hello(self):
        """Greet the user"""
        print(f"Agent: Hello World!")
        self.stop() # Stop the agentic loop

provider = OpenAI(os.getenv('OPENAI_API_KEY'))
agent = HelloAgent(provider)
agent.run()
```
Output:
```bash
Agent: Hello World!
```

And that's it! Check out the tutorials for more in-depth examples.