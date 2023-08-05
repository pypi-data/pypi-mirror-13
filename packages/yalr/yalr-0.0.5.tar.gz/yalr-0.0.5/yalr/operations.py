from .grammar import NonTerminal, Production, GrammarError
from .lexer import Lexer


class GrammarOperations(object):
    def __init__(self, *args, **kwargs):
        super(GrammarOperations, self).__init__(*args, **kwargs)
        self._clear_caches()
        self._start_symbol = None

    def _clear_caches(self):
        self._first_cache = None
        self._follow_cache = None
        self._precedence_cache = None

    @property
    def start(self):
        return self._start_symbol

    def _first(self, symbol):
        if self._first_cache is not None:
            return self._first_cache[symbol]

        first = {t: {t} for t in self.terminals}
        for nt in self.nonterminals:
            for p in nt.productions:
                if len(p.rhs) == 0:
                    first[nt] = {Production.Empty}
                else:
                    first[nt] = set()

        changed = True

        while changed:
            changed = False
            for nt in self.nonterminals:
                for p in nt.productions:
                    for y in p.rhs:
                        empty = False
                        for a in first[y]:
                            if a == Production.Empty:
                                empty = True
                            else:
                                if a not in first[nt]:
                                    first[nt].add(a)
                                    changed = True
                        if not empty:
                            break
                    else:
                        if Production.Empty not in first[nt]:
                            first[nt].add(Production.Empty)
                            changed = True

        self._first_cache = first
        return first[symbol]

    def first(self, rhs):
        first = set()
        for symbol in rhs:
            if symbol == Lexer.EOF:
                first.add(Lexer.EOF)
                break
            elif Production.Empty in self._first(symbol):
                first.update(self._first(symbol)
                             .difference({Production.Empty}))
            else:
                first.update(self._first(symbol))
                break
        else:
            first.add(Production.Empty)

        return first

    def follow(self, nt, start=None):
        if self._follow_cache is not None:
            return self._follow_cache[nt]

        if start is None:
            start = self._start_symbol

        follow = {nt: set() for nt in self.nonterminals}
        follow[start].add(Lexer.EOF)

        changed = True

        while changed:
            changed = False
            for p in self.productions():
                for i, b in enumerate(p.rhs):
                    if not isinstance(b, NonTerminal):
                        continue
                    rest = p.rhs[i + 1:]
                    if len(rest) > 0:
                        additional = (self.first(rest)
                                      .difference({Production.Empty}))
                        if Production.Empty in self.first(rest):
                            additional.update(follow[p.nt])
                    else:
                        additional = set(follow[p.nt])

                    additional.difference_update(follow[b])
                    if len(additional) > 0:
                        follow[b].update(additional)
                        changed = True

        self._follow_cache = follow
        return follow[nt]

    def augment(self, start):
        # Augment the grammar
        wrap = NonTerminal('<start>', self)
        wrap(start,)(id)
        start = self.nt._nt['<start>'] = wrap
        start.gen = 0
        return start

    # Functions for managing terminal precedence

    def _terminal_precedence(self, term):
        """ Give a computed precedence and associativity
            for the supplied terminal symbol.

            Precedence levels are from 0 (lowest)
            and increase positively with tighter binding.
        """

        if self._precedence_cache is None:

            cache = {}
            for level, (assoc, terms) in enumerate(self._precedence):
                for t in terms:
                    if t in cache:
                        raise GrammarError(
                            "Terminal {t} has multiple precedences".
                            format(t=t))
                    cache[t] = (level, assoc)

            self._precedence_cache = cache

        try:
            return self._precedence_cache[term]
        except KeyError:
            raise GrammarError("No precedence given for terminal {t}"
                               .format(t=term))

    def _rule_precedence(self, prod):
        """ Give a computed precedence level for a production.
            This is the specified value if there is one,
            otherwise it'll be the precedence of
            its rightmost terminal symbol.
        """

        if prod.prec is not None:
            return self._terminal_precedence(prod.prec)

        rightmost = None
        for x in prod.rhs:
            if not isinstance(x, NonTerminal):
                rightmost = x

        try:
            return self._terminal_precedence(rightmost)
        except KeyError:
            raise GrammarError("No value given when looking for "
                               "precedence for rule {p}"
                               .format(p=prod))
