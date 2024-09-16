import inspect
from .tool_registry import tool_registry
from pydantic import BaseModel
from enum import Enum

def __store_tool(name, description, parameters=None, required=None, function=None):
    return {
        "name": name,
        "description": description,
        "properties": parameters or {},
        "required": required or [],
        "function": function,
    }

def _parse_docstring_args(docstring, keyword="Args"):
    param_descriptions = {}
    if docstring:
        doc_lines = docstring.split('\n')
        args_section = False
        for line in doc_lines:
            stripped_line = line.strip()
            if stripped_line.startswith(keyword):
                args_section = True
                continue
            if args_section:
                if not stripped_line:
                    break
                try:
                    if ':' in stripped_line:
                        param_name_type, param_desc = stripped_line.split(":", 1)
                        if '(' in param_name_type and ')' in param_name_type:
                            param_name, param_type = param_name_type.split("(", 1)
                            param_name = param_name.strip()
                            param_type = param_type.rstrip(")").strip()
                        else:
                            param_name = param_name_type.strip()
                        param_descriptions[param_name] = param_desc.strip()
                except ValueError as e:
                    print(f"Error parsing parameter description: {stripped_line}. Error: {e}")
    return param_descriptions

def _translate_type(param_name, param_type, param_description): 
    if isinstance(param_type, type) and issubclass(param_type, Enum):
        return {
            "type": "string",
            "enum": [e.value for e in param_type],
            "description": param_description
        }
    if isinstance(param_type, type):
        if hasattr(param_type, '__annotations__'):
            properties = {}
            required = []
            args_section = _parse_docstring_args(inspect.getdoc(param_type) or "", keyword="Attributes")
            for field_name, field_type in param_type.__annotations__.items():
                field_description = args_section.get(field_name, f"{field_name} field")
                field_schema = _translate_type(field_name, field_type, field_description)
                properties[field_name] = field_schema
                required.append(field_name)
            return {
                "type": "object",
                "properties": properties,
                "required": required,
                "description": param_description
            }
    if hasattr(param_type, '__origin__') and param_type.__origin__ in [list, List]:
        return {
            "type": "array",
            "items": _translate_type(param_name, param_type.__args__[0], param_description),
            "description": param_description
        }
    type_mapping = {
        int: "integer",
        float: "number",
        str: "string",
        bool: "boolean",
    }
    return {
        "type": type_mapping.get(param_type, "string"),
        "description": param_description
    }

def _get_function_params(func):
    sig = inspect.signature(func)
    type_hints = func.__annotations__
    
    parameters = {}
    required = []
    
    docstring = inspect.getdoc(func)
    param_descriptions = _parse_docstring_args(docstring)

    for param_name, param in sig.parameters.items():
        if param_name == "self":
            continue
        param_type = type_hints.get(param_name, str)
        param_description = param_descriptions.get(param_name, f"{param_name} parameter")
        schema = _translate_type(param_name, param_type, param_description)
        parameters[param_name] = schema
        required.append(param_name)

    return parameters, required

def __get_function_description(func):
    docstring = inspect.getdoc(func)
    if not docstring:
        return ""
    doc_lines = docstring.split('\n')
    for line in doc_lines:
        stripped_line = line.strip()
        if stripped_line:
            return stripped_line
    return ""

def tool(func=None):
    """
    Decorator to register a function as a tool.

    This decorator adds metadata to the function and registers it in the tool registry.

    Returns:
        callable: The decorated function.
    """
    if func is None:
        return lambda f: tool(f)

    func.is_tool = True
    func.tool_name = func.__qualname__.replace('.', '_')
    parameters, required = _get_function_params(func)
    tool_data = __store_tool(
        name=func.__name__,
        description=__get_function_description(func),
        parameters=parameters,
        required=required,
        function=func,
    )
    tool_registry[func.tool_name] = tool_data
    return func