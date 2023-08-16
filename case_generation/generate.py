import random

import numpy as np

from case_generation.time_distribution import inverse_cdf


def hour_minute_second_format(random_value):
    hours = int(random_value)
    minutes = int(60 * (random_value - hours))
    seconds = int(60 * (60 * (random_value - hours) - minutes))
    return hours, minutes, seconds


def custom_time_sort(time_str):
    # sort strings from 6:00 to 5:59
    hours, minutes, seconds = map(int, time_str.split(":"))
    if hours < 6:
        return 24 + hours, minutes, seconds
    else:
        return hours, minutes, seconds


def custom_seconds_sort(seconds):
    # sort seconds from 6 * 60 * 60 = 21600 -> 21599
    if seconds < 21600:
        return seconds + 86400
    else:
        return seconds


def seconds_format(random_value):
    return int(random_value / 24 * 86400)


def generate_time_call(n, is_seconds_format: bool = True):
    calls = []
    uniform_random_values = np.random.uniform(0, 1, n)
    for u in uniform_random_values:
        custom_random_value = inverse_cdf(u)
        if is_seconds_format:
            seconds = seconds_format(custom_random_value)
            calls.append(seconds)
        else:
            hours, minutes, seconds = hour_minute_second_format(custom_random_value)
            calls.append(f"{hours:02}:{minutes:02}:{seconds:02}")
    if is_seconds_format:
        calls.sort(key=custom_seconds_sort)
    else:
        calls.sort(key=custom_time_sort)
    return calls


def generate_weight_passenger():
    return int(random.normalvariate(70, 15))


def generate_levels(n, max_level):
    times_half = int(n / 2)
    levels = [random.randint(2, max_level) for _ in range(times_half)]
    tb = [[level, 1] for level in levels]
    bt = [list(reversed(pair)) for pair in tb]
    tb = random.sample(tb, len(tb))
    bt = random.sample(bt, len(bt))
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


def generate_test_sample(max_level, number_flat_in_level, human_per_flat, average_call_per_human, elevators, filename):
    n = max_level * number_flat_in_level * human_per_flat * average_call_per_human
    if n % 2 == 1:
        n += 1
    times = generate_time_call(n)

    top_bottom_levels, bottom_top_levels = generate_levels(n, max_level)
    top_bottom_index = 0
    bottom_top_index = 0

    with open(filename, 'w') as f:
        f.write(f"{n} {max_level} {number_flat_in_level} {human_per_flat} {average_call_per_human} {elevators}\n")
        for i in range(n):
            probability = (i + (n / 10)) / (n + (n / 10))
            level_pair, top_bottom_index, bottom_top_index = choose_level(top_bottom_levels, bottom_top_levels,
                                                                          probability,
                                                                          top_bottom_index, bottom_top_index)
            weight_of_passenger = generate_weight_passenger()
            f.write(f"{times[i]} {level_pair[0]} {level_pair[1]} {weight_of_passenger}\n")
