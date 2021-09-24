import statistics
import random
from bprincess import gamestate
from typing import Callable, List


def run_simulations(
    create_player: Callable[[], gamestate.PlayerState],
    move_max=100,
    simulation_count=1000,
) -> List[List[int]]:
    simulations = []
    for _ in range(simulation_count):
        simulations.append(run_simulation(create_player(), move_max))

    return simulations


def run_simulation(player: gamestate.PlayerState, move_max) -> List[int]:
    scores = []

    for _ in range(move_max):
        to_move = random.randint(1, 5)
        player = player.move_and_play(to_move)
        scores.append(player.score)
        if player.has_won:
            break

    return scores


def print_stats(simulations: List[List[int]], prefix: str):
    print(prefix)

    simulation_lengths = [len(sim) for sim in simulations]
    print(f"Mean turns: {statistics.mean(simulation_lengths)}")
    print(f"Quartiles: {statistics.quantiles(simulation_lengths)}")
    print()


def main():
    base_simulations = run_simulations(gamestate.PlayerState)
    print_stats(base_simulations, "Stock Ruleset")
    two_tokens_simulations = run_simulations(gamestate.AlreadyWornTokensPlayer)
    print_stats(two_tokens_simulations, "Choose any jewelery after two failed")
    three_tokens_simulations = run_simulations(
        lambda: gamestate.AlreadyWornTokensPlayer(tokens_needed=3)
    )
    print_stats(three_tokens_simulations, "Choose any jewelery after three failed")
    no_mystery_ring = run_simulations(gamestate.NoMysteryRingPlayer)
    print_stats(no_mystery_ring, "Remove Mystery Ring")


if __name__ == "__main__":
    main()
