# Iterative Agent Guide

## 🎯 What is the Iterative Agent?

The Iterative Agent is an intelligent codebase explorer that can:
- **Think** about what information it needs
- **Plan** a series of searches
- **Execute** searches iteratively  
- **Observe** results and decide next steps
- **Synthesize** all gathered information into a comprehensive answer

It uses a **ReAct-style** (Reason + Act) approach, similar to modern AI agents like AutoGPT.

## 🚀 Quick Start

### 1. Run the Demo

```bash
# Make sure you have an OpenAI API key in .env
echo "OPENAI_API_KEY=sk-your-key" > .env

# Run the demo
python examples/iterative_agent_demo.py
```

Choose from the menu:
- **Demo 1**: Simple single-shot search (default behavior)
- **Demo 2**: Iterative agent with planning
- **Demo 3**: Direct IterativeCodebaseAgent usage
- **Demo 4**: Interactive mode (ask your own questions)

### 2. Test with Existing Tests

```bash
# Run all tests
make test

# Run just the codebase agent tests
pytest tests/test_codebase_agent.py -v
```

### 3. Use in Marimo Notebook

```bash
# Run the codebase agent demo notebook
marimo edit book/marimo/05-codebase-agent-demo.py
```

## 📚 Usage Examples

### Example 1: Basic Iterative Mode

```python
from ontonaut import CodebaseAgent
import openai

# Create agent with iterative mode enabled
agent = CodebaseAgent(
    ai_client=openai.OpenAI(api_key="..."),
    iterative=True,  # 🔥 Enable intelligent agent
    max_iterations=5  # Allow up to 5 search iterations
)

# Ask a complex question
agent.ask("How do I authenticate a user and send them a welcome email?")

# The agent will:
# 1. Search for authentication-related types
# 2. Get details about AuthService
# 3. Search for email-related services
# 4. Get details about EmailService
# 5. Synthesize a complete answer with code examples

print("Agent's thinking process:")
print(agent.context)  # Shows iterations, thinking, actions, observations

print("\nFinal answer:")
print(agent.response)  # Synthesized answer with code examples
```

### Example 2: Direct IterativeCodebaseAgent

For more control, use `IterativeCodebaseAgent` directly:

```python
from ontonaut import IterativeCodebaseAgent
import openai

agent = IterativeCodebaseAgent(
    ai_client=openai.OpenAI(api_key="..."),
    max_iterations=5,
    verbose=True
)

# Stream updates as the agent works
for update in agent.solve("How does user authentication work?"):
    if update["type"] == "thinking":
        print(f"💭 {update['content']}")
    elif update["type"] == "action":
        print(f"🔧 {update['content']}")
    elif update["type"] == "observation":
        print(f"👁️  {update['content']}")
    elif update["type"] == "final_answer":
        print(f"✅ {update['content']}")
```

### Example 3: Custom AI Client

You can use any OpenAI-compatible client:

```python
from ontonaut import CodebaseAgent

# Your company's AI wrapper
class MyCompanyAI:
    def __init__(self, api_key):
        self.api_key = api_key
    
    def chat(self):
        return self
    
    @property
    def completions(self):
        return self
    
    def create(self, model, messages, **kwargs):
        # Your custom implementation
        pass

agent = CodebaseAgent(
    ai_client=MyCompanyAI(api_key="..."),
    iterative=True
)
```

## 🔧 Available Tools

The agent has access to these tools:

1. **`search_types`** - Search for types by query or tags
   ```python
   search_types(query="user", tags=["database"], limit=5)
   ```

2. **`get_type_details`** - Get complete details about a type
   ```python
   get_type_details(type_path="mymodule.User")
   ```

3. **`search_methods_in_type`** - Search methods within a type
   ```python
   search_methods_in_type(type_path="mymodule.User", query="auth")
   ```

4. **`list_all_tags`** - List all available tags
   ```python
   list_all_tags()
   ```

5. **`get_type_count`** - Get registry statistics
   ```python
   get_type_count()
   ```

## 🎨 Agent Output Visualization

When `iterative=True`, the agent's `context` field shows:

```
🔄 Iteration 1/5
💭 Thinking: I need to search for authentication-related types...
🔧 Action: Using tool: search_types with args: {"query": "auth"}
👁️  Observation: Found 2 types: User, AuthService

🔄 Iteration 2/5
💭 Thinking: Let me get details about AuthService...
🔧 Action: Using tool: get_type_details with args: {"type_path": "mymodule.AuthService"}
👁️  Observation: AuthService has methods: login, logout, validate_token

✅ Final Answer: [Synthesized answer with code examples]
```

## 🧪 Testing Your Own Codebase

1. **Register your types:**

```python
from ontonaut import register_type, IndexTag

class MyTags(IndexTag):
    DATABASE = "database"
    API = "api"

class User:
    """User model."""
    pass

register_type(
    typ=User,
    tags=[MyTags.DATABASE],
    instructions="Main user model for authentication"
)
```

2. **Create an agent:**

```python
from ontonaut import CodebaseAgent
import openai

agent = CodebaseAgent(
    ai_client=openai.OpenAI(api_key="..."),
    iterative=True
)
```

3. **Ask questions:**

```python
agent.ask("How do I create and save a new user?")
print(agent.response)
```

## 📊 Comparison: Simple vs Iterative

| Feature | Simple Mode | Iterative Mode |
|---------|------------|----------------|
| Searches | Single search | Multiple iterations |
| Planning | No planning | AI plans searches |
| Context | Search results only | Full agent reasoning |
| Best for | Simple queries | Complex multi-step queries |
| Speed | Faster | Slower but more thorough |

## 🐛 Troubleshooting

### Agent keeps running out of iterations

Increase `max_iterations`:
```python
agent = CodebaseAgent(ai_client=client, iterative=True, max_iterations=10)
```

### AI client errors

Make sure your client implements the OpenAI interface:
```python
# Must have: client.chat.completions.create()
# Or be a callable that returns text/generator
```

### No results found

Make sure you've registered your types:
```python
from ontonaut import get_registry
print(f"Registered types: {len(get_registry())}")
```

## 💡 Tips & Best Practices

1. **Start with simple mode** to understand basic search, then try iterative
2. **Use specific tags** when registering types for better searchability
3. **Add instructions** to help the agent understand what each type does
4. **Monitor iterations** in the context to see agent's reasoning
5. **Adjust max_iterations** based on query complexity

## 📖 Further Reading

- [Indexing System Documentation](./docs/INDEXING_SYSTEM.md)
- [Example Notebooks](./book/marimo/)
- [API Reference](./README.md)

