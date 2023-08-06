"""
GP library focusing on randomness.
"""

import random
import uuid


def generate_random_number(start_range, end_range, amount_of_numbers=1):
    """
    Generates random number between start_range and end_range (including end_range).
    Therefor generate random number | 1 | 9 can generate 9.

    Usage:
    | generate random number | 1 | 9 |
    returns a random number between 1 and 9

    | generate random number | 10 | 150 |
    return a random number between 10 and 150

    | generate random number | 1 | 100 | 5 |
    returns a list of 5 random unique numbers between 1 and 100 i.e. [1, 13, 45, 32, 87]
    """
    try:
        start_range = int(start_range)
        end_range = int(end_range)
        amount_of_numbers = int(amount_of_numbers)
    except ValueError:
        raise ValueError("Unable to convert one or more arguments to integers. All arguments have to be numbers.")

    try:
        if amount_of_numbers == 1:
            return random.sample(xrange(start_range, end_range + 1), amount_of_numbers)[0]
        return random.sample(xrange(start_range, end_range + 1), amount_of_numbers)
    except ValueError:
        raise ValueError("Unable to generate %s unique number/s from range %s to %s" % (
                amount_of_numbers, start_range, end_range))


def generate_uuid():
    """
    Generates a random string in the format of uuid.
    """
    return uuid.uuid4()
