from case_generation.generate import generate_tests
from core.utils.environment import Environment

number_levels, people_everyday_use, number_elevators = 10, 7200, 1
case_path = Environment.get_case_path(Environment.CASE_NUMBER)
train_path = Environment.get_train_path(case_path)
tests_path = Environment.get_test_path(case_path)

generate_tests(tests_path, "validation", Environment.NUMBER_VALIDATION_PER_CASE,
               number_levels, people_everyday_use, number_elevators)

generate_tests(train_path, "train", Environment.NUMBER_TRAIN_PER_CASE,
               number_levels, people_everyday_use, number_elevators)

print("All train and test cases generated successfully!")
