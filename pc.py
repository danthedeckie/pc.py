'''
    pc.py - Copyright (C) 2014 Daniel Fairhead
    ------------------------------------------
    A simple parser-combinator library, experimental, for fun/learning/etc.
    ------------------------------------------
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
# pylint: disable=no-self-use, star-args

################################################################################
# Exceptions:

from types import GeneratorType

class NotHere(Exception):
    ''' attempted to parse what you asked for, but there ain't one here.
        this is the primary mechanism for returning after a 'forward parse'
        attempt.'''
    pass

class TooGeneric(Exception):
    ''' when a method needs to be implemented for consistency, but really
        should never occur, as a more specific parser should be used... '''

class Parsable(object):
    ''' base class for all parsers '''

    def __or__(self, other):
        ''' combine two parsers '''
        return Either(self, other)

    def __repr__(self):
        ''' for types which can, display themselves as a more useful form '''
        try:
            return '<%s:"%s">' % (self.__class__.__name__, self.data['text'])
        except:
            return '<%s>' % self.__class__.__name__

    def read(self, text, position=0):  #pylint: disable=unused-argument
        ''' read instance from text, starting at position.
            return either the length that we parsed, or raise a 'NotHere'
            exception if it's not possible to parse one of these here. '''
        raise TooGeneric('Parsable!')

    def output(self, data, clean=False):  #pylint: disable=unused-argument
        ''' return the textual version of this parsable.  If 'clean' is false,
            then return it unchanged.  If 'clean' is true, then return it in
            a cleaned up state. '''
        if 'text' in data:
            return data['text']

        raise TooGeneric('class "%s" has no "output" method defined!'
                         % data['class'])


class Either(Parsable):
    ''' Join mulitple parsers, any one of them can match '''
    which = None

    def __init__(self, *options):
        self.options = []
        add_nothing = False

        for option in options:
            if isinstance(option, str):
                if len(option) == 1:
                    self.options.append(SingleChar(option))
                else:
                    self.options.append(SpecificWord(option))
            elif isinstance(option, Either):
                for suboption in option.options:
                    if isinstance(suboption, Nothing):
                        add_nothing = True
                        continue

                    self.options.append(suboption)
            elif isinstance(option, Nothing):
                add_nothing = True
            else:
                self.options.append(option)

        if add_nothing:
            self.options.append(Nothing())

    def __repr__(self):
        return '<%s:(%s)>' % (self.__class__.__name__,
                              '|'.join(repr(i) for i in self.options))

    def read(self, text, position=0):
        for option in self.options:
            try:
                return option.read(text, position)
            except NotHere:
                continue
        raise NotHere

    def output(self, data, clean=False):
        raise TooGeneric('This is inside an Either!  It should have given '
                         'a more specific reply!')

class Nothing(Parsable):
    ''' a 'NULL' parser, which reads nothing, and returns nothing. '''
    def __init__(self):
        self.data = {'class': self, 'text': ''}

    def read(self, text, position=0):
        return 0, self.data

class SingleChar(Parsable):
    ''' a single character parser. '''
    def __init__(self, letter):
        self.letter = letter
        self.data = {'class': self, 'text': letter}

    def read(self, text, position=0):
        try:
            if text[position] == self.letter:
                return 1, self.data
            else:
                raise NotHere('Expected "%s", got "%s"' %
                                (self.letter, text[position]))
        except IndexError:
            raise NotHere('EOF! Expected "%s"' % self.letter)

class SpecificWord(Parsable):
    ''' parse a specific word '''
    def __init__(self, word):
        self.word = word
        self.length = len(word)
        self.data = {'class': self, 'text': word}

    def read(self, text, position=0):
        if text[position:position + self.length] == self.word:
            return self.length, self.data
        else:
            raise NotHere('Expected "%s"' % self.word)


class Word(Parsable):
    ''' a single word, made up of specified characters... '''

    def __init__(self, allowed_chars):
        self.chrs = allowed_chars
        self.length = 0
        self.word = ''

    def read(self, text, position=0):
        data = {'class': self}
        length = 0
        try:
            while text[position + length] in self.chrs:
                length += 1
                continue
        except IndexError:
            if not length:
                raise NotHere('EOF!')
        if not length:
            raise NotHere()

        data['text'] = text[position:position+length]
        return length, data

