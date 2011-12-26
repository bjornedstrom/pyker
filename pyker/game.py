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
from pyker.pots import Pots


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


class GameError(Exception):
    pass


class Game(object):
    def __init__(self, table, rules):
        self.table = table
        self.rules = rules

        # The dealer button is a piece of state that changes between
        # successive games. Most other state is state for the actual
        # game. This state is set up in the state machine code.
        self.dealer = -1

        # Seed for the state machine.
        self.state = 'init'

    def set_blinds(self, big, small):
        self.bb = big
        self.sb = small

    def next(self):
        while True:
            p = self.table.get(self.pos)
            self.pos += 1
            if p is not None:
                return p

    # TODO (bjorn): This code is too hairy and difficult to
    # understand. It probably has lots of bugs. Improve!
    def post(self, ps, chips):
        _chips = chips

        self.pots.post(ps, chips)

        # Update bets. This doesn't care about side pots etc, it's
        # just what the player attempted to match this betting round.
        try:
            self.bets[ps] += _chips
        except:
            self.bets[ps] = _chips

        print 'bets:', ' '.join(('%s=%s' % (k.player, v) for (k, v) in self.bets.iteritems()))

    # modifies: self.pots, self.bets, self.active,
    # self.deck, self.flop, self.turn, self.river,
    # self.dealer
    def _state_init(self):
        # Active players are players remaining at table with remaining
        # chips.
        self.active = set()
        for pos in range(self.table.num_seats):
            ps = self.table.get(pos)
            if ps is not None and ps.chips > 0:
                self.active.add(ps)

        if len(self.active) < 2:
            raise GameError('game over - too few funded players left')

        # There can be multiple pots, per table-stakes rules.
        self.pots = Pots()

        self.bets = {} # ps -> attempted bet

        # The deck
        deck = []
        for suit in 'hscd':
            for rank in map(Rank, range(2, 15)):
                deck.append(Card(rank, suit))
        random.shuffle(deck)
        self.deck = deck

        # The community cards.
        self.flop = []
        self.turn = None
        self.river = None

        # We could advance the dealer when the game has ended, but
        # since that can happen at multiple places it's more
        # convienient to do it once, here. If we want a particular
        # seat as dealer, we must remember to subtract one when we set
        # it.
        self.dealer += 1

    # modifies: self.deck
    def _state_deal_hole_cards(self):
        dealer = self.table.find(self.dealer)
        print '%s is dealer' % (self.table.get(dealer).player)

        for pos in range(dealer + 1,
                         dealer + 1 + self.table.num_seats):
            ps = self.table.get(pos)
            if ps is None:
                continue
            ps.hole, self.deck = self.deck[0:2], self.deck[2:]

            print 'dealt hole cards to %s' % (ps.player)

    # modifies: self.deck, self.flop
    def _state_deal_flop(self):
        burn, flop, self.deck = self.deck[0], \
            self.deck[1:4], self.deck[4:]

        self.flop = flop
        print 'flop is %s' % (' '.join(map(str, flop)))

    # modifies: self.deck, self.turn
    def _state_deal_turn(self):
        burn, turn, self.deck = self.deck[0], \
            self.deck[1], self.deck[2:]

        self.turn = turn
        print 'turn is %s' % (turn,)

    # modifies: self.deck, self.river
    def _state_deal_river(self):
        burn, river, self.deck = self.deck[0], \
            self.deck[1], self.deck[2:]

        self.river = river
        print 'river is %s' % (river,)

    # modifies: self.pos
    # calls: self.post
    def _state_post_blinds(self):
        pos = self.table.find(self.dealer)
        print '%s is dealer' % (self.table.get(pos).player)

        # If there are only two players, the dealer will post the
        # small blinds. Otherwise, it's the next player.
        if self.table.players() > 2:
            pos += 1

        player_sb_idx = self.table.find(pos)
        player_sb = self.table.get(player_sb_idx)

        print '%s posting small blind' % (player_sb.player,)
        self.post(player_sb, self.sb)

        player_bb_idx = self.table.find(player_sb_idx + 1)
        player_bb = self.table.get(player_bb_idx)

        print '%s posting big blind' % (player_bb.player,)
        self.post(player_bb, self.bb)

        self.pos = player_bb_idx + 1

    # modifies: self.pos, self.bets
    # calls: self.post
    def _state_betting(self):
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

            # Construct a setof valid options for the player.
            options = set(['fold'])
            if not self.bets or sum(self.bets.values()) == 0:
                options.add('bet') # open
                options.add('check')
            else:
                # TODO (bjorn): BB can check here (which is the same
                # as call).
                options.add('call')
                options.add('raise')

            # A context to execute the options.
            class Action(object):
                def action_check(iself):
                    if 'check' not in options:
                        raise GameError('invalid check')
                    print 'check'
                    self.post(ps, 0)
                def action_call(iself):
                    if 'call' not in options:
                        raise GameError('invalid call')
                    print 'call'
                    # XXX: All in etc
                    self.post(ps, max(self.bets.values()) - self.bets.get(ps, 0))
                def action_raise(iself, chips):
                    if 'raise' not in options or chips > ps.chips:
                        raise GameError('invalid raise')
                    print 'raise', chips
                    self.post(ps, chips)
                def action_bet(iself, chips):
                    if 'bet' not in options or chips > ps.chips:
                        raise GameError('invalid bet')
                    print 'bet', chips
                    self.post(ps, chips)
                def action_fold(iself):
                    print 'fold'
                    self.active.remove(ps)

            if ps.chips and len([pso for pso in self.active if pso.chips]) > 1:
                # Yield execution to the main loop.
                yield options, Action()
            else:
                if ps.chips == 0:
                    print '%s has no chips left' % (ps.player,)
                else:
                    print '%s is the sole player with chips left - skipping' % (ps.player,)
                    break

            acted.add(ps)
            self.pos = i + 1

        self.bets = {}
        self.pos = self.dealer + 1

    # modifies:
    def _state_showdown(self):
        if not self.active:
            return

        print 'community cards are %s' % ' '.join(map(str, self.flop + [self.turn, self.river]))

        relative = []
        for ps in self.active:
            best = Hand.best_from_seven(*(ps.hole + self.flop + [self.turn, self.river]))
            print '%s has %s, best hand is %s' % (ps.player, ' '.join(map(str, ps.hole)), best.classify())
            relative.append((best, ps))
        relative.sort(reverse=True)

        # TODO (bjorn): Leaky! Do not touch self.pots.pots
        for pot_idx, stakes in self.pots.pots.iteritems():
            ordering = [(best, ps) for (best, ps) in relative if ps in stakes]
            winners = [w for w in ordering if w[0] == ordering[0][0]]
            won = sum(stakes.values()) / len(winners)
            for _, ps in winners:
                print '%s won %s from pot %s' % (ps.player, won, pot_idx)
                ps.chips += won

    def loop(self):
        while True:
            yield self.game()

    def game(self):
        ret = None
        # Transitions for the game state machine.
        if self.state == 'init':
            print 'INIT'
            self._state_init()
            self.state = 'deal-hole'
        elif self.state == 'deal-hole':
            print 'DEALING CARDS'
            self._state_deal_hole_cards()
            self.state = 'blinds'
        elif self.state == 'blinds':
            print 'POSTING BLINDS'
            self._state_post_blinds()
            self.state = 'betting'
            self.sub_state = 'preflop'
        elif self.state == 'betting':
            print 'BETTING', self.sub_state
            ret = self._state_betting()
            if self.sub_state == 'preflop':
                self.state = 'deal-flop'
            elif self.sub_state == 'flop':
                self.state = 'deal-turn'
            elif self.sub_state == 'turn':
                self.state = 'deal-river'
            elif self.sub_state == 'river':
                self.state = 'showdown'
        elif self.state == 'deal-flop':
            print 'DEALING FLOP'
            self._state_deal_flop()
            self.state = 'betting'
            self.sub_state = 'flop'
        elif self.state == 'deal-turn':
            print 'DEALING TURN'
            self._state_deal_turn()
            self.state = 'betting'
            self.sub_state = 'turn'
        elif self.state == 'deal-river':
            print 'DEALING RIVER'
            self._state_deal_river()
            self.state = 'betting'
            self.sub_state = 'river'
        elif self.state == 'showdown':
            print 'SHOWDOWN'
            self._state_showdown()
            self.state = 'init'
        else:
            raise AssertionError('invalid state %s' % (self.state,))

        yield ret



