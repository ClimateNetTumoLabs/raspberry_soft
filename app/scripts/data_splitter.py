import math
import sys


def get_quantity(data_lst: list) -> int:
    """
    Calculates the number of sublists needed to split a given list into chunks that fit within a specified size limit.

    Args:
        data_lst (list): The list of data to be split.

    Returns:
        int: The number of sublists needed to split the data list.

    Note:
        The size limit for each sublist is set to 256 MB.

    Raises:
        None
    """
    size_in_bytes = sys.getsizeof(data_lst)
    size_limit_bytes = 256 * 1024 * 1024

    return math.ceil(size_in_bytes / size_limit_bytes)


def split_data(data_lst: list) -> list:
    """
    Splits a given list of data into smaller sublists to fit within a specified size limit.

    Args:
        data_lst (list): The list of data to be split.

    Returns:
        list: A list of sublists containing the split data.

    Note:
        The size limit for each sublist is set to 256 MB.

    Raises:
        None
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
