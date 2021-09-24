import random
import collections
from dataclasses import dataclass, replace, field
from types import new_class
from typing import List, no_type_check
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
    PUT_BACK = enum.auto()
    BRACELET = enum.auto()
    TAKE_ANY_PIECE = enum.auto()
    RING = enum.auto()
    MYSTERY_RING = enum.auto()
    EARRING = enum.auto()
    CROWN = enum.auto()


@dataclass(frozen=True)
class PlayerState:
    """ The base game rules """

    tiara: bool = False
    bracelet: bool = False
    necklace: bool = False
    ring: bool = False
    clear_ring: bool = False
    earrings: EarringCount = EarringCount.ZERO

    game_board: List[BoardSpaceTypes] = field(default_factory = lambda: list(BoardSpaceTypes))
    board_position: int = 0

    def __hash__(self) -> int:
        return (
            int(self.tiara) |
            int(self.bracelet) << 1 |
            int(self.necklace) << 2 |
            int(self.ring) << 3 |
            int(self.clear_ring) << 4 |
            int(self.earrings.value) << 5)

    @property
    def has_won(self):
        return self.score == 6

    @property
    def board_space(self):
        return self.game_board[self.board_position]

    @property
    def possible_states(self):
        states = []
        for board_space in BoardSpaceTypes:
            state = replace(self)
            state.apply_board_space(board_space)
            states.append(hash(state))

        return states

    @property
    def score(self):
        return (
            self.earrings.value + 
            sum(map(lambda v: 1 if v else 0, [self.tiara, self.bracelet, self.necklace, self.ring])) - 
            (1 if self.clear_ring else 0))

    def move(self, distance) -> "PlayerState":
        new_position = (self.board_position + distance) % len(self.game_board)
        return replace(self, board_position=new_position)

    def move_and_play(self, distance) -> "PlayerState":
        moved = self.move(distance)
        return moved.apply_board_space(self.board_space)

    def _toggle_jewelry(self, remove=False) -> "PlayerState":
        # pick a piece of jewelry and put it on or take it off
        if remove and self.clear_ring is remove:
            return replace(self, clear_ring=not remove)
        elif self.tiara is remove:
            return replace(self, tiara=not remove)
        elif self.bracelet is remove:
            return replace(self, bracelet=not remove)
        elif self.necklace is remove:
            return replace(self, necklace=not remove)
        elif self.ring is remove:
            return replace(self, ring=not remove)
        else:
            if remove:
                return replace(self, earrings=self.earrings.decrement())
            else:
                return replace(self, earrings=self.earrings.increment())
            
    def apply_board_space(self, board_space: BoardSpaceTypes) -> "PlayerState":
        match board_space:
            case BoardSpaceTypes.BRACELET:
                return replace(self, bracelet=True)
            case BoardSpaceTypes.CROWN:
                return replace(self, tiara=True)
            case BoardSpaceTypes.EARRING:
                return replace(self, earrings=EarringCount.increment(self.earrings))
            case BoardSpaceTypes.MYSTERY_RING:
                return replace(self, clear_ring=True)
            case BoardSpaceTypes.NECKLACE:
                return replace(self, necklace=True)
            case BoardSpaceTypes.PUT_BACK:
                return self._toggle_jewelry(remove=True)
            case BoardSpaceTypes.RING:
                return replace(self, ring=True)
            case BoardSpaceTypes.TAKE_ANY_PIECE:
                return self._toggle_jewelry(remove=False)

    @staticmethod
    def generate_all_states():
        # this code looks awful but it's only 96 loops
        out = set()
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
                                out.add(player)

        return out


@dataclass(frozen=True)
class AlreadyWornTokensPlayer(PlayerState):
    tokens_needed: int = 2
    tokens: int = 0

    @property
    def score(self):
        return super().score + self.tokens / (self.tokens_needed + 1)

    def __hash__(self) -> int:
        return super().__hash__() << 2 | self.tokens


    def apply_board_space(self, board_space: BoardSpaceTypes) -> "PlayerState":
        new_state = super().apply_board_space(board_space)
        if hash(new_state) == hash(self):
            new_state = replace(new_state, tokens=new_state.tokens+1)
        
        if new_state.tokens == self.tokens_needed:
            new_state = new_state._toggle_jewelry()
            new_state = replace(new_state, tokens=0)
        
        return new_state


def NoMysteryRingPlayer(*args, **kwargs) -> PlayerState:
    """ Had about a 2 turn impact. """
    kwargs['game_board'] = list(BoardSpaceTypes)
    kwargs['game_board'].remove(BoardSpaceTypes.MYSTERY_RING)

    return PlayerState(*args, **kwargs)


def ShuffledBoardPlayer(*args, **kwargs) -> PlayerState:
    """ Unsurprisingly, this has little effect on the flow of the game, but it was worth verifying """
    game_board = list(BoardSpaceTypes)
    random.shuffle(game_board)
    kwargs['game_board'] = game_board

    return PlayerState(*args, **kwargs)