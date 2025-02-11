from typing import Any
import json

from pydantic import BaseModel


def is_value_true(value:str) -> bool:
    """
    Check if a string is true in boolean value.
    :param value: String to check.
    :return: True or False.
    """
    return value.lower() in ('true', '1', 't', 'y', 'yes')

def cast_value(value: str, target_type: Any) -> Any:
    """Cast value to target_type"""
    if value is None:
        return None

    # Handle common Python types
    if target_type == bool:
        return is_value_true(value)
    elif target_type in (int, float):
        return target_type(value)
    elif target_type == list:
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            return value.split(',')
    elif target_type == dict:
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            return {}

    # Handle Pydantic models
    if isinstance(target_type, type) and issubclass(target_type, BaseModel):
        try:
            data = json.loads(value)
            return target_type(**data)
        except (json.JSONDecodeError, ValueError):
            return None

    # Default to string if no specific casting needed
    return value