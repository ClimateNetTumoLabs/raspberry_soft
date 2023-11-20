import sys
import math


def get_quantity(data_lst):
    size_in_bytes = sys.getsizeof(data_lst)
    size = 256 * 1024 * 1024

    return math.ceil(size_in_bytes / size)


def split_data(data_lst):
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