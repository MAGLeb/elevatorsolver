import os

from case_generation.generate import generate_test_sample
from core.utils.environment import Environment

INPUT_TESTS = [[10, 10, 2.5, 3, 1]]
NUMBER_TESTS = len(INPUT_TESTS)

for i in range(NUMBER_TESTS):
    case_path = Environment.get_case_path(i)
    tests_path = f"{case_path}/tests"
    os.makedirs(tests_path, exist_ok=True)
    for j in range(Environment.NUMBER_TEST_PER_CASE):
        levels, flats, average_human_per_flat, average_call_per_human, number_elevators = INPUT_TESTS[i]
        filename = f"{tests_path}/test{j}.txt"
        generate_test_sample(levels, flats, average_human_per_flat, average_call_per_human, number_elevators, filename)
