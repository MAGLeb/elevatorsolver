import random

import numpy as np

from test_generator.utils import inverse_cdf


def generate_time_call(n):
    calls = []
    uniform_random_values = np.random.uniform(0, 1, n)
    for u in uniform_random_values:
        custom_random_value = inverse_cdf(u)
        hour = int(custom_random_value)
        minutes = int(60 * (custom_random_value - hour))
        calls.append(f"{hour:02}:{minutes:02}")

    return calls


def generate_levels(n, max_level):
    times_half = int(n / 2)
    levels = [random.randint(2, max_level) for _ in range(times_half)]
    tb = [[level, 1] for level in levels]
    bt = [list(reversed(pair)) for pair in tb]
    return tb, bt


def choose_level(tb, bt, p, tb_i, bt_i):
    is_top_to_bottom = random.random() < 1 - p

    if tb_i >= len(tb):
        level = bt[bt_i]
        bt_i += 1
    elif bt_i >= len(bt) or is_top_to_bottom:
        level = tb[tb_i]
        tb_i += 1
    else:
        level = bt[bt_i]
        bt_i += 1

    return level, tb_i, bt_i


def generate_test_sample(max_level, number_flat_in_level, human_per_flat, average_call_per_human, filename):
    n = max_level * number_flat_in_level * human_per_flat * average_call_per_human
    if n % 2 == 1:
        n += 1
    times = generate_time_call(n)
    times_sorted = sorted(times)
    top_bottom_levels, bottom_top_levels = generate_levels(n, max_level)
    top_bottom_index = 0
    bottom_top_index = 0

    with open(filename, 'w') as f:
        f.write(f"{n} {max_level} {number_flat_in_level} {human_per_flat} {average_call_per_human}\n")
        for i in range(n):
            probability = i / n
            level_pair, top_bottom_index, bottom_top_index = choose_level(top_bottom_levels, bottom_top_levels,
                                                                          probability,
                                                                          top_bottom_index, bottom_top_index)
            f.write(f"{times_sorted[i]} {level_pair[0]} {level_pair[1]}\n")
