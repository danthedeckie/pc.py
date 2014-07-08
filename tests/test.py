'''
    basic unit tests for pc.py parser-combinator library.
    ------
    Copyright (C) 2014 Daniel Fairhead
    GPL3 Licence.

'''
# pylint: disable=too-many-public-methods, missing-docstring, invalid-name
# pylint: disable=no-self-use, wildcard-import

from unittest import TestCase
from cStringIO import StringIO
import sys

from pc import *
from php import PHP_BLOCK

class PCTestCase(TestCase):
    def assertHasRead(self, parsed, expected_length):
        self.assertEquals(parsed[0], expected_length)

    def assertTexts(self, parsed, expected):
        for a, b in zip(expected, parts(parsed[1])):
            self.assertEquals(a, b)

    def assertOutputs(self, parsed_block, text):
        count, parsed = parsed_block
        self.assertEquals(output(parsed), text)

    def assertReadsFully(self, parser, text):
        p = parser.parse(text)
        self.assertOutputs(p, text)
        self.assertHasRead(p, len(text))

class TestNothing(PCTestCase):
    def testNothing(self):
        text = ''
        N = Nothing()

        n = N.parse(text)

        self.assertHasRead(n, 0)
        self.assertOutputs(n, '')

class TestSingleA(PCTestCase):

    def testSingleChar(self):
        text = 'a'

        A = SingleChar('a')
        A_ = Either(SingleChar('a'), Nothing())

        self.assertHasRead(A.parse(text), 1)
        self.assertOutputs(A.parse(text), text)

        with self.assertRaises(NotHere):
            A.parse(' ')

        a = A_.parse(' ')

        self.assertHasRead(a, 0)

    def testMultipleSingleChar(self):

        text = 'a'

        A = Multiple(SingleChar('a'))
        A_ = Multiple(Either(SingleChar('a'), Nothing()))

        a = A.parse(text+text)
        self.assertHasRead(a, 2)

        a = A.parse(text * 4)
        self.assertHasRead(a, 4)

    def testAthenB(self):

        text = 'ab'

        A = Multiple(SingleChar('a'))
        A_ = Multiple(Either(SingleChar('a'), Nothing()))

        B = Multiple(SingleChar('b'))
        B_ = Multiple(Either(SingleChar('b'), Nothing()))

        ab = Joined(A, B).parse(text)

        self.assertHasRead(ab, 2)
        self.assertOutputs(ab, text)

        ab = Joined(A_, B).parse(text)

        self.assertHasRead(ab, 2)
        self.assertOutputs(ab, text)

        ab = Joined(A_, B_).parse(text)

        self.assertHasRead(ab, 2)
        self.assertOutputs(ab, text)

        text = 'abc'

        ab = Joined(A, B).parse(text)

        self.assertHasRead(ab, 2)
        self.assertOutputs(ab, 'ab')

        ab = Joined(A_, B).parse(text)

        self.assertHasRead(ab, 2)
        self.assertOutputs(ab, 'ab')

        ab = Joined(A_, B_).parse(text)

        self.assertHasRead(ab, 2)
        self.assertOutputs(ab, 'ab')


class TestSpecificWord(PCTestCase):
    def testSingle(self):

        # when 1 is there:

        text = 'tomato'

        T = SpecificWord('tomato')

        t = T.parse(text)

        self.assertHasRead(t, 6)
        self.assertOutputs(t, text)

        # when 0 are there:
        with self.assertRaises(NotHere):
            t = T.parse('')


    def testMultipleSpecificWords(self):

        #mulitple, but only 1 to read:
        text = 'tomato'

        T = SpecificWord('tomato')
        Ts = Multiple(T)

        ts = Ts.parse(text)

        self.assertHasRead(ts, 6)
        self.assertOutputs(ts, text)

        # Multiple with 8 to read:

        text = text * 8

        ts = Ts.parse(text)

        self.assertHasRead(ts, 48)
        self.assertOutputs(ts, text)

        # Multiple with junk following:

        ts = Ts.parse('tomatoPuree')

        self.assertHasRead(ts, 6)
        self.assertOutputs(ts, 'tomato')

        # None:

        ts = Ts.parse('')
        self.assertHasRead(ts, 0)
        self.assertOutputs(ts, '')

        # Only Junk:

        ts = Ts.parse('sauce made from tomato')
        self.assertHasRead(ts, 0)
        self.assertOutputs(ts, '')


