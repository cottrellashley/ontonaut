# CodeEditor Widget

The `CodeEditor` is an interactive code editor widget for marimo that allows custom code execution with pluggable backends.

## Overview

```python
from ontonaut import CodeEditor, PythonExecutor

editor = CodeEditor(
    executor=PythonExecutor(),
    code="x = 10\nresult = x * 2",
    theme="dark"
)
editor
```

## Features

- ✅ **Syntax Highlighting** - Beautiful, language-aware color coding powered by CodeMirror 6
  - Keywords in bold red/pink
  - Strings in blue
  - Functions in purple
  - Comments in gray and italic
  - Numbers in blue
  - Full bracket matching and active line highlighting
- ✅ **Line Numbers** - Toggle on/off with gutter highlighting
- ✅ **Multiple Languages** - Python, JavaScript, JSON with proper syntax highlighting
- ✅ **Custom Executors** - Plug in your own execution logic
- ✅ **Real-time Errors** - Immediate error feedback with red highlighting
- ✅ **Keyboard Shortcuts** - Cmd/Ctrl+Enter to run, tab indentation, and more
- ✅ **Themes** - Light and dark modes (OneDark for dark theme)
- ✅ **Read-only Mode** - Display code without editing
- ✅ **Professional Editor** - Full CodeMirror experience with history, selections, and more

## Basic Usage

### Simple Python Execution

```python
from ontonaut import CodeEditor, PythonExecutor

editor = CodeEditor(
    executor=PythonExecutor(),
    code="print('Hello, World!')\nx = 42"
)
editor
```

### With Initial Code

```python
initial_code = """
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

result = fibonacci(10)
"""

editor = CodeEditor(
    executor=PythonExecutor(),
    code=initial_code,
    language="python"
)
```

## Configuration

### Constructor Parameters

```python
CodeEditor(
    executor: Optional[Callable[[str], Any]] = None,
    code: str = "",
    language: str = "python",
    theme: str = "light",
    placeholder: str = "Write your code here...",
    show_line_numbers: bool = True,
    read_only: bool = False
)
```

**Parameters:**
- `executor`: Function that takes code string and returns result
- `code`: Initial code content
- `language`: Language for syntax highlighting (python, javascript, json, etc.)
- `theme`: UI theme ("light" or "dark")
- `placeholder`: Placeholder text when empty
- `show_line_numbers`: Show/hide line numbers
- `read_only`: Make editor read-only

### Attributes

```python
editor.code          # Current code (get/set)
editor.output        # Last execution output
editor.error         # Last error message
editor.is_executing  # True if currently executing
editor.language      # Current language
editor.theme         # Current theme
```

## Executors

### Built-in Executors

#### PythonExecutor

Execute Python code:

```python
from ontonaut import CodeEditor, PythonExecutor

editor = CodeEditor(
    executor=PythonExecutor(),
    code="x = 10\ny = 20\nresult = x + y"
)
```

With custom globals/locals:

```python
executor = PythonExecutor(
    globals_dict={"math": __import__("math")},
    locals_dict={"pi": 3.14159}
)

editor = CodeEditor(
    executor=executor,
    code="import math\nresult = math.sqrt(16)"
)
```

#### JSONExecutor

Format and validate JSON:

```python
from ontonaut import CodeEditor, JSONExecutor

editor = CodeEditor(
    executor=JSONExecutor(indent=2),
    code='{"name":"John","age":30}',
    language="json"
)
```

#### CalculatorExecutor

Simple calculator with variables:

```python
from ontonaut import CodeEditor, CalculatorExecutor

editor = CodeEditor(
    executor=CalculatorExecutor(),
    code="x = 10\ny = 20\nx * y + 5",
    language="calculator"
)
```

#### RegexExecutor

Test regular expressions:

```python
from ontonaut import CodeEditor, RegexExecutor

editor = CodeEditor(
    executor=RegexExecutor(),
    code="pattern: \\d+\ntext: There are 42 apples",
    language="regex"
)
```

