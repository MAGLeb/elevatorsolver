from case_generation.generate import generate_tests
from core.utils.environment import Environment


INPUT_TESTS = Environment.get_input_train_params()

case_path = Environment.get_case_path(Environment.CASE_NUMBER)
train_path = Environment.get_train_path(case_path)
tests_path = Environment.get_test_path(case_path)

levels, flats, average_human_per_flat, average_call_per_human, number_elevators = INPUT_TESTS
generate_tests(tests_path, "test", Environment.NUMBER_TEST_PER_CASE, levels, flats,
               average_human_per_flat, average_call_per_human, number_elevators)

generate_tests(train_path, "train", Environment.NUMBER_TRAIN_PER_CASE, levels, flats,
               average_human_per_flat, average_call_per_human, number_elevators)

print("All train and test cases generated successfully!")
