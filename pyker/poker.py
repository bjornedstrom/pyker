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

# TODO (bjorn): I'm not sure how it happened, but the code below
# turned out to be too-god-d**n-object-oriented :-) Should perhaps
# rewrite to be either more pythonic, or adapt OOP fully.

class Rank(object):
    """A Rank object for playing card ranks, representing Twos,
    Threes, Fours, Fives, Sixs, Sevens, Eights, Nines, Tens, Jacks,
    Queens, Kings and Aces.
    """

    def __init__(self, rank):
        """Construct a Rank.

        :param rank: 2,3,4,5,6,7,8,9,'t','j','q','k','a'.
        :param rank: int or str.
        """

        if rank in ('t', 'T', 'j', 'J', 'q', 'Q', 'k', 'K', 'a', 'A'):
            self.rank = self.__RANKS.index(rank.lower())
        else:
            self.rank = rank

        assert self.rank in xrange(2, 15)

    def __hash__(self):
        return hash(self.rank)

    def __cmp__(self, other):
        return cmp(self.rank, other.rank)

    def __str__(self):
        return self.__RANKS[self.rank]

    def pretty(self):
        """Return a human-readable representation."""

        pretty_rank = {
            14: 'Ace',
            13: 'King',
            12: 'Queen',
            11: 'Jack',
            10: 'Ten',
            9: 'Nine',
            8: 'Eight',
            7: 'Seven',
            6: 'Six',
            5: 'Five',
            4: 'Four',
            3: 'Three',
            2: 'Two',
            }
        return pretty_rank[self.rank]

    def __repr__(self):
        return '<Rank %s>' % (self.rank,)

    __RANKS = 'xx23456789tjqka'

    @staticmethod
    def from_string(s):
        """Construct a new Rank from the string representation.
        """
        try:
            rank = Rank.__RANKS.index(s.lower())
            return Rank(rank)
        except (ValueError, AssertionError):
            raise ValueError('Invalid Rank %s' % (s,))

class Card(object):
    """A playing card, which has a rank and a suit.
    """

    HEART = 'h'
    SPADES = 's'
    CLUBS = 'c'
    DIAMONDS = 'd'

    def __init__(self, rank, suit):
        """Create a new playing card.

        You probably want to use Card.from_string().

        :param rank: rank of the card.
        :type rank: Rank.
        :param suit: the suit ("color") of the card, one of 'h', 's',
            'c', 'd'.
        :type suit: str.
        """

        self.rank = rank
        self.suit = suit

        assert self.suit in ('h', 's', 'c', 'd')

    def __str__(self):
        return '%s%s' % (self.rank, self.suit)

    def __repr__(self):
        return '<Card rank=%r suit=%s>' % (self.rank, self.suit)

    @staticmethod
    def from_string(s):
        """Construct a new Card from the string representation.
        """

        try:
            rank_str, suit = s[0], s[1]
        except:
            raise ValueError('Invalid Card %s' % (s,))
        rank = Rank.from_string(rank_str)
        try:
            return Card(rank, suit)
        except AssertionError:
            raise ValueError('Invalid Card %s' % (s,))

class HandClass(object):
    def score(self):
        """Calculate an integer score for this hand classification.
        """

        # Scoring works by considering each HandClass as a tuple, most
        # significant information first, and converting this tuple to
        # a base-13 integer (because their are 13 unique ranks).
        #
        # For example, a three-of-a-kind an be uniquely identified by
        # the 5-tuple:
        #
        # (three-of-a-kind, <card in threes>, <highest kicker>,
        # <middle kicker>, <lowest kicker>)
        #
        # The most significant item in the tuple is the type of the
        # hand class itself. This we get from HandClass.SCORE:
        score = self.SCORE * 13**5

        # HandClasses implement _score() which returns the remaining
        # tuple of Ranks, ordered with most significant information
        # first:
        ranks = self._score()
        for i, r in enumerate(reversed(ranks)): #xrange(len(ranks)):
            # Subtract 2 so we can use a base-13 number instead of
            # base-15.
            score += (r.rank - 2) * 13**i
        return score

    def _score(self):
        raise NotImplementedError('not implemented')

    def __cmp__(self, other):
        return cmp(self.score(), other.score())

    def __repr__(self):
        return '<%s %r>' % (self.__class__.__name__, self.__dict__)

class StraightFlush(HandClass):
    SCORE = 8

    def __init__(self, highest):
        self.highest = highest

    def _score(self):
        return (self.highest,)

    def __str__(self):
        return 'Straight Flush, %s High' % (self.highest.pretty(),)

class FourOfAKind(HandClass):
    SCORE = 7

    def __init__(self, four, kicker):
        self.four = four
        self.kicker = kicker

    def _score(self):
        return (self.four, self.kicker)

    def __str__(self):
        return 'Four of a Kind of %ss, kicker %s' % (self.four.pretty(), self.kicker.pretty())

class FullHouse(HandClass):
    SCORE = 6

    def __init__(self, three, two):
        self.three = three
        self.two = two

    def _score(self):
        return (self.three, self.two)

    def __str__(self):
        return 'Full House, 3 %ss and 2 %ss' % (self.three.pretty(), self.two.pretty())

class Flush(HandClass):
    SCORE = 5

    def __init__(self, kickers):
        self.kickers = kickers

    def _score(self):
        return  self.kickers

    def __str__(self):
        return 'Flush with %s' % (', '.join(map(lambda s: s.pretty(), self.kickers)),)

