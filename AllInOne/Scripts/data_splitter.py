"""
    Utility script for splitting a list into multiple smaller lists based on a specified size limit.

    This script provides two functions:
    - get_quantity(data_lst: list) -> int: Calculates the number of smaller lists needed to split the input list based on a size limit.
    - split_data(data_lst: list) -> list: Splits the input list into multiple smaller lists.

    Function Signatures:
    ---------------------
    get_quantity(data_lst: list) -> int:
        Calculates the number of smaller lists needed to split the input list based on a size limit.

    split_data(data_lst: list) -> list:
        Splits the input list into multiple smaller lists.

    Module Usage:
    -------------
    To use this script, call the get_quantity(data_lst) function to calculate the quantity of smaller lists needed.
    Then, call the split_data(data_lst) function to split the input list into smaller lists based on the calculated quantity.
"""

import sys
import math


def get_quantity(data_lst: list) -> int:
    """
    Calculates the number of smaller lists needed to split the input list based on a size limit.

    Args:
        data_lst (list): The input list to be split.

    Returns:
        int: The number of smaller lists needed.
    """
    size_in_bytes = sys.getsizeof(data_lst)
    size = 256 * 1024 * 1024

    return math.ceil(size_in_bytes / size)


def split_data(data_lst: list) -> list:
    """
    Splits the input list into multiple smaller lists.

    Args:
        data_lst (list): The input list to be split.

    Returns:
        list: A list of smaller lists obtained by splitting the input list.
    """
    quantity = get_quantity(data_lst)
    avg = len(data_lst) // quantity
    remainder = len(data_lst) % quantity

    result = []
    start = 0
    for i in range(quantity):
        if i < remainder:
            end = start + avg + 1
        else:
            end = start + avg
        result.append(data_lst[start:end])
        start = end

    return result
