from pc import *

# Simple 'parts'. String literals, variables, etc.

VAR = Joined('$', Word(LETTERS + '_'))

WORD = Word(LETTERS + '_')

CONST = WORD # TODO: really????????

STRING = Joined('"', Until('"', escape='\\')) \
       | Joined("'", Until("'", escape='\\'))

NUMBER = Joined(Optional(SingleChar('-')), Word(NUMBERS), Optional(Joined('.', Word(NUMBERS))))

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

THING = Either(CONST, STRING, NUMBER)

BRACKETED_VAR = Joined(VAR, Optional(Joined('[' ,THING ,']')))
# $x->y, $x->$y->$z...
COMPLEX_VAR = Joined(BRACKETED_VAR, Multiple(Joined('->', BRACKETED_VAR | WORD)))


# Hm.  This is annoying.  Recursive definitions are not easy with this schema:

FUNC_APP = PHPJoin(WORD,
                   '(',
                   Either(PHPJoin(THING, Multiple(PHPJoin(',', THING))), Nothing()),
                   ')')

EXPR = PHPJoin('(', THING, ')')

# infix operations slightly different - they can't contain themselves, or else
# it becomes too recursive...

INFIXED = PHPJoin(Either(FUNC_APP, COMPLEX_VAR, EXPR, CONST, STRING, NUMBER), OPERATOR, THING)



# And add those into "THING" - before the 'simpler' options, as foo() needs to
# be attempted before foo with no brackets, $a++ before $a, etc.

THING.options = [FUNC_APP, INFIXED, EXPR, COMPLEX_VAR] + THING.options

################################################################################
#
# And now to actual 'complete' lines/parses:
#

STATEMENT_KEYWORDS = Either('echo', 'print')
STATEMENT = Joined(PHPJoin(STATEMENT_KEYWORDS, THING), SEMICOLON)

ASSIGNMENT = Joined(PHPJoin(COMPLEX_VAR, OPERATOR, THING), SEMICOLON)

# Again with the freaking recursive definitions!
PHP_LINE = Either(STATEMENT, ASSIGNMENT, Nothing())

BLOCK = PHPJoin('{', Multiple(PHP_LINE), '}')

IF = PHPJoin('if',
             EXPR,
             BLOCK | STATEMENT,
             Multiple(Joined(
                 Either('else if', 'elseif'), EXPR, BLOCK | STATEMENT)),
             Multiple(Joined('else', BLOCK | STATEMENT)))

# TODO: for, while, etc. function blocks, classes.

PHP_LINE.options += (IF,)
PHP_LINE = Joined(PHP_LINE, COMMENTS_OR_WHITESPACE)

PHP_BLOCK = Joined('<?php', Multiple(PHP_LINE), '?>')

# TODO: Once this all works, just as a general parser, then make custom class
#       versions of all the parts we need, with passing of data (such as
#       expected indent) through, and 'output' versions which actually do
#       pretty printing, etc.