class Joined(Parsable):
    ''' Join multiple parsers together, without spaces '''
    def __init__(self, *parts):
        self.parts = []
        for p in parts:
            if isinstance(p, str):
                if len(p) == 1:
                    self.parts.append(SingleChar(p))
                else:
                    self.parts.append(SpecificWord(p))
            else:
                self.parts.append(p)

    def __repr__(self):
        return '<%s:(%s)>' % (self.__class__.__name__,
                              '|'.join(i.__class__.__name__ for i in self.parts))


    def read(self, text, position=0):
        data = {'class': self,
                'parts': []}

        total_length = 0
        for part in self.parts:
            length, part_data = part.read(text, position + total_length)
            total_length += length
            data['parts'].append(part_data)

        return total_length, data

    def output(self, data, clean=False):
        return ''.join(p['class'].output(p, clean) for p in data['parts'])

class Multiple(Joined):
    ''' accept multiple of a parsable. '''
    def __init__(self, original, allow_none=True):
        assert allow_none in (True, False)

        self.original = original
        self.allow_none = True

    def __repr__(self):
        try:
            return '<%s:(%s)>' % (self.__class__.__name__,
                                  repr(self.original.__class__.__name__))
        except RuntimeError:
            return self.__class__.__name__


    def read(self, text, position=0):
        data = {'class': self, 'parts': []}
        i = 0
        while True:
            try:
                part_length, part_data = self.original.read(text, position + i)
                # don't allow multiple 'Nothing' parses (as will be infinite)
                if part_data['class'].output(part_data) == '': # nothing!
                    if data['parts'] and data['parts'][-1]['text'] == '':
                        raise NotHere
                data['parts'].append(part_data)
                i += part_length
            except NotHere:
                if not data['parts'] and not self.allow_none:
                    raise
                else:
                    return i, data
            except IndexError:
                if not data['parts'] and not self.allow_none:
                    raise
                else:
                    return i, data

class Until(Parsable):
    ''' accept any text, up until a certain 'end' marker '''

    def __init__(self, ending, escape=False, fail_on_eof=False):
        self.ending = ending
        self.escape = escape
        self.ending_length = len(ending)
        self.fail_on_eof = fail_on_eof

    def read(self, text, position=0):
        data = {'class': self}
        i = -1
        end = len(text) - position
        try:
            while i < end:
                i += 1
                now = position + i
                if text[now:now + self.ending_length] == self.ending \
                and text[now - 1] != self.escape:
                    data['text'] = text[position:now + self.ending_length]
                    return i + self.ending_length, data
            if self.fail_on_eof:
                raise NotHere('EOF')
            else:
                data['text'] = text[position:now + self.ending_length]
                return i, data
        except IndexError:
            return NotHere('EOF')

#class Spaced(*vargs):
#    ''' join mulitple parsers together, with optional spaces... '''
#

#######################################################
# Aliases, and other useful bits:

def Optional(*vargs):  #pylint: disable=invalid-name
    ''' sugar for Either + Nothing '''
    return Either(*list(vargs) + [Nothing()])

LETTERS = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
NUMBERS = '1234567890'
SPACES = ' \t'

def output(parsed_block):
    ''' go through a parsed tree, and output each thing as it thinks it should
        be done.  If the parse was successful, then you should probably end up
        with the same as you put in. '''
    _, parsed = parsed_block

    return parsed['class'].output(parsed)

def pretty_print(parsed_block, level=0):
    ''' take an output from the parser, and display it as a tree for easier
        debugging, etc. '''
    indent = level * ' '
    if type(parsed_block) == tuple:
        count, parsed_block = parsed_block
        print indent + '%i chars parsed.' % count
        print output((count, parsed_block))
        pretty_print(parsed_block)
    else:
        print indent + parsed_block['class'].__class__.__name__ + ':' +  \
            ('"' + parsed_block['text']+ '"' if 'text' in parsed_block else '')
        if 'parts' in parsed_block:
            for p in parsed_block['parts']:
                pretty_print(p, level + 2)

def parts(parsed):
    ''' walk a parsed (dict) tree, yielding each part that has been found
        and actually parsed (ignoring 'nothing's) '''

    assert isinstance(parsed, dict)

    if 'parts' in parsed:
        for p in parsed['parts']:
            o = parts(p)
            if type(o) == GeneratorType:
                for i in o:
                    if i:
                        yield i
            else:
                yield o
    else:
        if not isinstance(parsed.__class__, Nothing):
            if 'text' in parsed:
                yield parsed['text']