class TestWord(PCTestCase):
    def testalphas(self):

        # basic
        text = 'abc'
        A = Word('abc')

        a = A.parse(text)

        self.assertHasRead(a, 3)
        self.assertOutputs(a, 'abc')

        # junk following:

        a = A.parse('bcd')

        self.assertHasRead(a, 2)
        self.assertOutputs(a, 'bc')

        # only junk:

        with self.assertRaises(NotHere):
            a = A.parse('xyz')

        # nothing:

        with self.assertRaises(NotHere):
            a = A.parse('')

    def testJoined(self):

        # basic:
        text = '$variable'
        A = Joined('$', Word(LETTERS))

        a = A.parse(text)

        self.assertHasRead(a, 9)
        self.assertOutputs(a, text)

        # junk following:

        text = '$var again'

        a = A.parse(text)

        self.assertHasRead(a, 4)
        self.assertOutputs(a, '$var')


        A_ = Joined(A, Word(' '))

        a = A_.parse(text)

        self.assertHasRead(a, 5)
        self.assertOutputs(a, '$var ')

        A__ = Joined(A_, Word(LETTERS))

        a = A__.parse(text)

        self.assertHasRead(a, 10)
        self.assertOutputs(a, text)


class TestEither(PCTestCase):
    def testTwoSingleLetters(self):

        # Two choices:

        A = SingleChar('a')
        B = SingleChar('b')

        E = Either(A, B)

        # starting with first.

        text = 'abc'

        p = E.parse(text)

        self.assertHasRead(p, 1)
        self.assertOutputs(p, 'a')

        # starting with second choice

        text = 'bcd'

        p = E.parse(text)

        self.assertHasRead(p, 1)
        self.assertOutputs(p, 'b')

        # starting with something else

        text = 'def'

        with self.assertRaises(NotHere):
            p = E.parse(text)

    def testManySingleLetters(self):

        A = SingleChar('a')
        B = SingleChar('b')
        C = SingleChar('c')

        E = Either(A, B, C)

        # starting with first.

        text = 'abc'

        p = E.parse(text)

        self.assertHasRead(p, 1)
        self.assertOutputs(p, 'a')

        # starting with second choice

        text = 'bcd'

        p = E.parse(text)

        self.assertHasRead(p, 1)
        self.assertOutputs(p, 'b')

        # starting with third choice

        text = 'cde'

        p = E.parse(text)

        self.assertHasRead(p, 1)
        self.assertOutputs(p, 'c')

        # starting with something else

        text = 'def'

        with self.assertRaises(NotHere):
            p = E.parse(text)

    def testTwoSingleLettersORsyntax(self):

        # Two choices:

        A = SingleChar('a')
        B = SingleChar('b')

        E = A | B

        # starting with first.

        text = 'abc'

        p = E.parse(text)

        self.assertHasRead(p, 1)
        self.assertOutputs(p, 'a')

        # starting with second choice

        text = 'bcd'

        p = E.parse(text)

        self.assertHasRead(p, 1)
        self.assertOutputs(p, 'b')

        # starting with something else

        text = 'def'

        with self.assertRaises(NotHere):
            p = E.parse(text)

    def testManySingleLettersORsyntax(self):

        A = SingleChar('a')
        B = SingleChar('b')
        C = SingleChar('c')

        E = A | B | C

        # starting with first.

        text = 'abc'

        p = E.parse(text)

        self.assertHasRead(p, 1)
        self.assertOutputs(p, 'a')

        # starting with second choice

        text = 'bcd'

        p = E.parse(text)

        self.assertHasRead(p, 1)
        self.assertOutputs(p, 'b')

        # starting with third choice

        text = 'cde'

        p = E.parse(text)

        self.assertHasRead(p, 1)
        self.assertOutputs(p, 'c')

        # starting with something else

        text = 'def'

        with self.assertRaises(NotHere):
            p = E.parse(text)


    def testWords(self):
        # TODO
        pass

    def testSpecificWords(self):
        # TODO
        pass

    def testJoined(self):
        # TODO
        pass

    def testEitherEither(self):
        E = Either('a', 'b')
        EE = Either(E, ' ')

        with self.assertRaises(NotHere):
            E.parse(' ')

        self.assertReadsFully(EE, ' ')
        self.assertReadsFully(EE, 'a')
        self.assertReadsFully(EE, 'b')

    def testRecursiveEither(self):
        E = Either('a', 'b')
        EE = Either(E, ' ')
        EE.options += (EE, )

        # all normal reading is OK:

        self.assertReadsFully(EE, ' ')
        self.assertReadsFully(EE, 'a')
        self.assertReadsFully(EE, 'b')

        # But reading an unknown char fails:

        with self.assertRaises(NotHere):
            EE.parse('c')

        # add a new option AFTER the recursive EE

        EE.options += (SingleChar('c'), )

        self.assertReadsFully(EE, 'c')



    def testWithNothing(self):
        # TODO: add test for Nothing not at end of Either list!

        E = Either(SpecificWord('chocolate'), Nothing())

        text = 'chocolate!'

        e = E.parse(text)

        self.assertHasRead(e, 9)
        self.assertOutputs(e, 'chocolate')

        text = 'other sweets'

        e = E.parse(text)

        self.assertHasRead(e, 0)
        self.assertOutputs(e, '')

    def testEitherMultipleAfter(self):
        M = Multiple(Either('a','b','c'))
        E = Either('1','2', M, '3')

        self.assertReadsFully(E, '1')
        self.assertReadsFully(E, '2')
        self.assertReadsFully(E, 'a')
        self.assertReadsFully(E, 'b')
        self.assertReadsFully(E, 'abc')
        self.assertReadsFully(E, '')  # mulitple matches '' on failure...
        self.assertReadsFully(E, '3')


