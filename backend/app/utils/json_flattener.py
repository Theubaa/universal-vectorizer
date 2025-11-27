from __future__ import annotations

from typing import Any, Dict, List, Union


def flatten_json(data: Union[Dict[str, Any], List[Any], Any], parent_key: str = "") -> Dict[str, Any]:
    """
    Recursively flattens arbitrarily nested JSON objects and arrays.
    Arrays are indexed and appended to the parent key.
    """

    items: Dict[str, Any] = {}

    if isinstance(data, dict):
        for key, value in data.items():
            new_key = f"{parent_key}.{key}" if parent_key else key
            items.update(flatten_json(value, new_key))
    elif isinstance(data, list):
        for idx, value in enumerate(data):
            new_key = f"{parent_key}[{idx}]" if parent_key else f"[{idx}]"
            items.update(flatten_json(value, new_key))
    else:
        items[parent_key or "value"] = data

    return items


