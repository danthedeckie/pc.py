'''
    basic unit tests for pc.py parser-combinator library.
    ------
    Copyright (C) 2014 Daniel Fairhead
    GPL3 Licence.

'''
# pylint: disable=too-many-public-methods, missing-docstring, invalid-name
# pylint: disable=no-self-use, wildcard-import

from unittest import TestCase

from pc import *
from php import PHP_BLOCK

class PCTestCase(TestCase):
    def assertHasRead(self, parsed, expected_length):
        self.assertEquals(parsed[0], expected_length)

    def assertTexts(self, parsed, texts):
        for a, b in zip(parsed[1]['parts'], texts):
            self.assertEquals(a['text'], b)

    def assertOutputs(self, parsed, text):
        self.assertEquals(output(parsed), text)

    def assertReadsFully(self, parser, text):
        p = parser.read(text)
        self.assertOutputs(p, text)
        self.assertHasRead(p, len(text))

class TestNothing(PCTestCase):
    def testNothing(self):
        text = ''
        N = Nothing()

        n = N.read(text)

        self.assertHasRead(n, 0)
        self.assertOutputs(n, '')

class TestSingleA(PCTestCase):

    def testSingleChar(self):
        text = 'a'

        A = SingleChar('a')
        A_ = Either(SingleChar('a'), Nothing())

        self.assertHasRead(A.read(text), 1)
        self.assertOutputs(A.read(text), text)

        with self.assertRaises(NotHere):
            A.read(' ')

        a = A_.read(' ')

        self.assertHasRead(a, 0)

    def testMultipleSingleChar(self):

        text = 'a'

        A = Multiple(SingleChar('a'))
        A_ = Multiple(Either(SingleChar('a'), Nothing()))

        a = A.read(text+text)
        self.assertHasRead(a, 2)

        a = A.read(text * 4)
        self.assertHasRead(a, 4)

    def testAthenB(self):

        text = 'ab'

        A = Multiple(SingleChar('a'))
        A_ = Multiple(Either(SingleChar('a'), Nothing()))

        B = Multiple(SingleChar('b'))
        B_ = Multiple(Either(SingleChar('b'), Nothing()))

        ab = Joined(A, B).read(text)

        self.assertHasRead(ab, 2)
        self.assertOutputs(ab, text)

        ab = Joined(A_, B).read(text)

        self.assertHasRead(ab, 2)
        self.assertOutputs(ab, text)

        ab = Joined(A_, B_).read(text)

        self.assertHasRead(ab, 2)
        self.assertOutputs(ab, text)

        text = 'abc'

        ab = Joined(A, B).read(text)

        self.assertHasRead(ab, 2)
        self.assertOutputs(ab, 'ab')

        ab = Joined(A_, B).read(text)

        self.assertHasRead(ab, 2)
        self.assertOutputs(ab, 'ab')

        ab = Joined(A_, B_).read(text)

        self.assertHasRead(ab, 2)
        self.assertOutputs(ab, 'ab')


class TestSpecificWord(PCTestCase):
    def testSingle(self):

        # when 1 is there:

        text = 'tomato'

        T = SpecificWord('tomato')

        t = T.read(text)

        self.assertHasRead(t, 6)
        self.assertOutputs(t, text)

        # when 0 are there:
        with self.assertRaises(NotHere):
            t = T.read('')


    def testMultipleSpecificWords(self):

        #mulitple, but only 1 to read:
        text = 'tomato'

        T = SpecificWord('tomato')
        Ts = Multiple(T)

        ts = Ts.read(text)

        self.assertHasRead(ts, 6)
        self.assertOutputs(ts, text)

        # Multiple with 8 to read:

        text = text * 8

        ts = Ts.read(text)

        self.assertHasRead(ts, 48)
        self.assertOutputs(ts, text)

        # Multiple with junk following:

        ts = Ts.read('tomatoPuree')

        self.assertHasRead(ts, 6)
        self.assertOutputs(ts, 'tomato')

        # None:

        ts = Ts.read('')
        self.assertHasRead(ts, 0)
        self.assertOutputs(ts, '')

        # Only Junk:

        ts = Ts.read('sauce made from tomato')
        self.assertHasRead(ts, 0)
        self.assertOutputs(ts, '')


