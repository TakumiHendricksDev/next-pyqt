def is_value_true(value:str) -> bool:
    """
    Check if a string is true in boolean value.
    :param value: String to check.
    :return: True or False.
    """
    return value.lower() in ('true', '1', 't', 'y', 'yes')