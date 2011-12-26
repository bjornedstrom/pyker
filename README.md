pyker
=====

Python Poker code.

This is really a companion to my haskell-holdem project. It may
eventually turn into something useful. Right now I use it for
sketching.

- Björn


pyker-pots
----------

`pyker-pots` is a command line utility to visualize how bets will
affect main and side pots. Run `pyker-pots -h` for usage information.

For example, the pots on this [MyPokerCorner article](http://www.mypokercorner.com/poker-strategy/general-concepts/how-to-calculate-poker-side-pots/) can be visualized using the command:

    $ pyker-pots -p p1=1000 -p p2=1000 -p p3=1000 -p p4=200 \
          p1=50 p2=50 p3=50 p4=50 \
          p1=100 p2=100 p3=200 p4=150 p1=100

The Game
--------

You can run pyker/game.py for a semi-working No-Limit Texas Hold'em
game where you control all players. It is not done yet...