class Straight(HandClass):
    SCORE = 4

    def __init__(self, highest):
        self.highest = highest

    def _score(self):
        return (self.highest,)

    def __str__(self):
        return 'Straight, %s High' % (self.highest.pretty(),)

class ThreeOfAKind(HandClass):
    SCORE = 3

    def __init__(self, three, kickers):
        self.three = three
        self.kickers = kickers

    def _score(self):
        return (self.three,) + self.kickers

    def __str__(self):
        kickers = ', '.join(map(lambda s: s.pretty(), self.kickers))
        return 'Three of a Kind of %ss with %s' % (self.three.pretty(), kickers)

class TwoPair(HandClass):
    SCORE = 2

    def __init__(self, high_pair, low_pair, kicker):
        self.high_pair = high_pair
        self.low_pair = low_pair
        self.kicker = kicker

    def _score(self):
        return (self.high_pair, self.low_pair, self.kicker)

    def __str__(self):
        return 'Two Pairs of %ss and %ss, kicker %s' % (self.high_pair.pretty(), self.low_pair.pretty(), self.kicker.pretty())

class Pair(HandClass):
    SCORE = 1

    def __init__(self, pair, kickers):
        self.pair = pair
        self.kickers = kickers

    def _score(self):
        return (self.pair,) + self.kickers

    def __str__(self):
        kickers = ', '.join(map(lambda s: s.pretty(), self.kickers))
        return 'Pair of %ss with %s' % (self.pair.pretty(), kickers)

class Highest(HandClass):
    SCORE = 0

    def __init__(self, kickers):
        self.kickers = kickers

    def _score(self):
        return self.kickers

    def __str__(self):
        return 'Highest Cards %s' % (', '.join(map(lambda s: s.pretty(), self.kickers)),)

class Hand(object):
    """A poker hand which is conceptually a set of cards.
    """

    def __init__(self, cards):
        """Create a new Hand.

        :param cards: A list of Cards.
        :type cards: [Card].
        """

        self.cards = cards

    def __cmp__(self, other):
        return cmp(self.classify(), other.classify())

    def classify(self):
        """Attempt to classify this hand to a subclass of HandClass.

        :returns: A HandClass instance.
        """

        assert len(self.cards) == 5

        ranks = sorted((c.rank for c in self.cards))

        # Highest card if straight
        straight = None

        # Special case when ace is low:
        if ranks == [Rank(2), Rank(3), Rank(4), Rank(5), Rank('A')]:
            straight = Rank(5)

        # All the other ("normal") straights:
        elif ranks == map(Rank, range(ranks[0].rank, ranks[4].rank + 1)):
            straight = ranks[4]

        # Is a flush?
        flush = all((c.suit == self.cards[0].suit
                     for c in self.cards))

        # We now have enough info to determine three hand classes:
        if straight is not None and flush:
            return StraightFlush(straight)

        if flush:
            return Flush((ranks[4], ranks[3], ranks[2], ranks[1], ranks[0]))

        if straight is not None:
            return Straight(straight)

        # Determine pairs, required for further classifications.
        pairs = {}
        for r in ranks:
            try:
                pairs[r] += 1
            except:
                pairs[r] = 1
        has = {
            1: [],
            2: [],
            3: [],
            4: [],
            }
        for r, num in pairs.iteritems():
            has[num].append(r)

        if has[4]:
            return FourOfAKind(max(has[4]), max(has[1]))

        if has[3] and has[2]:
            return FullHouse(max(has[3]), max(has[2]))

        if has[3]:
            return ThreeOfAKind(max(has[3]), (max(has[1]), min(has[1])))

        if len(has[2]) == 2:
            return TwoPair(max(has[2]), min(has[2]), max(has[1]))

        if len(has[2]) == 1:
            kick = sorted(has[1])
            return Pair(max(has[2]), (kick[2], kick[1], kick[0]))

        return Highest((ranks[4], ranks[3], ranks[2], ranks[1], ranks[0]))

    @staticmethod
    def best_from_seven(*cards):
        """Given 7 cards, construct the best 5 card hand.

        :param *cards: list of cards
        :type *cards: [Card]
        :returns: Hand
        """
        # Instead of thinking of this as "7 choose 5", we think of "7
        # remove 2" which is easier to implement.

        best = None
        for r1 in range(7):
            for r2 in range(r1 + 1, 7):
                hand = Hand([cards[i] for i in range(7) if i not in (r1, r2)])
                best = hand if best is None else max(best, hand)
        return best

    @staticmethod
    def from_string(s):
        """Construct a new Hand from the string representation.
        """

        return Hand(map(Card.from_string, s.split()))

    def __repr__(self):
        return '<Hand %s>' % (' '.join(map(str, self.cards)))


def string_to_cards(s):
    """Given a string, return a list of Cards.
    """

    return map(Card.from_string, s.split())


if __name__ == '__main__':
    c1 = Card.from_string('9h')
    c2 = Card.from_string('th')

    hh = [
        '7h 8h 9h th jh',
        '7h 7s 7c 7d jh',
        '3h 3c 3s tc th',
        '7h 8h 2h th jh',
        '9c 8h 7d td jh',
        '3c 3h 3d td js',
        '2c 2s 3d 3h jd',
        '7c 4s 4d th jd',
        'kc as 9d 3h 2d'
    ]

    for h in hh:
        #print h, repr(Hand.from_string(h).classify())
        print h,
        try:
            print Hand.from_string(h).classify().score()
        except Exception, e:
            print 'failed', e

    print Hand.best_from_seven(*string_to_cards('kc as 9d 3h 2d ac ks')).classify()
