def is_power_of_two(num):
    """
    Check if num is power of two
    """
    return ((num & (num - 1)) == 0) and num > 0
