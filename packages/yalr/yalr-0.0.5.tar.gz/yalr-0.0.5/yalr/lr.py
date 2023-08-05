import logging

from .grammar import Grammar, GrammarError
from .operations import GrammarOperations
from .lexer import Lexer

LOG = logging.getLogger(__name__)


class LR(GrammarOperations, Grammar):

    def term(self, term):
        if term in self._terminals:
            return term
        elif type(term) in self._terminals:
            return type(term)
        elif term == Lexer.EOF:
            return term
        raise GrammarError("Terminal {t} not in terminals"
                           .format(t=term))

    def action(self, state, term):
        return self._action_table.get((state, self.term(term)), LR.Error())

    def goto(self, state, nt):
        return self._goto_table.get((state, nt), LR.Error())

    def parse(self, stream):
        # The stack consists of (data, state) pairs
        stack = [(None, self._s0)]
        for a in stream:
            LOG.debug("read", a)
            while True:
                LOG.debug("stack =", stack)
                action = self.action(stack[-1][1], a)
                if isinstance(action, LR.Shift):
                    LOG.debug("  shift", a, "=>", action.state)
                    stack.append((a, action.state))
                    break
                if isinstance(action, LR.Reduce):
                    LOG.debug("  reduce", action.rule, "=>")
                    # We do it this way because lambda productions
                    # have a length of 0, and stack[:-0] doesn't do
                    # the right thing.
                    split = len(stack) - len(action.rule.rhs)
                    value = action.rule.fn(*[v for (v, s) in stack[split:]])
                    stack = stack[:split]
                    state = self.goto(stack[-1][1], action.nt)
                    LOG.debug("  => reduce:", state, "=", value)
                    stack.append((value, state))
                    continue
                if isinstance(action, LR.Accept):
                    LOG.debug("accept, stack =", stack)
                    return stack[-1][0]
                if isinstance(action, LR.Error):
                    raise GrammarError(action.message,
                                       stack=stack,
                                       token=a,
                                       **action.kwargs)

    class Shift(object):
        def __init__(self, state):
            self.state = state

        def __repr__(self):
            return "LR.Shift({s})".format(s=self.state)

        def __eq__(self, other):
            return isinstance(other, LR.Shift) and other.state == self.state

        def __ne__(self, other):
            return not(self == other)

        def __hash__(self):
            return hash(self.state)

    class Reduce(object):
        def __init__(self, rule):
            self.rule = rule

        def __repr__(self):
            return "LR.Reduce({r})".format(r=self.rule)

        def __eq__(self, other):
            return isinstance(other, LR.Reduce) and other.rule == self.rule

        def __ne__(self, other):
            return not(self == other)

        def __hash__(self):
            return hash(self.rule)

        @property
        def nt(self):
            return self.rule.nt

    class Accept(object):
        def __repr__(self):
            return "LR.Accept"

        def __eq__(self, other):
            return isinstance(other, LR.Accept)

        def __ne__(self, other):
            return not(self == other)

        def __hash__(self):
            return hash(LR.Accept)

    class Error(object):
        def __init__(self, message='', **kwargs):
            self.message = message
            self.kwargs = kwargs

        def __repr__(self):
            s = "LR.Error({})".format(self.message)
            if self.kwargs:
                s += (' {' +
                      ', '.join(k + ': ' + str(self.kwargs[k])
                                for k in sorted(self.kwargs)) +
                      '}')
            return s

        __str__ = __repr__
