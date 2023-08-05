Yet Another LR Implementation
=============================

This is another implementation of the classic LR(1) parsing
algorithm, along with Knuth's LR(1) table generation algorithm.

Rather than follow the model of tools like yacc and require
external code generation, this library is driven dynamically
from Python code.

An obvious question is, "why?"

Two reasons:

- firstly, to experiment with surface syntax for expressing
  grammars in Python code in as uninvasive a way as possible.

  The package "ptk" takes a similar approach here.

- secondly, to provide a playground to look at other
  "cutting-edge" parsing algorithms, as a basis for improving
  my own understanding of them.

By "cutting-edge" I'm largely referring to the late 1970s.

The current implementation is largely inspired by yacc,
including yacc's various deficiencies:

- there's a linearisation used for reduce/reduce conflict
  resolution;

- there's a linearisation used for token precedence.

In practice, it's easy to get bitten by both of these - as
it is for the default shift/reduce resolution to mask
errors. A more flexible partial ordering is certainly feasible.

Credits
=======

Some of the example grammars included in the tests are derived
from the (Red) Dragon Book, which I've had since I was about 16;
it's a book which definitely shaped my life.

I've no idea how the reference numbers line up with later
additions.

    Compilers: Principles, Techniques, and Tools (1986)
    by Alfred V. Aho, Ravi Sethi and Jeffrey D. Ullman

