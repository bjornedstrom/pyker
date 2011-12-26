# -*- coding: utf-8 -*-
#
# Copyright (c) 2011 Björn Edström <be@bjrn.se>

import unittest

from pyker.poker import *


class HandTest(unittest.TestCase):
    def setUp(self):
        pass

    def test_classifications(self):
        C = lambda s: Hand.from_string(s).classify().__class__

        self.assertEquals(StraightFlush, C('7h 8h 9h th jh'))
        self.assertEquals(FourOfAKind, C('7h 7s 7c 7d jh'))
        self.assertEquals(FullHouse, C('3h 3c 3s tc th'))
        self.assertEquals(Flush, C('7h 8h 2h th jh'))
        self.assertEquals(Straight, C('9c 8h 7d td jh'))
        self.assertEquals(ThreeOfAKind, C('3c 3h 3d td js'))
        self.assertEquals(TwoPair, C('2c 2s 3d 3h jd'))
        self.assertEquals(Pair, C('7c 4s 4d th jd'))
        self.assertEquals(Highest, C('kc as 9d 3h 2d'))

    def test_relative(self):
        H = lambda s: Hand.best_from_seven(*string_to_cards(s))

        # straight
        h1 = H('ah kc qd js th 3s 4d')
        h2 = H('ah kc 8d 5s 2h 3s 4d')
        self.assertEquals(Straight(Rank('a')), h1.classify())
        self.assertEquals(Straight(Rank(5)), h2.classify())
        self.assertTrue(h1 > h2)

        # two pairs
        h1 = H('kd 9h 8s 4d 8h 5s kc')
        h2 = H('4s qc kd 9h 8s 4d 8h')
        self.assertEquals(TwoPair(Rank('k'), Rank(8), Rank(9)), h1.classify())
        self.assertEquals(TwoPair(Rank(8), Rank(4), Rank('k')), h2.classify())
        self.assertTrue(h1 > h2)

        # pair
        h1 = H('jd 9h 8s 4d 8h 5s kc')
        h2 = H('2s qc qd 9h 8s 4d 7h')
        self.assertEquals(Pair(Rank(8), (Rank('k'), Rank('j'), Rank(9))), h1.classify())
        self.assertEquals(Pair(Rank('q'), (Rank(9), Rank(8), Rank(7))), h2.classify())
        self.assertTrue(h2 > h1)

        # equal pair, kickers
        # XXX: Don't care that both of these have 8s :)
        h1 = H('jd 9h 8s 4d 8h 5s kc')
        h2 = H('8s qc kd 9h 8c 4d 7h')
        self.assertEquals(Pair(Rank(8), (Rank('k'), Rank('j'), Rank(9))), h1.classify())
        self.assertEquals(Pair(Rank(8), (Rank('k'), Rank('q'), Rank(9))), h2.classify())
        self.assertTrue(h2 > h1)

    def test_strings(self):
        self.assertEquals('Jack', Rank('j').pretty())
        self.assertEquals(Rank('j'), Rank.from_string('J'))
        self.assertEquals('j', str(Rank('j')))

        self.assertEquals('8h', str(Card(Rank(8), 'h')))
        self.assertEquals(Card(Rank(8), 'h'), Card.from_string('8h'))

        C = lambda s: Hand.from_string(s).classify()
        self.assertEquals('Straight Flush, Jack High', str(C('7h 8h 9h th jh')))


if __name__ == '__main__':
    unittest.main()
