import logging

from .grammar import Grammar, GrammarError, NonTerminal
from .lexer import Lexer
from .lr import LR

LOG = logging.getLogger(__name__)


class LR1(LR):

    def _closure(self, items):
        """ An item is a triple:
            (n, P, t) for P a Production,
                          0 <= n <= len(P.rhs),
                          t a terminal symbol
        """
        new = set(items)
        result = set()

        while len(new) > 0:
            result.update(new)
            for (n, p, a) in set(new):
                if n == len(p.rhs):
                    continue
                b = p.rhs[n]
                if not isinstance(b, NonTerminal):
                    continue
                for t in self.first(p.rhs[n + 1:] + (a,)):
                    new.update((0, r, t) for r in b.productions)
            new.difference_update(result)

        return frozenset(result)

    def _goto(self, items, symbol):
        """ goto(I, X)
            where I is a set of items and X is a grammar symbol,
            is the closure of the set of all items,
                A -> a X . b; t
            such that
                A -> a . X b; t
            is in I.
        """

        return self._closure({
            (n + 1, p, a)
            for (n, p, a) in items
            if n < len(p.rhs) and p.rhs[n] == symbol
        })

    def _sets_of_items(self, start):
        """ The starting production - which may be augmented - is passed in """

        c = set()
        symbols = self.symbols

        new = {self._closure({(0, start, Lexer.EOF)})}
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
            for n, p, b in items:

                # if [A -> alpha . a beta; b] is in I_i,
                #  a a terminal, and goto(I_i, a) = I_j,
                #  then set action[i, a] to 'shift j'

                if n < len(p.rhs) and not isinstance(p.rhs[n], NonTerminal):
                    g = index[self._goto(items, p.rhs[n])]
                    a = p.rhs[n]

                    action[i, a] = self._conflict(action.get((i, a)),
                                                  LR.Shift(g),
                                                  lookahead=a)

                # if [A -> alpha . ; a] is in I_i, A != S',
                # then set action[i, a] to 'reduce A -> alpha'

                if n == len(p.rhs) and p != starting_production:
                    action[i, b] = self._conflict(action.get((i, b)),
                                                  LR.Reduce(p),
                                                  lookahead=b)

                # if [S' -> S . ; $] is in I_i,
                # then set action[i, $] to 'accept'

                if (n == len(p.rhs) and
                        p == starting_production and
                        b == Lexer.EOF):

                    action[i, b] = self._conflict(action.get((i, b)),
                                                  LR.Accept())

                # the initial state of the parser is the one constructed from
                # the set containing [S' -> . S; $]

                if n == 0 and p == starting_production and b == Lexer.EOF:
                    if s0 is not None:
                        raise GrammarError(
                            "Multiple start states found, {s0} and {i}"
                            .format(s0=s0, i=i))
                    s0 = i

            for nt in self.nonterminals:
                g = self._goto(items, nt)
                if g in index:
                    goto[i, nt] = index[g]

        if s0 is None:
            raise GrammarError("No start state found")

        self._action_table = action
        self._goto_table = goto
        self._s0 = s0

    def _clear_caches(self):
        super(LR1, self)._clear_caches()
        self._shift_reduce_conflicts = set()
        self._reduce_reduce_conflicts = set()

    def _conflict(self, current, new, lookahead=None):
        if current is None:
            return new

        if current == new:
            return current

        if isinstance(current, LR.Accept) or isinstance(new, LR.Accept):
            raise GrammarError("accept conflict found",
                               existing_action=current,
                               new_action=new,
                               )

        if isinstance(current, LR.Shift) and isinstance(new, LR.Shift):
            raise GrammarError("shift/shift conflict found",
                               existing_action=current,
                               new_action=new,
                               )

        if isinstance(current, LR.Shift) and isinstance(new, LR.Reduce):
            return self._conflict_shift_reduce(current, new, lookahead)

        if isinstance(current, LR.Reduce) and isinstance(new, LR.Shift):
            return self._conflict_shift_reduce(new, current, lookahead)

        if isinstance(current, LR.Reduce) and isinstance(new, LR.Reduce):
            return self._conflict_reduce_reduce(current, new)

        if isinstance(current, LR.Error):
            a = current.kwargs['a']
            b = current.kwargs['b']
            LOG.debug("extracting former actions from error:", a, b,
                      "new action is", new)
            if new == a or new == b:
                LOG.debug("... keeping error")
                return current
            result1 = self._conflict(a, new, lookahead)
            result2 = self._conflict(b, new, lookahead)
            LOG.debug("... bailing with new results:", result1, result2)

        raise GrammarError("unhandled conflict found:",
                           current=current,
                           new=new,
                           lookahead=lookahead)

    def _conflict_shift_reduce(self, shift, reduce, lookahead):
        try:
            level, assoc = self._terminal_precedence(lookahead)
            l2, a2 = self._rule_precedence(reduce.rule)
        except GrammarError:
            # Use a default rule.
            LOG.info("Defaulting to shift for s/r:", shift, reduce, lookahead)
            self._shift_reduce_conflicts.add((shift, reduce, lookahead))
            return shift

        if level > l2:
            return shift
        elif level < l2:
            return reduce
        else:
            if assoc is Grammar.Left:
                return reduce
            elif assoc is Grammar.Right:
                return shift
            else:
                return LR.Error("{} is non-associative".format(lookahead),
                                a=shift, b=reduce)

    def _conflict_reduce_reduce(self, r1, r2):
        if r1.rule.gen < r2.rule.gen:
            LOG.info("Preferring older rule for r/r:", r1, r2)
            self._shift_reduce_conflicts.add((r1, r2))
            return r1
        elif r1.rule.gen > r2.rule.gen:
            LOG.info("Preferring older rule for r/r:", r2, r1)
            self._shift_reduce_conflicts.add((r2, r1))
            return r2

        raise GrammarError("reduce/reduce conflict found", r1=r1, r2=r2)
