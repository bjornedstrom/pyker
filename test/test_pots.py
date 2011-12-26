# -*- coding: utf-8 -*-
#
# Copyright (c) 2011 Björn Edström <be@bjrn.se>

import unittest

import pyker.pots as pots

class PS(object):
    def __init__(self, player, chips):
        self.player = player
        self.chips = chips

class PotsTest(unittest.TestCase):
    def setUp(self):
        self.p1 = PS('player1', 1000)
        self.p2 = PS('player2', 500)
        self.p3 = PS('player3', 300)
        self.p4 = PS('player4', 900)
        self.p5 = PS('player5', 3000)

        self.p = pots.Pots()

    def test_main_pot_simple(self):
        self.p.post(self.p1, 500)
        self.assertEquals(500, self.p1.chips)
        self.assertTrue(0 in self.p.pots)
        self.assertEquals(500, self.p.pots[0][self.p1])

    def test_main_pot_simple_many(self):
        self.p.post(self.p1, 500)
        self.assertEquals(500, self.p1.chips)
        self.assertTrue(0 in self.p.pots)
        self.assertEquals(500, self.p.pots[0][self.p1])

        self.p.post(self.p2, 500)
        self.assertEquals(0, self.p2.chips)
        self.assertTrue(0 in self.p.pots)
        self.assertTrue(1 not in self.p.pots)
        self.assertEquals(500, self.p.pots[0][self.p2])

        self.p.post(self.p4, 500)
        self.assertEquals(400, self.p4.chips)
        self.assertTrue(0 in self.p.pots)
        self.assertTrue(1 not in self.p.pots)
        self.assertEquals(500, self.p.pots[0][self.p4])

    def test_all_in_simple(self):
        self.p.post(self.p1, 500)
        self.assertEquals(500, self.p1.chips)
        self.assertTrue(0 in self.p.pots)
        self.assertEquals(500, self.p.pots[0][self.p1])

        # This player must go all in
        self.p.post(self.p3, 500)
        self.assertEquals(0, self.p3.chips)
        self.assertTrue(0 in self.p.pots)
        self.assertTrue(1 in self.p.pots)
        self.assertEquals(300, self.p.pots[0][self.p3])

        # This has created a new pot for player 1
        self.assertEquals(200, self.p.pots[1][self.p1])
        self.assertTrue(self.p3 not in self.p.pots[1])

    def test_all_in_many(self):
        self.p.post(self.p1, 500)
        self.assertEquals(500, self.p1.chips)
        self.assertTrue(0 in self.p.pots)
        self.assertEquals(500, self.p.pots[0][self.p1])

        # This player must go all in
        self.p.post(self.p3, 500)
        self.assertEquals(0, self.p3.chips)
        self.assertTrue(0 in self.p.pots)
        self.assertTrue(1 in self.p.pots)
        self.assertEquals(300, self.p.pots[0][self.p3])

        # This has created a new pot for player 1
        self.assertEquals(200, self.p.pots[1][self.p1])
        self.assertTrue(self.p3 not in self.p.pots[1])

        # Player 2 calls.
        self.p.post(self.p2, 500)
        self.assertTrue(self.p2 in self.p.pots[0])
        self.assertTrue(self.p2 in self.p.pots[1])
        self.assertEquals(300, self.p.pots[0][self.p2])
        self.assertEquals(200, self.p.pots[1][self.p2])

        # Player 4 raises
        self.p.post(self.p4, 700)
        self.assertTrue(self.p4 in self.p.pots[0])
        self.assertTrue(self.p4 in self.p.pots[1])
        self.assertTrue(self.p4 in self.p.pots[2])
        self.assertEquals(1, len(self.p.pots[2]))
        self.assertEquals(300, self.p.pots[0][self.p4])
        self.assertEquals(200, self.p.pots[1][self.p4])
        self.assertEquals(200, self.p.pots[2][self.p4])

if __name__ == '__main__':
    unittest.main()
