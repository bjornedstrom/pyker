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

""" module for handling multiple pots.
"""

class Pots(object):
    """Keeps track of the different pots, who has stakes in each etc.
    """

    def __init__(self):
        self.clear()

    def clear(self):
        self.pots = {} # name -> ps -> num chips
        self.pots_limited = {} # name -> limited?

    def post(self, ps, chips):
        """Post a bet into the pots.

        :param ps: An arbitrary "player struct". ps can be anything
           as long as it has a mutable attribute "chips" which chips
           will be drawn from and put into the pots. For example, this
           will work:

           class Player(object):
               def __init__(self):
                  self.chips = 3500

        :param chips: The number of chips the player attempts to
          post. This can be higher than the players current chip
          (which can happen if the player calls, for example).
        """

        if not self.pots:
            # Create main pot
            print 'creating pot 0'
            self.pots[0] = {}
            self.pots_limited[0] = False

        # Find the pots this player has a stake in and has not fully
        # contributed to:
        new_pots = []
        for pot_idx, stakes in self.pots.iteritems():
            if ps.chips == 0 or chips == 0:
                break

            if ps not in stakes:
                stakes[ps] = 0

            # Determine how many chips to post in this pot, and
            # whether it means player goes all-in.
            all_in = False
            post = chips
            if self.pots_limited[pot_idx]:
                post = min(post, max(stakes.values()) - stakes[ps])
            if post >= ps.chips:
                post = ps.chips
                all_in = True

            # Move chipts from the player to the pot
            ps.chips -= post
            stakes[ps] += post
            chips -= post

            print '%s posts %s in pot %s - player has %s remaining. All In: %s' % (ps, post, pot_idx, ps.chips, all_in)

            # Mark this as a limited pot: further bets may create a
            # side pot.
            if all_in:
                self.pots_limited[pot_idx] = True

                # Maybe move chips to a side pot
                new_side_pot = {}
                for other_ps, value in stakes.iteritems():
                    if value > stakes[ps]:
                        new_side_pot[other_ps] = value - stakes[ps]
                        stakes[other_ps] = stakes[ps]
                if new_side_pot:
                    new_pots.append(new_side_pot)

        for new_pot in new_pots:
            i = max(self.pots.keys()) + 1
            self.pots[i] = new_pot
            self.pots_limited[i] = False

        # Player has remaining chips. Create new pot
        if ps.chips and chips:
            i = max(self.pots.keys()) + 1
            self.pots[i] = {}
            self.pots_limited[i] = False

            print 'creating pot %s' % i

            self.pots[i][ps] = chips
            ps.chips -= chips
            print '%s posts %s in pot %s - player has %s remaining' % (ps, chips, i, ps.chips)
            chips = 0


        print 'pots:'
        for name, pot in self.pots.iteritems():
            print 'pot %d (limited: %s)' % (name, self.pots_limited[name])
            for k, v in pot.iteritems():
                print "\t", k, "\t", v

    def list(self):
        """Yields information about pots and which players have stakes
        in them.
        """

        for name, pot in self.pots.iteritems():
            if pot:
                yield pot.keys(), sum(pot.values())
