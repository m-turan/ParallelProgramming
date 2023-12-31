import threading
import random
import time
import math
import matplotlib.pyplot as plt
import matplotlib.animation as animation


class Fork:
    def __init__(self, index: int):
        self.index: int = index
        self.lock: threading.Lock = threading.Lock()
        self.picked_up: bool = False
        self.owner: int = -1

    def pick_up(self, owner: int):
        with self.lock:
            self.owner = owner
            self.picked_up = True

    def put_down(self):
        with self.lock:
            self.picked_up = False
            self.owner = -1

    def __str__(self):
        return f"F{self.index:2d} ({self.owner:2d})"

#eğer komşu gelirse tüm çatallar bıraklıp komşunun yemeye başlaması lazım 

class Arbitrator:
    def __init__(self, forks: list[Fork]):
        self.forks: list[Fork] = forks
        self.permission: threading.Semaphore = threading.Semaphore(1)

    def acquire_forks(self, philosopher_index: int):
        self.permission.acquire()
        left_fork = self.forks[philosopher_index]
        right_fork = self.forks[(philosopher_index + 1) % len(self.forks)]
        left_fork.pick_up(philosopher_index)
        right_fork.pick_up(philosopher_index)

    def release_forks(self, philosopher_index: int):
        left_fork = self.forks[philosopher_index]
        right_fork = self.forks[(philosopher_index + 1) % len(self.forks)]
        left_fork.put_down()
        right_fork.put_down()
        self.permission.release()


class Philosopher(threading.Thread):
    def __init__(self, index: int, arbitrator: Arbitrator, spaghetti: int):
        super().__init__()
        self.index: int = index
        self.arbitrator: Arbitrator = arbitrator
        self.spaghetti: int = spaghetti
        self.eating: bool = False

    def run(self):
        while self.spaghetti > 0:
            self.think()
            self.eat_arb()

    def think(self):
        time.sleep(3 + random.random() * 3)

    def eat_arb(self):
        self.arbitrator.acquire_forks(self.index)
        try:
            # think for a while
            time.sleep(2 + random.random() * 3)
            self.spaghetti -= 1
            self.eating = True
            time.sleep(2 + random.random() * 3)
        finally:
            self.eating = False
            self.arbitrator.release_forks(self.index)

    def __str__(self):
        return f"P{self.index:2d} ({self.spaghetti:2d})"


def animated_table(philosophers: list[Philosopher], forks: list[Fork], m: int):
    """
    Creates an animated table with the philosophers and forks.

    :param philosophers: The list of philosophers.
    :param forks: The list of forks.
    :param m: The amount of spaghetti each philosopher has.
    """
    fig, ax = plt.subplots()
    ax.set_xlim(-1, 1)
    ax.set_ylim(-1, 1)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title("Dining Philosophers")
    philosopher_circles: list[plt.Circle] = [
        plt.Circle((0, 0), 0.2, color="black") for _ in range(len(philosophers))
    ]
    philosopher_texts: list[plt.Text] = [
        plt.Text(
            0,
            0,
            str(philosopher.index),
            horizontalalignment="center",
            verticalalignment="center",
        )
        for philosopher in philosophers
    ]
    fork_lines: list[plt.Line2D] = [
        plt.Line2D((0, 0), (0, 0), color="black") for _ in range(len(forks))
    ]
    fork_texts: list[plt.Text] = [
        plt.Text(
            0,
            0,
            str(fork.index),
            horizontalalignment="center",
            verticalalignment="center",
        )
        for fork in forks
    ]
    for philosopher_circle in philosopher_circles:
        ax.add_patch(philosopher_circle)
    for fork_line in fork_lines:
        ax.add_line(fork_line)
    for philosopher_text in philosopher_texts:
        ax.add_artist(philosopher_text)
    for fork_text in fork_texts:
        ax.add_artist(fork_text)

    def update(frame):
        """
        Updates the table.
        """
        # get the philosophers and forks from the global scope
        nonlocal philosophers, forks
        for i in range(len(philosophers)):
            philosopher_circles[i].center = (
                0.5 * math.cos(2 * math.pi * i / len(philosophers)),
                0.5 * math.sin(2 * math.pi * i / len(philosophers)),
            )
            # update the labels as text on the plot
            philosopher_texts[i].set_position(
                (
                    0.9 * math.cos(2 * math.pi * i / len(philosophers)),
                    0.9 * math.sin(2 * math.pi * i / len(philosophers)),
                )
            )
            philosopher_texts[i].set_text(
                str(philosophers[i]) if philosophers[i].spaghetti > 0 else "X"
            )
            if philosophers[i].eating:
                philosopher_circles[i].set_color("red")
            else:
                philosopher_circles[i].set_color("black")
            philosopher_circles[i].radius = 0.2 * philosophers[i].spaghetti / m
            fork_lines[i].set_data(
                (
                    0.5 * math.cos(2 * math.pi * i / len(philosophers)),
                    0.5 * math.cos(2 * math.pi * (i + 1) / len(philosophers)),
                ),
                (
                    0.5 * math.sin(2 * math.pi * i / len(philosophers)),
                    0.5 * math.sin(2 * math.pi * (i + 1) / len(philosophers)),
                ),
            )
            # add the labels of the forks as text on the plot
            fork_texts[i].set_position(
                (
                    0.5 * math.cos(2 * math.pi * i / len(philosophers))
                    + 0.5 * math.cos(2 * math.pi * (i + 1) / len(philosophers)),
                    0.5 * math.sin(2 * math.pi * i / len(philosophers))
                    + 0.5 * math.sin(2 * math.pi * (i + 1) / len(philosophers)),
                )
            )
            fork_texts[i].set_text(str(forks[i]))
            if forks[i].picked_up:
                fork_lines[i].set_color("red")
            else:
                fork_lines[i].set_color("black")
            if sum(philosopher.spaghetti for philosopher in philosophers) == 0:
                ani.event_source.stop()
                exit(0)
        return philosopher_circles + fork_lines + philosopher_texts + fork_texts

    ani = animation.FuncAnimation(
        fig, update, frames=range(100000), interval=10, blit=False
    )
    plt.show()


def table(philosophers: list[Philosopher], forks: list[Fork], m: int):
    while sum(philosopher.spaghetti for philosopher in philosophers) > 0:
        eating_philosophers: int = sum(
            philosopher.eating for philosopher in philosophers
        )
        print("\033[H\033[J")
        print("=" * (len(philosophers) * 16))
        print(
            "         ",
            "             ".join(
                ["E" if philosopher.eating else "T" for philosopher in philosophers]
            ),
        )
        print("       ".join(map(str, forks)), "     ", forks[0])
        print(
            "      ",
            "       ".join(map(str, philosophers)),
            "      : ",
            str(eating_philosophers),
        )
        spaghetti_eaten: int = sum(philosopher.spaghetti for philosopher in philosophers)
        print("Total spaghetti eaten:", spaghetti_eaten)
        time.sleep(0.1)


def main() -> None:
    n: int = 5
    m: int = 7
    forks: list[Fork] = [Fork(i) for i in range(n)]
    arbitrator: Arbitrator = Arbitrator(forks)
    philosophers: list[Philosopher] = [Philosopher(i, arbitrator, m) for i in range(n)]

    for philosoper in philosophers:
        philosoper.start()
    threading.Thread(target=table, args=(philosophers, forks, m), daemon=True).start()
    animated_table(philosophers, forks, m)
    for philosoper in philosophers:
        philosoper.join()


if __name__ == "__main__":
    main()