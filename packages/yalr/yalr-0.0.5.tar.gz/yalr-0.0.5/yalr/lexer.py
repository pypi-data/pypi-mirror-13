import re


class Lexer(object):

    ActualNone = object()
    EOF = object()

    def __init__(self):
        self.rules = []

    def __call__(self, pattern, flags=re.MULTILINE | re.VERBOSE):
        pattern = re.compile(pattern, flags)

        def decorate(f):
            self.rules.append((pattern, f))
            return f
        return decorate

    def lex(self, input):
        """ Take a string and lex it """
        while input != "":
            for p, f in self.rules:
                result = p.match(input)
                if result:
                    break
            else:
                raise LexerError(input)

            input = input[result.end():]
            if len(p.groupindex) == 0:
                token = f(*result.groups())
            else:
                token = f(**result.groupdict())
            if token is not None:
                yield token if token is not Lexer.ActualNone else None
        yield Lexer.EOF


class LexerError(Exception):
    pass