class TestUntil(PCTestCase):
    def testSingleLetter(self):
        P = Until(' ')

        # ends with ending:

        text = 'thing '
        p = P.parse(text)
        self.assertHasRead(p, 6)
        self.assertOutputs(p, 'thing ')

        # continues afterwards:

        text = 'thing another'
        p = P.parse(text)
        self.assertHasRead(p, 6)
        self.assertOutputs(p, 'thing ')

        # no ending:

        text = 'thisisalongtext'
        p = P.parse(text)
        self.assertHasRead(p, 15)
        self.assertOutputs(p, text)

        # no ending, please fail:

        with self.assertRaises(NotHere):
            p = Until(' ', fail_on_eof=True).parse(text)


    def testWordEnding(self):
        text = "START do stuff. END"

        # text ends with ending.

        P = Until('END')
        p = P.parse(text)
        self.assertHasRead(p, 19)
        self.assertOutputs(p, text)

        # text continues past ending

        text1 = "START do stuff. END and some extra crap. END AGAIN"
        p = P.parse(text1)
        self.assertHasRead(p, 19)
        self.assertOutputs(p, text)

        # text doesn't have ending

        text2 = "START do stuff. "
        p = P.parse(text2)
        self.assertHasRead(p, 16)
        self.assertOutputs(p, text2)

        # no ending, please fail:

        with self.assertRaises(NotHere):
            p = Until('END', fail_on_eof=True).parse(text2)

    def testSingleLetterWithEscape(self):
        P = Until('"', escape='\\')

        # ends with ending:

        self.assertReadsFully(P, 'thing\\" end"')

        # continues afterwards:

        text = 'thing" another'
        p = P.parse(text)
        self.assertHasRead(p, 6)
        self.assertOutputs(p, 'thing"')

        # no ending:

        text = 'thisisalongtext'
        p = P.parse(text)
        self.assertHasRead(p, 15)
        self.assertOutputs(p, text)

        # no ending, please fail:

        with self.assertRaises(NotHere):
            p = Until(' ', fail_on_eof=True).parse(text)

