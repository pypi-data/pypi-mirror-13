Things left to do and known outstanding issues
----------------------------------------------

- Provide freeze/thaw support to load the results of an
  expensive compilation stage from persistent storage.

- try not to rathole into writing a general parser generator.
  (too late)

- implement GLR or a variant.

- look at other surface syntaxes:

We could use some more reflection to go from this:

@n.E(n.T, '+', n.E)
def f(t, _, e):

... which tends to repeat itself, to something using annotations perhaps:

@n.E()   # still a funcall - need to specify things like prec here
(... or do we?)
def f(t: n.T, _: '+', e: n.E):

I have no idea now that I look at that whether it's more readable.

- Experiment with a second surface syntax:

    class g(Grammar):

        def E(t1: T, _: '+', t2: T):
            return t1 + t2

        def E(t: T):
            return t

        def T(i: int):
            return i

(This may not be completely possible with Python; making it work, even
were this actually possible, would represent a massive ugly metaclass
hack.)

- Experiment with adding error productions for _useful_ error
  recovery.

- Get the lexer to actually consume a stream rather than a string.
  Ideally, do this without reimplementing the entirety of Python's
  're' module in native Python.

- Permit lexer actions to directly access the remaining input stream.

- Permit lexer rules to say "nope, this doesn't match after all!"

- Do something more useful with my spare time.