def test_pots():
    p1 = Player('player 1', 5000)
    p2 = Player('player 2', 3000)
    p3 = Player('player 3', 8000)
    p4 = Player('player 4', 7000)

    t = Table(5)
    rules = GameRules()
    g = Game(t, rules)
    g.set_blinds(20, 10)

    p1s = PlayerState(p1, 100)
    p2s = PlayerState(p2, 200)
    p3s = PlayerState(p3, 233)
    p4s = PlayerState(p4, 250)

    t.join(0, p1s)
    t.join(2, p2s)
    t.join(3, p3s)
    t.join(4, p4s)

    g._state_init()
    g.post(p1s, 150)
    g.post(p2s, 150)
    g.post(p3s, 150)
    g.post(p4s, 150)

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
    p2s = PlayerState(p2, 500)
    p3s = PlayerState(p3, 600)
    p4s = PlayerState(p4, 700)

    t.join(0, p1s)
    t.join(2, p2s)
    t.join(3, p3s)
    t.join(4, p4s)


    for gen in g.loop():
        action_gen = gen.next()
        if action_gen is None:
            continue

        for options, action in action_gen:

            while True:
                act = raw_input('%s?> ' % '/'.join(options))

                try:
                    if act == 'check':
                        action.action_check()
                        break
                    elif act == 'call':
                        action.action_call()
                        break
                    elif 'raise' in act or 'bet' in act:
                        try:
                            fst, snd = act.split()
                            name = fst
                            chips = int(snd)
                        except Exception, e:
                            print 'invalid input: %s' % (act,)
                            continue

                        if name == 'raise':
                            action.action_raise(chips)
                        else:
                            action.action_bet(chips)
                        break
                    elif act == 'fold':
                        action.action_fold()
                        break
                    else:
                        print 'invalid input: %s' % (act,)
                except GameError, e:
                    print e


if __name__ == '__main__':
    test_game()
