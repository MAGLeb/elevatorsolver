import math


def boolean_array_to_integer(a):
    return int(''.join(map(str, a)), 2)


def calculate_exploration_fall(number_commands):
    """
    First fifth part of all commands, we do exploration then move to take best action from table.
    """
    t = math.log10(0.5)
    y = int(number_commands / 20)
    return 10 ** (t / y)
