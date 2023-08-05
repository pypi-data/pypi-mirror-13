from .grammar import GrammarError, NonTerminal
from .lexer import Lexer
from .lr import LR


class SLR(LR):

    def _closure(self, items):
        """ An item is a pair:
            (n, P) for P a Production, 0 <= n <= len(P.rhs)
        """
        new = set(items)
        result = set()

        while len(new) > 0:
            result.update(new)
            for (n, p) in set(new):
                if n == len(p.rhs):
                    continue
                b = p.rhs[n]
                if isinstance(b, NonTerminal):
                    new.update((0, r) for r in b.productions)
            new.difference_update(result)

        return frozenset(result)

    def _goto(self, items, symbol):
        """ goto(I, X)
            where I is a set of items and X is a grammar symbol,
            is the closure of the set of all items,
                A -> a X . b
            such that
                A -> a . X b
            is in I.
        """

        return self._closure({
            (n + 1, p)
            for (n, p) in items
            if n < len(p.rhs) and p.rhs[n] == symbol
        })

    def _sets_of_items(self, start):
        """ The starting production - which may be augmented - is passed in """

        c = set()
        symbols = self.symbols

        new = {self._closure({(0, start)})}
        while len(new) > 0:
            c.update(new)
            for items in set(new):
                for x in symbols:
                    goto = self._goto(items, x)
                    if len(goto) > 0:
                        new.add(goto)
            new.difference_update(c)
        return c

    def compile(self, start, augment=True):
        self.nt._validate()
        self._clear_caches()

        if augment:
            start = self.augment(start)

        # We must have a single start production
        if len(start.productions) != 1:
            raise GrammarError(
                "There should be 1 production for {start}, not {n}"
                .format(start=start.id, n=len(start.productions))
            )

        start_ = list(start.productions)[0]

        self._start_symbol = start
        self._terminals = self.terminals

        self._compile(start_)
        return self._start_symbol

    def _compile(self, starting_production):
        c = self._sets_of_items(starting_production)
        sets = list(c)
        index = {s: n for n, s in enumerate(sets)}

        action = {}
        goto = {}
        s0 = None

        for i, items in enumerate(sets):
            for n, p in items:
                if n == 0 and p == starting_production:
                    if s0 is not None:
                        raise GrammarError(
                            "Multiple start states found, {s0} and {i}"
                            .format(s0=s0, i=i))
                    s0 = i
                if n < len(p.rhs) and not isinstance(p.rhs[n], NonTerminal):
                    g = self._goto(items, p.rhs[n])
                    if (i, p.rhs[n]) in action:
                        raise GrammarError(
                            "Conflicting actions for the production {p}"
                            .format(p=p))
                    action[i, p.rhs[n]] = LR.Shift(index[g])
                elif n == len(p.rhs):
                    if p == starting_production:
                        if (i, Lexer.EOF) in action:
                            raise GrammarError(
                                "Multiple actions for EOF")
                        action[i, Lexer.EOF] = LR.Accept()
                    else:
                        for a in self.follow(p.nt):
                            if (i, a) in action:
                                raise GrammarError(
                                    "Conflict in state {s} on terminal {t}"
                                    .format(s=i, t=a))
                            action[i, a] = LR.Reduce(p)

            for nt in self.nonterminals:
                g = self._goto(items, nt)
                if g in index:
                    goto[i, nt] = index[g]

        if s0 is None:
            raise GrammarError("No start state found")

        self._action_table = action
        self._goto_table = goto
        self._s0 = s0
