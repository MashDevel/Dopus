from typing import List, Dict, Any, Optional

def get_tool_str(tool):
    if isinstance(tool, str):
        return tool
    else:
        return tool.tool_name

def strip_array(array: List[Dict[str, Any]], fields: List[str]) -> List[Dict[str, Any]]:
    """
    Strip keys from a list of dictionaries.

    :param array: List of dictionaries.
    :param fields: The fields to remove.
    :return: List of dictionaries with certain keys removed.
    """
    new_array = []
    for item in array:
        new_item = {key: value for key, value in item.items() if key not in fields}
        new_array.append(new_item)
    return new_array