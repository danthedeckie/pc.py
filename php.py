from pc import *

# Simple 'parts'. String literals, variables, etc.

VAR = Joined('$', Word(LETTERS + '_'))

WORD = Word(LETTERS + '_')

# $x->y, $x->$y->$z...
COMPLEX_VAR = Joined(VAR, Multiple(Joined('->', VAR | WORD)))

CONST = WORD # TODO: really????????

STRING = Joined('"', Until('"', escape='\\')) \
       | Joined("'", Until("'", escape='\\'))

NUMBER = Joined(Word(NUMBERS), Optional('.', Word(NUMBERS)))

OPERATOR = Either('+', '-', '/', '=', '.')

COMMENT_INLINE = Joined("/*", Until("*/", fail_on_eof=True))
COMMENT_LINE = Joined("//", Until("\n"))

COMMENT = COMMENT_INLINE \
        | COMMENT_LINE

WHITESPACE = Word(' \t\n')

SEMICOLON = SingleChar(';')

COMMENTS_OR_WHITESPACE = Multiple(Either(WHITESPACE, COMMENT))

def phpitem(actual):
    ''' most php 'things' can be separated by (x) random amount of whitespace,
        or comments.  that's just the way it is... '''
    return Joined(COMMENTS_OR_WHITESPACE, actual, COMMENTS_OR_WHITESPACE)


class PHPJoin(Joined):
    ''' wrap a list of otherwise sensible parsers in PHPItem(s). '''
    def __init__(self, *parts):
        self.parts = [phpitem(part) for part in parts]


THING = Either(COMPLEX_VAR, CONST, STRING, NUMBER)

# Hm.  This is annoying.  Recursive definitions are not easy with this schema:

FUNC_APP = PHPJoin(WORD,
                   '(',
                   Either(Multiple(PHPJoin(THING, ','), allow_none=False),
                          THING,
                          Nothing()),
                   ')')

INFIXED = PHPJoin(THING, OPERATOR, THING)

EXPR = PHPJoin('(', THING, ')')


# And add those into "THING" - before the 'simpler' options, as foo() needs to
# be attempted before foo with no brackets, $a++ before $a, etc.

THING.options = [FUNC_APP, INFIXED, EXPR] + THING.options

################################################################################
#
# And now to actual 'complete' lines/parses:
#

STATEMENT_KEYWORDS = Either('echo', 'print')
STATEMENT = Joined(PHPJoin(STATEMENT_KEYWORDS, THING), SEMICOLON)

ASSIGNMENT = Joined(PHPJoin(THING, OPERATOR, THING), SEMICOLON)

# Again with the freaking recursive definitions!
PHP_LINE = Either(STATEMENT, ASSIGNMENT, Nothing())

BLOCK = PHPJoin('{', Multiple(PHP_LINE), '}')

IF = PHPJoin('if',
             EXPR,
             BLOCK | STATEMENT,
             Multiple(Joined(
                 Either('else if', 'elseif'), EXPR, BLOCK | STATEMENT)),
             Multiple(Joined('else', BLOCK | STATEMENT)))

PHP_LINE.options += (IF,)

PHP_BLOCK = Joined('<?php', Multiple(PHP_LINE), '?>')