class TestMultiple(PCTestCase):
    def testMultiLetters(self):
        P = Multiple(SingleChar('a'))

        self.assertReadsFully(P, '')
        self.assertReadsFully(P, 'a')
        self.assertReadsFully(P, 'aaaaaaaaaa')

        P = Multiple(Either('a', 'b', 'c'))

        self.assertReadsFully(P, '')
        self.assertReadsFully(P, 'a')
        self.assertReadsFully(P, 'b')
        self.assertReadsFully(P, 'c')
        self.assertReadsFully(P, 'abc')
        self.assertReadsFully(P, 'abcbbaaaaccabaccabbaaaa')

    def testMultiEithers(self):
        E = Either(SpecificWord('the'), SpecificWord('cat'))
        S = Multiple(Either(Word(SPACES), E))

        text = 'the cat sat on the mat'

        s = S.parse(text)

        self.assertHasRead(s, 8)
        self.assertOutputs(s, 'the cat ')

        text = 'the the the cat, yo. remix!'

        s = S.parse(text)

        self.assertHasRead(s, 15)
        self.assertOutputs(s, 'the the the cat')

    def testMultiNothings(self):

        # 3 options, first succeeds:

        E = Either(SpecificWord('chocolate'), ' ', Nothing())

        text = 'chocolate!'

        e = E.parse(text)

        self.assertHasRead(e, 9)
        self.assertOutputs(e, 'chocolate')

        # same options, but multiple.  First succeeds:

        M = Multiple(E)

        m = E.parse(text)

        self.assertHasRead(m, 9)
        self.assertOutputs(m, 'chocolate')

        # new options, option with Nothing PRECEDING matching option

        ME = Multiple(Either(Either('?', Nothing()), E))

        me = ME.parse(text)

        self.assertHasRead(me, 9)
        self.assertOutputs(me, 'chocolate')

    def testWithoutAllowedNone(self):
        text = 'this is some text'

        P = Multiple(Either('a', 'b', 'c'))

        count, p = P.parse(text)

        self.assertEquals(output(p), '')

        PF = Multiple(Either('a', 'b', 'c'), allow_none=False)

        with self.assertRaises(NotHere):
            pf = PF.parse(text)

    def testRecursiveMultiple(self):
        E = Either('a', 'b')
        M = Multiple(E)
        E.options += (M, )

        self.assertReadsFully(M, '')
        self.assertReadsFully(M, 'a')
        self.assertReadsFully(M, 'abaabbabaab')

        # and now with options AFTER the Mulitple (test continues after attempt)

        E.options += (SingleChar('c'), )

        self.assertReadsFully(M, '')
        self.assertReadsFully(M, 'a')
        self.assertReadsFully(M, 'c')
        self.assertReadsFully(M, 'abcaacbbabcccccaab')



class TestReprs(TestCase):
    ''' these tests are internal to the library, and shouldn't be relied
        upon to not change between versions. '''

    def testParsableRepr(self):
        P = Parsable()
        self.assertEquals(repr(P), '<Parsable>')

    def testJoinedRepr(self):
        J = Joined()
        self.assertEquals(repr(J), '<Joined:()>')

        J = Joined(Nothing())
        self.assertEquals(repr(J), '<Joined:(Nothing)>')

        J = Joined(SpecificWord('test'))
        self.assertEquals(repr(J), '<Joined:("test")>')

        J = Joined(SingleChar('t'))
        self.assertEquals(repr(J), "<Joined:('t')>")

        J = Joined(SingleChar('t'), SpecificWord('est'))
        self.assertEquals(repr(J), '<Joined:(\'t\'+"est")>')

        J = Joined(SingleChar('t'), SpecificWord('est'), Nothing())
        self.assertEquals(repr(J), '<Joined:(\'t\'+"est"+Nothing)>')

    def testEitherRepr(self):
        J = Either()
        self.assertEquals(repr(J), '<Either:()>')

        J = Either(Nothing())
        self.assertEquals(repr(J), '<Either:(Nothing)>')

        J = Either(SpecificWord('test'))
        self.assertEquals(repr(J), '<Either:("test")>')

        J = Either(SingleChar('t'))
        self.assertEquals(repr(J), "<Either:('t')>")

        J = Either(SingleChar('t'), SpecificWord('est'))
        self.assertEquals(repr(J), '<Either:(\'t\'|"est")>')

        J = Either(SingleChar('t'), SpecificWord('est'), Nothing())
        self.assertEquals(repr(J), '<Either:(\'t\'|"est"|Nothing)>')

    def testMultipleRepr(self):
        M = Multiple(Nothing())
        self.assertEquals(repr(M), "<Multiple:(<Nothing>)>")

        MM = Multiple(M)
        self.assertEquals(repr(MM), "<Multiple:(<Multiple:(<Nothing>)>)>")

        E = Either('yes', 'no', 'maybe')

        ME = Multiple(E)
        self.assertEquals(repr(ME),
                          '<Multiple:(<Either:("yes"|"no"|"maybe")>)>')

        # and recursive!
        E.options += (ME,)
        self.assertEquals(repr(ME),
                          '<Multiple:(<Either:("yes"|"no"|"maybe"|Multiple)>)>')



