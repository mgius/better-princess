from bprincess.gamestate import EarringCount, PlayerState
import unittest


class TestEarringCount(unittest.TestCase):
    def test_increment(self):
        self.assertEqual(EarringCount.ONE, EarringCount.ZERO.increment())
        self.assertEqual(EarringCount.TWO, EarringCount.ONE.increment())
        self.assertEqual(EarringCount.TWO, EarringCount.TWO.increment())

    def test_decrement(self):
        self.assertEqual(EarringCount.ONE, EarringCount.TWO.decrement())
        self.assertEqual(EarringCount.ZERO, EarringCount.ONE.decrement())
        self.assertEqual(EarringCount.ZERO, EarringCount.ZERO.decrement())


class TestToggleJewelry(unittest.TestCase):
    def test_toggle_up_to_victory(self):
        player = PlayerState()
        self.assertEqual(0, player.score)
        for i in range(1, 7):
            player._toggle_jewelry()
            self.assertEqual(i, player.score)

        self.assertTrue(player.has_won)


class TestPlayerStateScores(unittest.TestCase):
    def test_no_jewelery(self):
        state = PlayerState()
        self.assertEqual(0, state.score)

    def test_earrings_count(self):
        no_earrings = PlayerState(earrings=EarringCount.ZERO)
        one_earring = PlayerState(earrings=EarringCount.ONE)
        two_earrings = PlayerState(earrings=EarringCount.TWO)

        self.assertEqual(0, no_earrings.score)
        self.assertEqual(1, one_earring.score)
        self.assertEqual(2, two_earrings.score)

    def test_clear_ring(self):
        only_clear_ring = PlayerState(clear_ring=True)
        clear_plus_tiara = PlayerState(clear_ring=True, tiara=True)

        self.assertEqual(-1, only_clear_ring.score)
        self.assertEqual(0, clear_plus_tiara.score)

    def test_fully_loaded(self):
        fully_loaded_with_clear_ring = PlayerState(
            tiara=True,
            bracelet=True,
            necklace=True,
            ring=True,
            clear_ring=True,
            earrings=EarringCount.TWO,
        )

        self.assertEqual(5, fully_loaded_with_clear_ring.score)

        fully_loaded = PlayerState(
            tiara=True,
            bracelet=True,
            necklace=True,
            ring=True,
            earrings=EarringCount.TWO,
        )

        self.assertEqual(6, fully_loaded.score)
