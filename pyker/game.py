#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2011 Björn Edström <be@bjrn.se>
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
# 3. Neither the name of the University nor the names of its contributors
#    may be used to endorse or promote products derived from this software
#    without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE REGENTS AND CONTRIBUTORS ``AS IS'' AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.  IN NO EVENT SHALL THE REGENTS OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS
# OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
# HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY
# OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
# SUCH DAMAGE.

import random
from pyker.poker import *


class Player(object):
    def __init__(self, name='', chips=0):
        self.name = name
        self.chips = chips

    def __str__(self):
        return self.name

    def __repr__(self):
        return '<Player name=%s chips=%s>' % (self.name, self.chips)


class PlayerState(object):
    def __init__(self, player, chips):
        self.player = player

        # XXX: Remove from Player...
        self.chips = chips

    def __repr__(self):
        return '<PlayerState player=%s chips=%s>' % (self.player, self.chips)


class Table(object):
    def __init__(self, num_seats):
        self.num_seats = num_seats
        self.seats = [None] * num_seats

    def free(self):
        return (i for i in range(self.num_seats) if self.seats[i] is None)

    def players(self):
        return self.num_seats - len(tuple(self.free()))

    def join(self, seat, player_state):
        if self.seats[seat] is not None:
            raise Exception('seat taken by other player')
        self.seats[seat] = player_state

    def leave(self, player_state):
        try:
            i = self.seats.index(player_state)
        except ValueError:
            raise Exception('player not in table')
        self.seats[i] = None

    def __repr__(self):
        s = []
        for i in range(self.num_seats):
            s.append(str(self.seats[i]))
        return '<Table %s>' % (' '.join(s),)

    def get(self, i):
        return self.seats[i % self.num_seats]

    def find(self, i):
        while True:
            p = self.seats[i % self.num_seats]
            if p is not None:
                return i
            i += 1


class GameRules(object):
    def __init__(self):
        # simplified, moving, dead
        self.button_rule = 'simplified'

        self.table_stakes = True


