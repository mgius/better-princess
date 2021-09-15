import statistics
import random
import itertools
from bprincess import gamestate


def run_simulation():
    scores = []
    player = gamestate.PlayerState()

    for _ in range(100):
        to_move = random.randint(1, 4)
        scores.append(player.move_and_play(to_move))
        if player.has_won:
            break

    return scores


def main():
    simulations = []
    for _ in range(1000):
        simulations.append(run_simulation())

    simulation_lengths = [len(sim) for sim in simulations]
    print(f"Mean turns: {statistics.mean(simulation_lengths)}")
    print(f"Quartiles: {statistics.quantiles(simulation_lengths)}")
    with open("data.csv", "w") as f:
        f.write("turns\n")
        for s in simulation_lengths:
            f.write(f"{s}\n")


if __name__ == "__main__":
    main()
