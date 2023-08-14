import os

from case_generation.generate import generate_test_sample
from utils.environment import Environment


INPUT_PATH = Environment.get_path('case_generation/input.txt')

with open(INPUT_PATH, 'r') as f:
    lines = f.readlines()
    number_tests = len(lines)

    for i in range(number_tests):
        dirname = f"./cases/case{i}"
        os.makedirs(dirname, exist_ok=True)
        for j in range(Environment.NUMBER_TEST_PER_CASE):
            levels, flats, average_human_per_flat, average_call_per_human, number_elevators = list(
                map(int, lines[i].strip().split()))
            filename = f"{dirname}/test_{j}.txt"
            generate_test_sample(levels, flats, average_human_per_flat, average_call_per_human, number_elevators, filename)
