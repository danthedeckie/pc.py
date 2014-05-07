'''
    basic PHP unit tests for pc.py parser-combinator library.
    ------
    Copyright (C) 2014 Daniel Fairhead
    GPL3 Licence.

'''
# pylint: disable=too-many-public-methods, missing-docstring, invalid-name
# pylint: disable=no-self-use, wildcard-import

from unittest import TestCase
from test import PCTestCase

from pc import *
from php import *

class TestVar(PCTestCase):
    def testGood(self):
        text = '$thing'
        v = VAR.read(text)

        self.assertHasRead(v, 6)
        self.assertOutputs(v, text)

        text = '$thing_two '

        v = VAR.read(text)

        self.assertHasRead(v, 10)
        self.assertOutputs(v, '$thing_two')

    def testBad(self):
        text = '%other'

        with self.assertRaises(NotHere):
            v = VAR.read(text)

        text = '$-32'

        with self.assertRaises(NotHere):
            v = VAR.read(text)

        text = ''

        with self.assertRaises(NotHere):
            v = VAR.read(text)


class TestWord(PCTestCase):
    def testGood(self):
        # TODO
        pass
    def testBad(self):
        # TODO
        pass


class TestComplexVar(PCTestCase):
    def testGood(self):
        # TODO
        pass
    def testBad(self):
        # TODO
        pass


class TestString(PCTestCase):
    def testGood(self):
        text = '"this is a string"'
        s = STRING.read(text)
        self.assertHasRead(s, 18)
        self.assertOutputs(s, text)
    def testBad(self):
        # TODO
        pass

class TestNumber(PCTestCase):
    def testGood(self):
        # TODO
        pass
    def testBad(self):
        # TODO
        pass

class TestOperator(PCTestCase):
    def testGood(self):
        # TODO
        pass
    def testBad(self):
        # TODO
        pass

class TestComment(PCTestCase):
    def testGood(self):
        # TODO
        pass
    def testBad(self):
        # TODO
        pass

class TestWhiteSpace(PCTestCase):
    def testGood(self):
        # TODO
        pass
    def testBad(self):
        # TODO
        pass

class TestCommentOrWhiteSpace(PCTestCase):
    def testGood(self):
        # TODO
        pass
    def testBad(self):
        # TODO
        pass

########################################

# TODO: somehow tests for phpitem & PHPJoin?

class TestThing(PCTestCase):
    def testGood(self):
        # TODO
        pass
    def testBad(self):
        # TODO
        pass

class TestFuncApp(PCTestCase):
    def testGood(self):
        # TODO
        pass
    def testBad(self):
        # TODO
        pass
    def testRecursive(self):
        # TODO
        pass

class TestInfixed(PCTestCase):
    def testGood(self):
        # TODO
        pass
    def testBad(self):
        # TODO
        pass
    def testRecursive(self):
        # TODO
        pass

class TestExpr(PCTestCase):
    def testGood(self):
        # TODO
        pass
    def testBad(self):
        # TODO
        pass
    def testRecursive(self):
        # TODO
        pass


class TestStatement(PCTestCase):
    def testGood(self):
        text = 'echo "hi!";'
        P = STATEMENT.read(text)
        # TODO
        pass
    def testBad(self):
        # TODO
        pass
    def testRecursive(self):
        # TODO
        pass


class TestAssignment(PCTestCase):
    def testGood(self):
        # TODO
        pass
    def testBad(self):
        # TODO
        pass
    def testRecursive(self):
        # TODO
        pass


class TestPHP_Line(PCTestCase):
    def testGood(self):
        # TODO
        pass
    def testBad(self):
        # TODO
        pass
    def testRecursive(self):
        # TODO
        pass






class TestPHPEcho(PCTestCase):

    def testEcho(self):
        things = [
            '<?php echo "hi"; ?>']

        for t in things:
            x = PHP_BLOCK.read(t)
            print x
