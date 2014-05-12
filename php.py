'''
    php.py - Copyright (C) 2014 Daniel Fairhead
    ----------------------------------------------------------------------
    This is the (WIP) grammar for a PHP parser/cleaner, written using pc.py,
    to prove (as much as anything) that the model works as a way of writing
    this library.

    Ultimately, I hope it can become a "phpfmt"/uncrustify type of program.
    ----------------------------------------------------------------------
    GPL3 Licenced.

    pc.py is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    py.py is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with pc.py.  If not, see <http://www.gnu.org/licenses/>.

'''

from pc import *


# TODO: function blocks, classes.
# TODO: switch, continue & break
# TODO: ternary operators
# TODO: Once this all works, just as a general parser, then make custom class
#       versions of all the parts we need, with passing of data (such as
#       expected indent) through, and 'output' versions which actually do
#       pretty printing, etc.

################################################################################
#
# Simple Literals, variables, etc:
#

VAR = Joined('$', Word(LETTERS + '_'))

WORD = Word(LETTERS + '_')

CONST = WORD # TODO: really????????

STRING = Joined('"', Until('"', escape='\\')) \
       | Joined("'", Until("'", escape='\\'))

NUMBER = Joined(Optional(SingleChar('-')),
                Word(NUMBERS),
                Optional(Joined('.', Word(NUMBERS))))

OPERATOR = Either('===', '!==', '!=', '==',
                  '+=', '-=', '/=', '.=',
                  '+', '-', '/', '=', '.',
                  '>', '<', '<<', '>>')

COMMENT_INLINE = Joined("/*", Until("*/", fail_on_eof=True))
COMMENT_LINE = Joined("//", Until("\n"))

COMMENT = COMMENT_INLINE \
        | COMMENT_LINE

WHITESPACE = Word(' \t\n')

SEMICOLON = SingleChar(';')

COMMENTS_OR_WHITESPACE = Multiple(Either(WHITESPACE, COMMENT))

################################################################################
#
# Two 'helpers' which let us join things together with COMMENTS_OR_WHITESPACE
# optionally between every single item.
#

def phpitem(actual):
    ''' most php 'things' can be separated by (x) random amount of whitespace,
        or comments.  that's just the way it is... '''
    return Joined(COMMENTS_OR_WHITESPACE, actual, COMMENTS_OR_WHITESPACE)

class PHPJoin(Joined):
    ''' wrap a list of otherwise sensible parsers in PHPItem(s). '''
    def __init__(self, *parts):
        self.parts = [phpitem(part) for part in parts]

def phpmulti(parsable, separator):
    ''' takes a parsable thing, and returns a version of it that can accept
        multiple instances, separated by separator. So phpMulti("x",",")
        would accept x or x,x or x,x,x,x,x,x,x '''
    return PHPJoin(parsable, Multiple(PHPJoin(separator, parsable)))

################################################################################
#
# "Things" - Any kind of PHP item, usually joined with random amounts of
#            whitespace, with optional comments, etc.
#

THING = Either(CONST, STRING, NUMBER)

BRACKETED_VAR = Joined(VAR, Optional(Joined('[', THING, ']')))
# $x->y, $x->$y->$z...
COMPLEX_VAR = Joined(BRACKETED_VAR, Multiple(Joined('->', BRACKETED_VAR | WORD)))

INPLACE_CHANGE = Either(PHPJoin(Either('--', '++'), COMPLEX_VAR),
                        PHPJoin(COMPLEX_VAR, Either('--', '++')))

# Hm.  This is annoying.  Recursive definitions are not easy with this schema:

FUNC_APP = PHPJoin(WORD,
                   '(',
                   Either(phpmulti(THING, ','), Nothing()),
                   ')')

EXPR = PHPJoin('(', THING, ')')

# infix operations slightly different - they can't contain themselves, or else
# it becomes too recursive...

INFIXED = PHPJoin(Either(FUNC_APP, INPLACE_CHANGE, COMPLEX_VAR, EXPR, CONST,
                         STRING, NUMBER),
                  OPERATOR, THING)

# And add those into "THING" - before the 'simpler' options, as foo() needs to
# be attempted before foo with no brackets, $a++ before $a, etc.

THING.options = [FUNC_APP, INFIXED, EXPR, INPLACE_CHANGE, COMPLEX_VAR] \
              + THING.options

################################################################################
#
# And now to actual 'complete' lines/parses:
#

STATEMENT_KEYWORDS = Either('echo', 'print', 'return')
KEYWORD_STATEMENT = PHPJoin(STATEMENT_KEYWORDS, THING)

ASSIGNMENT = PHPJoin(COMPLEX_VAR, OPERATOR, THING)

# Again with the freaking recursive definitions!
PHP_LINE = PHPJoin(Either(KEYWORD_STATEMENT, ASSIGNMENT, INPLACE_CHANGE),
                SEMICOLON)

STATEMENT = Either(PHP_LINE)

BLOCK = PHPJoin('{', Multiple(STATEMENT), '}')

IF = PHPJoin('if',
             EXPR,
             BLOCK | STATEMENT,
             Multiple(Joined(
                 Either('else if', 'elseif'), EXPR, BLOCK | STATEMENT)),
             Multiple(Joined('else', BLOCK | STATEMENT)))

FOR_CONDITIONS = PHPJoin(phpmulti(ASSIGNMENT, ','), SEMICOLON,
                         phpmulti(INFIXED, ','), SEMICOLON,
                         phpmulti(THING, ','))

FOREACH_CONDITIONS = PHPJoin(COMPLEX_VAR, 'as', Either(PHPJoin(VAR, '=>', VAR),
                                                               VAR))

FOR = PHPJoin('for', '(', FOR_CONDITIONS, ')', BLOCK | STATEMENT)
FOREACH = PHPJoin('foreach', '(', FOREACH_CONDITIONS, ')', BLOCK | STATEMENT)
WHILE = PHPJoin('while', '(', THING, ')', BLOCK | STATEMENT)

STATEMENT.options += (IF, FOR, FOREACH, WHILE, Nothing())
STATEMENT_ = Joined(STATEMENT, COMMENTS_OR_WHITESPACE)

################################################################################
#
# And Parse PHP files, from <?php ... to the end.

PHP_BLOCK = Joined('<?php', Multiple(STATEMENT_), '?>')
# TODO: files which end w/o closing ?>
