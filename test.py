from unittest import TestCase

from pc import *
from php import PHP_BLOCK

# pylint: disable=too-many-public-methods, missing-docstring, invalid-name, no-self-use

class PCTestCase(TestCase):
    def assertHasRead(self, parsed, length):
        assert parsed[0] == length

    def assertTexts(self, parsed, texts):
        for a, b in zip(parsed[1]['parts'], texts):
            assert a['text'] == b

    def assertOutputs(self, parsed, text):
        assert output(parsed) == text

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

    def testMulitpleSingleChar(self):

        text = 'a'

        A = Multiple(SingleChar('a'))
        A_ = Multiple(Either(SingleChar('a'), Nothing()))

        a = A.read(text+text)
        print a
        self.assertHasRead(a, 2)

        a = A.read(text * 4)
        print a
        self.assertHasRead(a, 4)

    def testAthenB(self):

        text = 'ab'

        A = Multiple(SingleChar('a'))
        A_ = Multiple(Either(SingleChar('a'), Nothing()))

        B = Multiple(SingleChar('b'))
        B_ = Multiple(Either(SingleChar('b'), Nothing()))

        ab = Joined(A, B).read(text)

        print '---'
        print ab
        print '___'

        self.assertHasRead(ab, 2)
        self.assertOutputs(ab, text)

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


    def testMulitpleSpecificWords(self):

        #mulitple, but only 1 to read:
        text = 'tomato'

        T = SpecificWord('tomato')
        Ts = Multiple(T)

        ts = Ts.read(text)

        self.assertHasRead(ts, 6)
        self.assertOutputs(ts, text)

        # Mulitple with 8 to read:

        text = text * 8

        ts = Ts.read(text)

        self.assertHasRead(ts, 48)
        self.assertOutputs(ts, text)

        # Mulitple with junk following:

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

    

'''
class TestPHPEcho(PCTestCase):

    def testEcho(self):
        things = [
            '<?php echo "hi"; ?>']

        for t in things:
            x = PHP_BLOCK.read(t)
            print x

'''