class Game(object):
    def __init__(self, table, rules):
        self.table = table
        self.rules = rules
        self.dealer = 0
        self.bb = 0
        self.sb = 0
        self.pots = {} # multiple per table stakes
        self.pos = 0

        self.state = 'init'
        self.deck = None
        self.active = set()

    def set_blinds(self, big, small):
        self.bb = big
        self.sb = small

    def next(self):
        while True:
            p = self.table.get(self.pos)
            self.pos += 1
            if p is not None:
                return p

    def post(self, ps, chips):
        ps.chips -= chips
        assert ps.chips >= 0
        self.pots['main'] += chips
        print '\tpots = %s'  % (self.pots,)

        try:
            self.bets[ps] += chips
        except:
            self.bets[ps] = chips

        print 'bets:', ' '.join(('%s=%s' % (k.player, v) for (k, v) in self.bets.iteritems()))

    def game(self): # state

        # state machine:
        if self.state == 'init':
            print 'INIT'
            self.pots = {}
            self.pots['main'] = 0
            self.bets = {}

            self.state = 'deal-hole'

        elif self.state == 'deal-hole':
            print 'DEALING CARDS'

            self.active = set()

            deck = []
            for suit in 'hscd':
                for rank in map(Rank, range(2, 15)):
                    deck.append(Card(rank, suit))
            random.shuffle(deck)
            self.deck = deck

            dealer = self.table.find(self.dealer)
            print '%s is dealer' % (self.table.get(dealer).player)

            for pos in range(dealer + 1,
                             dealer + 1 + self.table.num_seats):
                ps = self.table.get(pos)
                if ps is None:
                    continue
                ps.hole, self.deck = self.deck[0:2], self.deck[2:]

                print 'dealt hole cards to %s' % (ps.player)

                self.active.add(ps)

            self.state = 'blinds'
        elif self.state == 'blinds':
            print 'POSTING BLINDS'

            pos = self.table.find(self.dealer)
            print '%s is dealer' % (self.table.get(pos).player)

            # If there are only two players, the dealer will post the
            # small blinds. Otherwise, it's the next player.
            if self.table.players() > 2:
                pos += 1

            sbi = self.table.find(pos)
            sb = self.table.get(sbi)

            print '%s posting small blind' % (sb.player,)
            self.post(sb, self.sb)

            bbi = self.table.find(sbi + 1)
            bb = self.table.get(bbi)

            print '%s posting big blind' % (bb.player,)
            self.post(bb, self.bb)

            self.pos = bbi + 1
            self.state = 'betting'
            self.sub_state = 'preflop'
        elif self.state == 'betting':
            print 'BETTING', self.sub_state

            acted = set()

            while self.active:
                # betting round continues until everyone has acted and
                # bet the same amount (or all-in)

                if len(acted) == len(self.active):
                    val = self.bets.values()
                    # XXX: All in
                    if all((v == val[0] for v in val)):
                        break

                i = self.table.find(self.pos)
                ps = self.table.get(i)

                print '%s to act' % (ps.player,)

                class Action(object):
                    def action_check(iself):
                        print 'check'
                        self.post(ps, 0)
                    def action_call(iself):
                        print 'call'
                        # XXX: All in etc
                        self.post(ps, max(self.bets.values()) - self.bets.get(ps, 0))
                    def action_raise(iself, chips):
                        print 'raise', chips
                        self.post(ps, chips)
                    def action_bet(iself, chips):
                        print 'bet', chips
                        self.post(ps, chips)
                    def action_fold(iself):
                        print 'fold'
                        self.active.remove(ps)

                action = Action()
                act = raw_input('check/call/raise/fold?> ')
                if act == 'check':
                    action.action_check()
                elif act == 'call':
                    action.action_call()
                elif 'raise' in act or 'bet' in act:
                    fst, snd = act.split()
                    if fst == 'raise':
                        action.action_raise(int(snd))
                    else:
                        action.action_bet(int(snd))
                elif act == 'fold':
                    action.action_fold()

                acted.add(ps)

                self.pos = i + 1

            if self.sub_state == 'preflop':
                self.state = 'deal-flop'
            elif self.sub_state == 'flop':
                self.state = 'deal-turn'
            elif self.sub_state == 'turn':
                self.state = 'deal-river'
            elif self.sub_state == 'river':
                self.state = 'showdown'
            self.bets = {}
            self.pos = self.dealer + 1

        elif self.state == 'deal-flop':
            print 'DEALING FLOP'

            burn, flop, self.deck = self.deck[0], \
                self.deck[1:4], self.deck[4:]

            self.flop = flop
            print 'flop is %s' % (' '.join(map(str, flop)))

            self.state = 'betting'
            self.sub_state = 'flop'

        elif self.state == 'deal-turn':
            print 'DEALING TURN'

            burn, turn, self.deck = self.deck[0], \
                self.deck[1], self.deck[2:]

            self.turn = turn
            print 'turn is %s' % (turn,)

            self.state = 'betting'
            self.sub_state = 'turn'

        elif self.state == 'deal-river':
            print 'DEALING RIVER'

            burn, river, self.deck = self.deck[0], \
                self.deck[1], self.deck[2:]

            self.river = river
            print 'river is %s' % (river,)

            self.state = 'betting'
            self.sub_state = 'river'

        elif self.state == 'showdown':
            print 'SHOWDOWN'

            if self.active:
                relative = []
                for ps in self.active:
                    best = Hand.best_from_seven(*(ps.hole + self.flop + [self.turn, self.river]))
                    print '%s has %s' % (ps.player, best.classify())
                    relative.append((best, ps))
                relative.sort(reverse=True)

                print 'winners', relative

                #winners = set([ps for (ps, hand) in relative if hand == relative[0][1]])

            self.dealer += 1
            self.state = None


def test_game():
    # set up a bunch of players. These exists independent of games.
    p1 = Player('player 1', 5000)
    p2 = Player('player 2', 3000)
    p3 = Player('player 3', 8000)
    p4 = Player('player 4', 7000)

    # create a game
    t = Table(5)
    rules = GameRules()
    g = Game(t, rules)
    g.set_blinds(20, 10)

    # set up player states for this game
    p1s = PlayerState(p1, 1000)
    p2s = PlayerState(p2, 1000)
    p3s = PlayerState(p3, 1000)
    p4s = PlayerState(p4, 1000)

    t.join(0, p1s)
    t.join(2, p2s)
    #t.join(3, p3s)
    #t.join(4, p4s)

    for i in range(15):
        g.game()


if __name__ == '__main__':
    test_game()
