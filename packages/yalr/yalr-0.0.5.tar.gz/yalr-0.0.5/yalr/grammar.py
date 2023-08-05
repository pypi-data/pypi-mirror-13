class Grammar(object):

    def __init__(self, *args, **kwargs):
        super(Grammar, self).__init__(*args, **kwargs)
        self.nt = Nonterminals(self)
        self._precedence = []
        self._generation = 0

    def compile(self, start=None):
        raise NotImplementedError()

    def parse(self, stream=None):
        raise NotImplementedError()

    def productions(self, nt=None):
        return self.nt._productions(nt)

    @property
    def terminals(self):
        return self.nt._terminals()

    @property
    def nonterminals(self):
        return self.nt._nonterminals()

    @property
    def symbols(self):
        return self.terminals.union(self.nonterminals)

    # precedence markers
    Left = object()
    Right = object()
    NonAssoc = object()

    def precedence(self, assoc, *args):
        self._precedence.append((assoc, frozenset(args)))

    def left(self, *args):
        self.precedence(Grammar.Left, *args)

    def right(self, *args):
        self.precedence(Grammar.Right, *args)

    def nonassoc(self, *args):
        self.precedence(Grammar.NonAssoc, *args)

    # Support for rule ordering by age
    def _count(self):
        self._generation += 1
        return self._generation


class GrammarError(Exception):
    def __init__(self, *args, **kwargs):
        super(GrammarError, self).__init__(*args)
        self.kwargs = kwargs

    def __str__(self):
        s = super(GrammarError, self).__str__()
        if self.kwargs:
            s += (' {' +
                  ', '.join(k + ': ' + str(self.kwargs[k])
                            for k in sorted(self.kwargs)) +
                  '}')
        return s


class Nonterminals(object):

    def __init__(self, grammar):
        self._grammar = grammar
        self._nt = {}

    def __getattr__(self, id):
        if id.startswith('_'):
            return
        try:
            return self._nt[id]
        except KeyError:
            nt = NonTerminal(id, self._grammar)
            self._nt[id] = nt
            return nt

    def _validate(self):
        for id in self._nt:
            if len(self._nt[id].alts) == 0:
                raise GrammarError("Non-terminal {id} has no productions"
                                   .format(id=id))

    def _terminals(self):
        terminals = set()
        for id in self._nt:
            terminals.update(self._nt[id].terminals())
        return terminals

    def _nonterminals(self):
        return set(self._nt.values())

    def _productions(self, nt=None):
        if nt is not None:
            assert nt == self._nt[nt.id]
            return nt.productions

        prods = set()
        for id in self._nt:
            prods.update(self._nt[id].productions)
        return prods


class NonTerminal(object):

    def __init__(self, id, grammar):
        self.id = id
        self.grammar = grammar
        self.alts = []

    def __call__(self, *args, **kwargs):
        prec = kwargs.get('prec')

        def decorate(f):
            self.alts.append(
                Production(self, args, prec=prec, fn=f,
                           gen=self.grammar._count())
            )
        return decorate

    def terminals(self):
        terminals = set()
        for alt in self.alts:
            terminals.update(alt.terminals())
        return terminals

    @property
    def productions(self):
        return set(self.alts)

    def __str__(self):
        return self.id

    def __getitem__(self, args):
        if not isinstance(args, tuple):
            args = (args,)
        for p in self.alts:
            if p.rhs == args:
                return p
        raise KeyError(args)


class Production(object):

    Empty = object()

    def __init__(self, nt, rhs, prec=None, fn=None, gen=0):
        self.nt = nt
        self.rhs = rhs
        self.prec = prec
        self.fn = fn
        self.gen = gen

    def terminals(self):
        terminals = set()
        for symbol in self.rhs:
            if isinstance(symbol, NonTerminal):
                continue
            terminals.add(symbol)
        return terminals

    def __str__(self):
        s = "{id} -> {items}".format(
            id=self.nt,
            items=" ".join(str(s) for s in self.rhs)
        )
        if self.prec is not None:
            s += " %prec {}".format(self.prec)
        return s