### Custom Executors

Create your own executor:

```python
def my_custom_executor(code: str) -> str:
    """Execute custom DSL"""
    # Your custom logic here
    if "hello" in code.lower():
        return "Hello back!"
    return f"Executed: {code}"

editor = CodeEditor(
    executor=my_custom_executor,
    code="hello world",
    language="custom"
)
```

Class-based executor:

```python
class SQLExecutor:
    def __init__(self, connection_string: str):
        self.conn = create_connection(connection_string)

    def __call__(self, code: str) -> str:
        cursor = self.conn.execute(code)
        return format_results(cursor.fetchall())

executor = SQLExecutor("sqlite:///mydb.db")
editor = CodeEditor(executor=executor, language="sql")
```

## Methods

### execute()

Execute code programmatically:

```python
editor = CodeEditor(executor=PythonExecutor())

# Execute specific code
result = editor.execute("x = 10\nx * 2")
print(result)  # 20

# Execute current editor code
result = editor.execute()
```

### clear()

Clear all content and output:

```python
editor.clear()
# Clears: code, output, errors
```

### set_code()

Set editor content:

```python
editor.set_code("new code here")
```

### get_code()

Get current code:

```python
code = editor.get_code()
```

## Keyboard Shortcuts

- **Cmd/Ctrl + Enter**: Execute code
- **Tab**: Smart indentation (context-aware)
- **Cmd/Ctrl + Z**: Undo
- **Cmd/Ctrl + Shift + Z**: Redo
- **Cmd/Ctrl + /**: Toggle line comment (language-dependent)
- **Bracket Matching**: Automatic highlighting of matching brackets

## Syntax Highlighting

The editor uses **CodeMirror 6** for professional-grade syntax highlighting that makes your code more readable and helps catch errors visually.

### Color Scheme

#### Light Theme
- **Keywords** (`def`, `if`, `return`, `class`, etc.): Bold red/pink (#d73a49)
- **Strings** and **docstrings**: Dark blue (#032f62)
- **Numbers**: Blue (#005cc5)
- **Comments**: Gray italic (#6a737d)
- **Functions**: Purple bold (#6f42c1)
- **Class names**: Purple bold (#6f42c1)
- **Operators**: Red (#d73a49)
- **Brackets**: Blue (#005cc5)
- **Active line**: Light gray background

#### Dark Theme (OneDark)
- **Keywords**: Orange/red
- **Strings**: Green
- **Numbers**: Orange
- **Comments**: Gray italic
- **Functions**: Blue/purple
- **Operators**: Cyan
- **Active line**: Subtle gray background

### Supported Languages

Full syntax highlighting support:
- **Python** - All Python 3 syntax including f-strings, type hints, decorators
- **JavaScript** - ES6+, JSX, modern JavaScript features
- **JSON** - Proper JSON validation with error highlighting
- More languages can be added via CodeMirror language packs

### Example

```python
# This code demonstrates syntax highlighting
from ontonaut import CodeEditor, PythonExecutor

code = '''
def calculate_fibonacci(n: int) -> int:
    """Calculate the nth Fibonacci number."""
    if n <= 1:
        return n
    else:
        # Recursive calculation
        return calculate_fibonacci(n-1) + calculate_fibonacci(n-2)

# Test with different values
for i in range(10):
    result = calculate_fibonacci(i)
    print(f"F({i}) = {result}")
'''

editor = CodeEditor(
    executor=PythonExecutor(),
    code=code,
    language="python",
    theme="light"
)
editor
```

In this example, you'll see:
- `def`, `return`, `if`, `else`, `for`, `in` highlighted as keywords
- The docstring `"""Calculate..."""` in blue
- The f-string `f"F({i}) = {result}"` with proper string highlighting
- Comments `# Recursive calculation` in gray italic
- Function names `calculate_fibonacci`, `range`, `print` in purple
- Numbers `1`, `2`, `10` in blue
- Type hints `: int` and `-> int` with proper syntax coloring

## Styling

### Themes

```python
# Light theme
editor = CodeEditor(executor=PythonExecutor(), theme="light")

# Dark theme
editor = CodeEditor(executor=PythonExecutor(), theme="dark")

# Change theme dynamically
editor.theme = "dark"
```

### Languages

Supported languages for syntax highlighting:
- `python`
- `javascript`, `typescript`
- `json`
- `sql`
- `bash`, `shell`
- `calculator`
- `regex`
- `text` (no highlighting)

```python
editor = CodeEditor(
    executor=my_executor,
    language="javascript",
    code="const x = 10;\nconsole.log(x);"
)
```

## Advanced Usage

### Read-only Display

Show code without allowing edits:

```python
editor = CodeEditor(
    executor=PythonExecutor(),
    code="# This code is read-only\nprint('Hello')",
    read_only=True
)
```

### Hide Line Numbers

```python
editor = CodeEditor(
    executor=PythonExecutor(),
    show_line_numbers=False
)
```

### Error Handling

The editor automatically catches and displays errors:

```python
editor = CodeEditor(
    executor=PythonExecutor(),
    code="x = 10\nprint(y)"  # y is undefined
)
# Error will be displayed in red below output
```

Access errors programmatically:

```python
editor.execute()
if editor.error:
    print(f"Execution failed: {editor.error}")
```

### Reactive Updates

In marimo, the editor is reactive:

```python
import marimo as mo

# Create editor
editor = CodeEditor(executor=PythonExecutor())

# Use output in other cells
mo.md(f"Last result: {editor.output}")
```

## Examples

### Multi-line Python

```python
code = """
def factorial(n):
    if n <= 1:
        return 1
    return n * factorial(n - 1)

# Calculate factorial of 5
result = factorial(5)
"""

editor = CodeEditor(
    executor=PythonExecutor(),
    code=code
)
```

### JSON Formatter

```python
json_code = """{
  "users": [
    {"name": "Alice", "age": 30},
    {"name": "Bob", "age": 25}
  ]
}"""

editor = CodeEditor(
    executor=JSONExecutor(indent=2),
    code=json_code,
    language="json"
)
```

### Calculator with Variables

```python
calc_code = """
# Define variables
price = 100
tax_rate = 0.08
quantity = 3

# Calculate total
subtotal = price * quantity
tax = subtotal * tax_rate
total = subtotal + tax
"""

editor = CodeEditor(
    executor=CalculatorExecutor(),
    code=calc_code,
    language="calculator"
)
```

### Regex Matcher

```python
regex_code = """
pattern: \\b[A-Z][a-z]+\\b
text: Hello World from Python
"""

editor = CodeEditor(
    executor=RegexExecutor(),
    code=regex_code,
    language="regex"
)
```

## Tips & Best Practices

1. **Choose the right executor** for your use case
2. **Provide initial code** to guide users
3. **Use appropriate language** for syntax highlighting
4. **Handle errors gracefully** in custom executors
5. **Consider read-only mode** for documentation
6. **Match theme** with your notebook style
7. **Test executors** independently before use

## Common Issues

### Executor Not Working

Ensure your executor:
- Takes a single `str` parameter
- Returns a value (or None)
- Handles exceptions internally (optional)

```python
def good_executor(code: str) -> str:
    try:
        # Your logic
        return result
    except Exception as e:
        return f"Error: {e}"
```

### Syntax Highlighting Wrong

Set the correct language:

```python
editor.language = "javascript"
```

### Output Not Showing

Check if executor returns a value:

```python
def bad_executor(code: str):
    eval(code)  # No return!

def good_executor(code: str):
    return eval(code)  # Returns result
```

## See Also

- [Executors Guide](./executors.md)
- [Custom Executors](./custom-executors.md)
- [Styling Guide](./styling.md)
- [Examples](../../examples/basic_usage.py)
