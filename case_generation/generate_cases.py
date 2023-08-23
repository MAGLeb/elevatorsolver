import os

from case_generation.generate import generate_test_sample
from core.utils.environment import Environment

NUMBER_TEST_PER_CASE = 1000 if Environment.IS_PRODUCTION else 3

INPUT_TESTS = [[10, 10, 2.5, 3, 1]]
NUMBER_TESTS = len(INPUT_TESTS)

for i in range(NUMBER_TESTS):
    dirname = f"./cases/case{i}"
    os.makedirs(dirname, exist_ok=True)
    for j in range(NUMBER_TEST_PER_CASE):
        levels, flats, average_human_per_flat, average_call_per_human, number_elevators = input_test[i]
        filename = f"{dirname}/test{j}.txt"
        generate_test_sample(levels, flats, average_human_per_flat, average_call_per_human, number_elevators,
                             filename)
