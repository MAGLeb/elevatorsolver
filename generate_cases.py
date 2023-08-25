import os

from case_generation.generate import generate_test_sample
from core.utils.environment import Environment

INPUT_TESTS = [3, 10, 2.5, 3, 1]

case_path = Environment.get_case_path(1)
tests_path = f"{case_path}/tests"

os.makedirs(tests_path, exist_ok=True)

for j in range(Environment.NUMBER_TEST_PER_CASE):
    levels, flats, average_human_per_flat, average_call_per_human, number_elevators = INPUT_TESTS
    filename = f"{tests_path}/test{j}.txt"

    print(f"Generating test sample {j + 1}")
    generate_test_sample(levels, flats, average_human_per_flat, average_call_per_human, number_elevators, filename)

print("All test cases generated successfully!")
