def save_results(filename, result):
    print(f"Saving results to {filename}")
    with open(filename, 'w') as f:
        f.writelines(map(lambda x: str(x) + '\n', result))


def read_commands_from_file(filename):
    print(f"Reading test data from {filename}")

    commands = []
    with open(filename, 'r') as f:
        line = f.readline()
        n, levels, _, _, _, _ = line.split()
        n = int(n)
        levels = int(levels)
        while n != 0:
            line = f.readline().strip().split()
            time, from_level, to_level, weight = line
            from_level = int(from_level)
            to_level = int(to_level)
            weight = int(weight)
            commands.append([time, from_level, to_level, weight])
            n -= 1

    print(f"Read {len(commands)} commands from test data.")

    return levels, commands
