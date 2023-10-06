import os.path
import random

import numpy as np

from case_generation.time_distribution import DistributionCalculator
from core.utils.environment import Environment


def seconds_format(random_value):
    return int(random_value * 86400 / 24)


def generate_time_call(n):
    calculator = DistributionCalculator()
    calls = []
    uniform_random_values = np.random.uniform(0, 1, n)
    for u in uniform_random_values:
        custom_random_value = calculator.inverse_cdf(u)
        seconds = seconds_format(custom_random_value)
        calls.append(seconds)

    return calls


def generate_weight_passenger():
    return int(random.normalvariate(70, 15))


def choose_level(tb, bt, p, tb_i, bt_i):
    is_top_to_bottom = random.random() < 1 - p

    if tb_i >= len(tb):
        level_pair = bt[bt_i]
        bt_i += 1
    elif bt_i >= len(bt) or is_top_to_bottom:
        level_pair = tb[tb_i]
        tb_i += 1
    else:
        level_pair = bt[bt_i]
        bt_i += 1

    return level_pair, tb_i, bt_i


def generate_levels(n, times):
    times_half = int(n / 2)
    levels = [random.randint(2, Environment.LEVELS) for _ in range(times_half)]
    tb = [[level, 1] for level in levels]
    bt = [list(reversed(pair)) for pair in tb]
    tb = random.sample(tb, len(tb))
    bt = random.sample(bt, len(bt))

    level_pairs = []
    top_bottom_index = 0
    bottom_top_index = 0

    for i in range(n):
        if times[i] < 18000:
            probability = 0.2
        elif times[i] < 36000:
            probability = 0.9
        elif times[i] < 57600:
            probability = 0.5
        else:
            probability = 0.2
        level_pair, top_bottom_index, bottom_top_index = choose_level(tb, bt, probability,
                                                                      top_bottom_index, bottom_top_index)
        level_pairs.append(level_pair)
    return level_pairs


def generate_test_sample(filename):
    n = int(Environment.LEVELS * Environment.PASSABILITY)
    if n % 2 == 1:
        n += 1
    times = generate_time_call(n)
    level_pairs = generate_levels(n, times)

    with open(filename, 'w') as f:
        f.write(f"{n}\n")
        for i in range(n):
            weight_of_passenger = generate_weight_passenger()
            f.write(f"{times[i]} {level_pairs[i][0]} {level_pairs[i][1]} {weight_of_passenger}\n")


def generate_tests(path, filename, number_tests):
    for j in range(number_tests):
        path_filename = f"{path}/{filename}_{j + 1}.txt"

        if not os.path.exists(path_filename):
            print(f"Generating test {j + 1} for {filename} to {path_filename}")
            generate_test_sample(path_filename)
        else:
            print(f"Test {j + 1} for {filename} exists.")
