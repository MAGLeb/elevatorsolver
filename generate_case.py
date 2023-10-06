from case_generation.generate import generate_tests
from core.utils.environment import Environment


generate_tests(Environment.VALIDATE_TESTS_PATH, "validation", Environment.NUMBER_VALIDATION_PER_CASE)

generate_tests(Environment.TRAIN_TESTS_PATH, "train", Environment.NUMBER_TRAIN_PER_CASE)

print("All train and test cases generated successfully!")
