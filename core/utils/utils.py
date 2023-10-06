def save_results(filename, result):
    print(f"Saving results to {filename}")
    with open(filename, 'a') as f:
        f.write(str(result) + '\n')


def read_commands_from_file(filename):
    print(f"Reading test data from {filename}")

    commands = []
    with open(filename, 'r') as f:
        line = f.readline()
        n = line.split()[0]
        n = int(n)
        while n != 0:
            line = f.readline().strip().split()
            time, from_level, to_level, weight = line
            from_level = int(from_level)
            to_level = int(to_level)
            weight = int(weight)
            commands.append([time, from_level, to_level, weight])
            n -= 1

    print(f"Read {len(commands)} commands from test data.")

    return commands
