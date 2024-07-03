import math
import sys


def get_quantity(data_lst: list) -> int:
    """
    Calculates the number of chunks required to split the data list based on size limit.

    Args:
        data_lst (list): The list of data to be split.

    Returns:
        int: The number of chunks needed.
    """
    size_in_bytes = sys.getsizeof(data_lst)
    size_limit_bytes = 256 * 1024 * 1024  # 256 MB

    return math.ceil(size_in_bytes / size_limit_bytes)


def split_data(data_lst: list) -> list:
    """
    Splits the data list into chunks based on a size limit.

    Args:
        data_lst (list): The list of data to be split.

    Returns:
        list: A list of lists, each containing a chunk of the original data.
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