class TestWord(PCTestCase):
    def testalphas(self):

        # basic
        text = 'abc'
        A = Word('abc')

        a = A.read(text)

        self.assertHasRead(a, 3)
        self.assertOutputs(a, 'abc')

        # junk following:

        a = A.read('bcd')

        self.assertHasRead(a, 2)
        self.assertOutputs(a, 'bc')

        # only junk:

        with self.assertRaises(NotHere):
            a = A.read('xyz')

        # nothing:

        with self.assertRaises(NotHere):
            a = A.read('')

    def testJoined(self):

        # basic:
        text = '$variable'
        A = Joined('$', Word(LETTERS))

        a = A.read(text)

        self.assertHasRead(a, 9)
        self.assertOutputs(a, text)

        # junk following:

        text = '$var again'

        a = A.read(text)

        self.assertHasRead(a, 4)
        self.assertOutputs(a, '$var')


        A_ = Joined(A, Word(' '))

        a = A_.read(text)

        self.assertHasRead(a, 5)
        self.assertOutputs(a, '$var ')

        A__ = Joined(A_, Word(LETTERS))

        a = A__.read(text)

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

        p = E.read(text)

        self.assertHasRead(p, 1)
        self.assertOutputs(p, 'a')

        # starting with second choice

        text = 'bcd'

        p = E.read(text)

        self.assertHasRead(p, 1)
        self.assertOutputs(p, 'b')

        # starting with something else

        text = 'def'

        with self.assertRaises(NotHere):
            p = E.read(text)

    def testManySingleLetters(self):

        A = SingleChar('a')
        B = SingleChar('b')
        C = SingleChar('c')

        E = Either(A, B, C)

        # starting with first.

        text = 'abc'

        p = E.read(text)

        self.assertHasRead(p, 1)
        self.assertOutputs(p, 'a')

        # starting with second choice

        text = 'bcd'

        p = E.read(text)

        self.assertHasRead(p, 1)
        self.assertOutputs(p, 'b')

        # starting with third choice

        text = 'cde'

        p = E.read(text)

        self.assertHasRead(p, 1)
        self.assertOutputs(p, 'c')

        # starting with something else

        text = 'def'

        with self.assertRaises(NotHere):
            p = E.read(text)

    def testTwoSingleLettersORsyntax(self):

        # Two choices:

        A = SingleChar('a')
        B = SingleChar('b')

        E = A | B

        # starting with first.

        text = 'abc'

        p = E.read(text)

        self.assertHasRead(p, 1)
        self.assertOutputs(p, 'a')

        # starting with second choice

        text = 'bcd'

        p = E.read(text)

        self.assertHasRead(p, 1)
        self.assertOutputs(p, 'b')

        # starting with something else

        text = 'def'

        with self.assertRaises(NotHere):
            p = E.read(text)

    def testManySingleLettersORsyntax(self):

        A = SingleChar('a')
        B = SingleChar('b')
        C = SingleChar('c')

        E = A | B | C

        # starting with first.

        text = 'abc'

        p = E.read(text)

        self.assertHasRead(p, 1)
        self.assertOutputs(p, 'a')

        # starting with second choice

        text = 'bcd'

        p = E.read(text)

        self.assertHasRead(p, 1)
        self.assertOutputs(p, 'b')

        # starting with third choice

        text = 'cde'

        p = E.read(text)

        self.assertHasRead(p, 1)
        self.assertOutputs(p, 'c')

        # starting with something else

        text = 'def'

        with self.assertRaises(NotHere):
            p = E.read(text)


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
            E.read(' ')

        self.assertReadsFully(EE, ' ')
        self.assertReadsFully(EE, 'a')
        self.assertReadsFully(EE, 'b')

    def testRecursiveEither(self):
        E = Either('a', 'b')
        EE = Either(E, ' ')
        EE.options += (EE,)

        # all normal reading is OK:

        self.assertReadsFully(EE, ' ')
        self.assertReadsFully(EE, 'a')
        self.assertReadsFully(EE, 'b')

        # But reading an unknown char fails:

        with self.assertRaises(NotHere):
            EE.read('c')

        # add a new option AFTER the recursive EE

        EE.options += (SingleChar('c'),)

        self.assertReadsFully(EE, 'c')



    def testWithNothing(self):
        # TODO: add test for Nothing not at end of Either list!

        E = Either(SpecificWord('chocolate'), Nothing())

        text = 'chocolate!'

        e = E.read(text)

        self.assertHasRead(e, 9)
        self.assertOutputs(e, 'chocolate')

        text = 'other sweets'

        e = E.read(text)

        self.assertHasRead(e, 0)
        self.assertOutputs(e, '')




