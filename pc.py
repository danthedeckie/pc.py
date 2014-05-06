class NotHere(Exception):
    ''' attempted to parse what you asked for, but there ain't one here.
        this is the primary mechanism for returning after a 'forward parse'
        attempt.'''
    pass

class TooGeneric(Exception):
    ''' when a method needs to be implemented for consistency, but really
        should never occur, as a more specific parser should be used... '''

class Parsable(object):

    def __or__(self, other):
        ''' combine two parsers '''
        return Either(self, other)

    def read(self, text, position=0):
        ''' read instance from text, starting at position.
            return either the length that we parsed, or raise a 'NotHere'
            exception if it's not possible to parse one of these here. '''
        raise TooGeneric('Parsable!')

    def output(self, data, clean=False):
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
        self.options = options

    def read(self, text, position=0):
        for option in self.options:
            try:
                return option.read(text, position)
            except NotHere:
                continue

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
        if text[position] == self.letter:
            return 1, self.data
        else:
            raise NotHere('Expected "%s", got "%s"' %
                            (self.letter, text[position]))

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
        self.original = original
        self.allow_none = True

    def read(self, text, position=0):
        data = {'class': self, 'parts': []}
        i = 0
        while True:
            try:
                part_length, part_data = self.original.read(text, position + i)
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
    def __init__(self, ending, escape=False):
        self.ending = ending
        self.escape = escape
        self.ending_length = len(ending)

    def read(self, text, position=0):
        data = {'class': self}
        i = 0
        while True:
            if text[position + i:self.ending_length] == self.ending \
            and text[position + i - 1] != self.escape:
                data['text'] = text[position:position + i + self.ending_length]
                return i + self.ending_length, data

#class Spaced(*vargs):
#    ''' join mulitple parsers together, with optional spaces... '''
#    

#######################################################
# Aliases, and other useful bits:

def Optional(*vargs):
    return Either(*list(vargs) + [Nothing()])

LETTERS='abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
NUMBERS='1234567890'
SPACES=' \t'

def output(parsed_block):
    length, parsed = parsed_block

    return parsed['class'].output(parsed)
