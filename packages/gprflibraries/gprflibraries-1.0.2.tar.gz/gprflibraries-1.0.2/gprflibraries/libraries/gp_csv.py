"""
GP library for working on csv files.
"""

import csv


def read_csv(file_path):
    """
    Reads from a given csv and returns a generator object.

    Usage:
    Say we have the following csv file:

    | id | item  | quantity |
    | 1  | lamp  | 2        |
    | 2  | chair | 4        |
    | 3  | table | 1        |

    and want to iterate over it:

    | ${var} | read csv | /home/user/items.csv |
    | :FOR | ${row} | IN | @{var} |
    | \    log to console | ${row} |

    This will log to console every row of the csv, each row as a list. Therefor the following will be logged to console:
    | [id, item, quantity] |
    | [1, lamp, 2] |
    | [2, chair, 4] |
    | [3, table, 1] |
    """
    with open(file_path, "rb") as f:
        csv_reader = csv.reader(f)
        for row in csv_reader:
            yield row
