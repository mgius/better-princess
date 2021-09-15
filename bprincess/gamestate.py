import random
import collections
from dataclasses import dataclass
from typing import List
import enum


class EarringCount(enum.IntEnum):
    ZERO = 0
    ONE = 1
    TWO = 2

    def increment(cur: "EarringCount"):
        if cur == EarringCount.ZERO:
            return EarringCount.ONE
        else:
            return EarringCount.TWO
    
    def decrement(cur: "EarringCount"):
        if cur == EarringCount.TWO:
            return EarringCount.ONE
        else:
            return EarringCount.ZERO


class BoardSpaceTypes(enum.Enum):
    NECKLACE = enum.auto()
    BRACELET = enum.auto()
    RING = enum.auto()
    EARRING = enum.auto()
    CROWN = enum.auto()
    MYSTERY_RING = enum.auto()
    PUT_BACK = enum.auto()
    TAKE_ANY_PIECE = enum.auto()


GAME_BOARD = [
    BoardSpaceTypes.NECKLACE,
    BoardSpaceTypes.PUT_BACK,
    BoardSpaceTypes.BRACELET,
    BoardSpaceTypes.TAKE_ANY_PIECE,
    BoardSpaceTypes.RING,
    BoardSpaceTypes.MYSTERY_RING,
    BoardSpaceTypes.EARRING,
    BoardSpaceTypes.CROWN,
    BoardSpaceTypes.NECKLACE,
    BoardSpaceTypes.PUT_BACK,
    BoardSpaceTypes.BRACELET,
    BoardSpaceTypes.TAKE_ANY_PIECE,
    BoardSpaceTypes.RING,
    BoardSpaceTypes.MYSTERY_RING,
    BoardSpaceTypes.EARRING,
    BoardSpaceTypes.CROWN,
]

# each space is equally likely, excellent
SPACE_DISTRIBUTION = collections.Counter(GAME_BOARD)


@dataclass
class PlayerState:
    """
    2 * 2 * 2 * 2 * 2 * 3 = 96 possible user states
    """

    tiara: bool = False
    bracelet: bool = False
    necklace: bool = False
    ring: bool = False
    clear_ring: bool = False
    earrings: EarringCount = EarringCount.ZERO

    board_position: int = 0

    @property
    def has_won(self):
        return self.score == 6

    def move(self, distance) -> BoardSpaceTypes:
        self.board_position = (self.board_position + distance) % len(GAME_BOARD)
        return GAME_BOARD[self.board_position]

    def move_and_play(self, distance) -> int:
        new_position = self.move(distance)
        self.apply_board_space(new_position)
        return self.score

    @staticmethod
    def generate_all_states():
        # this code looks awful but it's only 96 loops
        out = []
        for tiara in [True, False]:
            for bracelet in [True, False]:
                for necklace in [True, False]:
                    for ring in [True, False]:
                        for clear_ring in [True, False]:
                            for earring in EarringCount:
                                player = PlayerState(
                                    tiara=tiara,
                                    bracelet=bracelet,
                                    necklace=necklace,
                                    ring=ring,
                                    clear_ring=clear_ring,
                                    earrings=earring,
                                )
                                if player.is_win():
                                    # don't care about players already winning
                                    continue
                                out.append(player)

        return out


    @property
    def score(self):
        return (
            self.earrings.value + 
            sum(map(lambda v: 1 if v else 0, [self.tiara, self.bracelet, self.necklace, self.ring])) - 
            (1 if self.clear_ring else 0))

    def _toggle_jewelry(self, remove=False):
        # pick a piece of jewelry and put it on or take it off
        if remove and self.clear_ring is remove:
            self.clear_ring = not remove
        elif self.tiara is remove:
            self.tiara = not remove
        elif self.bracelet is remove:
            self.bracelet = not remove
        elif self.necklace is remove:
            self.necklace = not remove
        elif self.ring is remove:
            self.ring = not remove
        else:
            if remove:
                self.earrings = self.earrings.decrement()
            else:
                self.earrings = self.earrings.increment()
            

    def apply_board_space(self, board_space: BoardSpaceTypes):
        match board_space:
            case BoardSpaceTypes.BRACELET:
                self.bracelet = True
            case BoardSpaceTypes.CROWN:
                self.crown = True
            case BoardSpaceTypes.EARRING:
                self.earrings = EarringCount.increment(self.earrings)
            case BoardSpaceTypes.MYSTERY_RING:
                self.clear_ring = True
            case BoardSpaceTypes.NECKLACE:
                self.neckace = True
            case BoardSpaceTypes.PUT_BACK:
                self._toggle_jewelry(remove=True)
            case BoardSpaceTypes.RING:
                self.ring = True
            case BoardSpaceTypes.TAKE_ANY_PIECE:
                self._toggle_jewelry(remove=False)


@dataclass
class GameState:
    players: List[PlayerState]

    def apply_board_space(self, player: PlayerState, board_space: BoardSpaceTypes):
        match board_space:
            case BoardSpaceTypes.CROWN:
                for player in self.players:
                    player.crown = False
            case BoardSpaceTypes.MYSTERY_RING:
                for player in self.players:
                    player.clear_ring = False

        player.apply_board_space(board_space)