class TestShouldNotBeReachable(TestCase):
    ''' these tests should never actually be reachable in normal code.
        all they do is raise exceptions when someone implements something
        badly.  Of course these aren't included to improve coverage score...'''

    def testParsableRead(self):
        P = Parsable()
        with self.assertRaises(TooGeneric):
            P.parse('text')

    def testParsableOutput(self):
        P = Parsable()
        self.assertEquals(P.output({'class': P, 'text': 'stuff' }), 'stuff')

        with self.assertRaises(TooGeneric):
            P.output({'class': P })

    def testEitherOutput(self):
        E = Either()
        with self.assertRaises(TooGeneric):
            E.output({'class': E, 'text': 'anything'})


class TestPrettyPrint(TestCase):
    def testBasic(self):
        Ws = Either(SingleChar('a'), SpecificWord('cat'),
                    SpecificWord('said'), Word(LETTERS))

        S = Multiple(Joined(Ws, Optional(Word(' '))))

        s = S.parse('the cat said  hello')

        stdout = sys.stdout
        sys.stdout = StringIO()

        pretty_print(s)

        text = sys.stdout.getvalue()
        sys.stdout = stdout

        expected = '''19 chars parsed.
the cat said  hello
Multiple:
  Joined:
    Word:"the"
    Word:" "
  Joined:
    SpecificWord:"cat"
    Word:" "
  Joined:
    SpecificWord:"said"
    Word:"  "
  Joined:
    Word:"hello"
    Nothing:""
'''

        self.assertEquals(text, expected)

class testNamedJoin(PCTestCase):
    def testBasic(self):
        A = SpecificWord('A')
        B = SpecificWord('B')

        AB = NamedJoin(('a', A),
                       ('b', B))

        length, data = AB.parse('AB')

        assert length == 2

        assert 'a' in data['parts']
        assert 'b' in data['parts']

        self.assertEquals(data['parts']['a']['text'], 'A')
        self.assertEquals(data['parts']['b']['text'], 'B')

    def testSimpleEnglishSentences(self):
        WS = Word(SPACES)
        WORD = Word(LETTERS)

        ARTICLES = Either(SpecificWord('the'), SpecificWord('a'), SpecificWord('an'))

        VERBS = Either(SpecificWord('have'), SpecificWord('go to'), SpecificWord('eat'))

        SENTENCE = NamedJoin(
            ('subject', Joined(Optional(Joined(ARTICLES, WS)), WORD)),
            ('sub_sp', WS),
            ('verb', VERBS),
            ('verb_sp', WS),
            ('object', Joined(Optional(Joined(ARTICLES, WS)), WORD)),
            ('punctuation', Word('.?!'))
            )

        length, munchies = SENTENCE.parse('the cats have  dinner.')

        assert(length == 22)
        assert(output(munchies['parts']['subject']) == 'the cats')
        assert(output(munchies['parts']['verb']) == 'have')
        assert(output(munchies['parts']['object']) == 'dinner')


class testParts(PCTestCase):
    def testBasic(self):

        CAT = SpecificWord('cat')
        SAID = SpecificWord('said')
        OTHERS = Word(LETTERS)
        SPACES = Word(' ')

        WORDS = Either(CAT, SAID, OTHERS)

        WORDSPACE = Joined(WORDS, Optional(SPACES))

        S = Multiple(WORDSPACE)

        s = S.parse('the cat said  hello')

        self.assertEquals(s[0], 19)
        expected = ['the', ' ', 'cat', ' ', 'said', '  ', 'hello']

        self.assertEquals([a for a in parts(s[1])], expected)

        self.assertTexts(s, expected)