class TestUntil(PCTestCase):
    def testSingleLetter(self):
        P = Until(' ')

        # ends with ending:

        text = 'thing '
        p = P.read(text)
        self.assertHasRead(p, 6)
        self.assertOutputs(p, 'thing ')

        # continues afterwards:

        text = 'thing another'
        p = P.read(text)
        self.assertHasRead(p, 6)
        self.assertOutputs(p, 'thing ')

        # no ending:

        text = 'thisisalongtext'
        p = P.read(text)
        self.assertHasRead(p, 15)
        self.assertOutputs(p, text)

        # no ending, please fail:

        with self.assertRaises(NotHere):
            p = Until(' ', fail_on_eof=True).read(text)


    def testWordEnding(self):
        text = "START do stuff. END"

        # text ends with ending.

        P = Until('END')
        p = P.read(text)
        self.assertHasRead(p, 19)
        self.assertOutputs(p, text)

        # text continues past ending

        text1 = "START do stuff. END and some extra crap. END AGAIN"
        p = P.read(text1)
        self.assertHasRead(p, 19)
        self.assertOutputs(p, text)

        # text doesn't have ending

        text2 = "START do stuff. "
        p = P.read(text2)
        self.assertHasRead(p, 16)
        self.assertOutputs(p, text2)

        # no ending, please fail:

        with self.assertRaises(NotHere):
            p = Until('END', fail_on_eof=True).read(text2)

    def testSingleLetterWithEscape(self):
        P = Until('"', escape='\\')

        # ends with ending:

        self.assertReadsFully(P, 'thing\\" end"')

        # continues afterwards:

        text = 'thing" another'
        p = P.read(text)
        self.assertHasRead(p, 6)
        self.assertOutputs(p, 'thing"')

        # no ending:

        text = 'thisisalongtext'
        p = P.read(text)
        self.assertHasRead(p, 15)
        self.assertOutputs(p, text)

        # no ending, please fail:

        with self.assertRaises(NotHere):
            p = Until(' ', fail_on_eof=True).read(text)

    def testWordEnding(self):
        text = "START do stuff. END"

        # text ends with ending.

        P = Until('END')
        p = P.read(text)
        self.assertHasRead(p, 19)
        self.assertOutputs(p, text)

        # text continues past ending

        text1 = "START do stuff. END and some extra crap. END AGAIN"
        p = P.read(text1)
        self.assertHasRead(p, 19)
        self.assertOutputs(p, text)

        # text doesn't have ending

        text2 = "START do stuff. "
        p = P.read(text2)
        self.assertHasRead(p, 16)
        self.assertOutputs(p, text2)

        # no ending, please fail:

        with self.assertRaises(NotHere):
            p = Until('END', fail_on_eof=True).read(text2)

class TestMultiple(PCTestCase):
    def testMultiLetters(self):
        P = Multiple(SingleChar('a'))

        self.assertReadsFully(P,'')
        self.assertReadsFully(P,'a')
        self.assertReadsFully(P,'aaaaaaaaaa')

        P = Multiple(Either('a','b','c'))

        self.assertReadsFully(P,'')
        self.assertReadsFully(P,'a')
        self.assertReadsFully(P,'b')
        self.assertReadsFully(P,'c')
        self.assertReadsFully(P,'abc')
        self.assertReadsFully(P,'abcbbaaaaccabaccabbaaaa')

    def testMultiEithers(self):
        E = Either(SpecificWord('the'), SpecificWord('cat'))
        S = Multiple(Either(Word(SPACES), E))

        text = 'the cat sat on the mat'

        s = S.read(text)

        self.assertHasRead(s, 8)
        self.assertOutputs(s, 'the cat ')

        text = 'the the the cat, yo. remix!'

        s = S.read(text)

        self.assertHasRead(s, 15)
        self.assertOutputs(s, 'the the the cat')

    def testMultiNothings(self):

        # 3 options, first succeeds:

        E = Either(SpecificWord('chocolate'), ' ', Nothing())

        text = 'chocolate!'

        e = E.read(text)

        self.assertHasRead(e, 9)
        self.assertOutputs(e, 'chocolate')

        # same options, but multiple.  First succeeds:

        M = Multiple(E)

        m = E.read(text)

        self.assertHasRead(m, 9)
        self.assertOutputs(m, 'chocolate')

        # new options, option with Nothing PRECEDING matching option

        ME = Multiple(Either(Either('?', Nothing()), E))

        me = ME.read(text)

        self.assertHasRead(me, 9)
        self.assertOutputs(me, 'chocolate')

    def testWithoutAllowedNone(self):
        text = 'this is some text'

        P = Multiple(Either('a','b','c'))

        p = P.read(text)

        self.assertEquals(output(p), '')

        PF = Multiple(Either('a','b','c'), allow_none=False)

        with self.assertRaises(NotHere):
            pf = PF.read(text)

    def testRecursiveMultiple(self):
        E = Either('a','b')
        M = Multiple(E)
        E.options += (M,)

        self.assertReadsFully(M,'')
        self.assertReadsFully(M,'a')
        self.assertReadsFully(M,'abaabbabaab')

        # and now with options AFTER the Mulitple (test continues after attempt)

        E.options += (SingleChar('c'),)

        self.assertReadsFully(M,'')
        self.assertReadsFully(M,'a')
        self.assertReadsFully(M,'c')
        self.assertReadsFully(M,'abcaacbbabcccccaab')



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




class TestShouldNotBeReachable(TestCase):
    ''' these tests should never actually be reachable in normal code.
        all they do is raise exceptions when someone implements something
        badly.  Of course these aren't included to improve coverage score...'''

    def testParsableRead(self):
        P = Parsable()
        with self.assertRaises(TooGeneric):
            P.read('text')

    def testParsableOutput(self):
        P = Parsable()
        self.assertEquals(P.output({'class': P, 'text': 'stuff' }), 'stuff')

        with self.assertRaises(TooGeneric):
            P.output({'class': P })

