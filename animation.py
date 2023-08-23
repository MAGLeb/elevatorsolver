import matplotlib.pyplot as plt
import matplotlib.patches as patches

# Количество этажей
NUM_FLOORS = 5

fig, ax = plt.subplots()
ax.set_xlim(0, 2)
ax.set_ylim(0, NUM_FLOORS)
ax.set_yticks(range(NUM_FLOORS))
ax.set_xticks([0.5, 1.5])
ax.set_xticklabels(['Elevator', 'Buttons'])

def visualize_elevator(elevator_position, buttons):
    ax.clear()
    ax.set_xlim(0, 2)
    ax.set_ylim(0, NUM_FLOORS)
    ax.set_yticks(range(NUM_FLOORS))
    ax.set_xticks([0.5, 1.5])
    ax.set_xticklabels(['Elevator', 'Buttons'])

    # Отображение лифта
    elevator = patches.Rectangle((0, elevator_position), 1, 1, facecolor="blue")
    ax.add_patch(elevator)

    # Отображение состояния кнопок на этажах
    for i in range(NUM_FLOORS):
        color = "white"
        if buttons[i] == 'outside':
            color = "green"
        elif buttons[i] == 'inside':
            color = "yellow"
        elif buttons[i] == 'both':
            color = "red"

        button = patches.Rectangle((1, i), 1, 1, facecolor=color)
        ax.add_patch(button)

    plt.draw()
    plt.pause(0.01)  # Задержка, чтобы график успел обновиться

# Пример использования:
for _ in range(20):
    elevator_position = _ % NUM_FLOORS
    buttons = ['outside' if i == _ else None for i in range(NUM_FLOORS)]
    visualize_elevator(elevator_position, buttons)
