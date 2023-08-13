from test_generator.generate import generate_test_sample


'''
30 levels in building
3 elevators
15 flats in level
3 humans in flat
total humans in building: 30 * 15 * 3 = 1350 humans
average times call per human per day: 3
4050 calls per day

8 most people go to work
13 go to home to dinner
18 return from home
'''

levels = 30
flats = 10
average_human_per_flat = 2
average_call_per_human = 3
filename = './test_generator/tests/test_1.txt'

generate_test_sample(levels, flats, average_human_per_flat, average_call_per_human, filename)

