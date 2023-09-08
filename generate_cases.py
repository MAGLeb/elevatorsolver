from case_generation.generate import generate_tests
from core.utils.environment import Environment

INPUT_TESTS = [4, 10, 2.5, 3, 1]
CASE_NUMBER = 0

case_path = Environment.get_case_path(CASE_NUMBER)
train_path = Environment.get_train_path(case_path)
tests_path = Environment.get_test_path(case_path)

levels, flats, average_human_per_flat, average_call_per_human, number_elevators = INPUT_TESTS
generate_tests(tests_path, "test", Environment.NUMBER_TEST_PER_CASE, levels, flats,
               average_human_per_flat, average_call_per_human, number_elevators)

generate_tests(train_path, "train", Environment.NUMBER_TRAIN_PER_CASE, levels, flats,
               average_human_per_flat, average_call_per_human, number_elevators)

print("All train and test cases generated successfully!")
