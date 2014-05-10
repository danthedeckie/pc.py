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
    def testLineComment(self):
        text = '// thing. '
        p = COMMENT.read(text)
        self.assertHasRead(p, 10)
        self.assertOutputs(p, text)

    def testInlineComment(self):
        text = '/* hidden */'
        p = COMMENT.read(text)
        self.assertHasRead(p, 12)
        self.assertOutputs(p, text)

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

class TestCommentsOrWhiteSpace(PCTestCase):
    def testSingleSpace(self):
        text = ' '
        p = COMMENTS_OR_WHITESPACE.read(text)
        self.assertHasRead(p, 1)
        self.assertOutputs(p, text)

    def testMultipleSpaces(self):
        text = '   '
        p = COMMENTS_OR_WHITESPACE.read(text)
        self.assertHasRead(p, 3)
        self.assertOutputs(p, text)

    def testMultipleTypesOfSpaces(self):
        text = '  \t '
        p = COMMENTS_OR_WHITESPACE.read(text)
        self.assertHasRead(p, 4)
        self.assertOutputs(p, text)

        text = '  \t\n\n  '
        p = COMMENTS_OR_WHITESPACE.read(text)
        self.assertHasRead(p, 7)
        self.assertOutputs(p, text)

    def testComment(self):
        text = '// thing. '
        p = COMMENTS_OR_WHITESPACE.read(text)
        self.assertHasRead(p, 10)
        self.assertOutputs(p, text)

    def testNone(self):
        text = 'other stuff'
        p = COMMENTS_OR_WHITESPACE.read(text)
        self.assertHasRead(p, 0)
        self.assertOutputs(p, '')

    def testSpaceComment(self):
        text = ' // space, then comment!'

        p = COMMENTS_OR_WHITESPACE.read(text)
        self.assertHasRead(p, len(text))
        self.assertOutputs(p, text)

    def testSpaceInlineCommentSpace(self):
        text = ' /* inline comment */ '

        p = COMMENTS_OR_WHITESPACE.read(text)
        self.assertHasRead(p, len(text))
        self.assertOutputs(p, text)

    def testMixture(self):
        text = '\n /* inline comment */\n /* more\n things */ \n // stuff\n  '

        p = COMMENTS_OR_WHITESPACE.read(text)
        self.assertHasRead(p, len(text))
        self.assertOutputs(p, text)



########################################
# TODO: somehow tests for phpitem & PHPJoin?

class TestThing(PCTestCase):
    def testVar(self):
        self.assertReadsFully(THING, '$thing')
        self.assertReadsFully(THING, '$thing->$more')
        self.assertReadsFully(THING, '$thing->$more->$thing')
        self.assertReadsFully(THING, 'CONST')
        self.assertReadsFully(THING, '22')
        self.assertReadsFully(THING, '3.14')
        self.assertReadsFully(THING, '"text"')
        self.assertReadsFully(THING, "'t\\'ext'")
        self.assertReadsFully(THING, "blah ($x)")

    def testBad(self):
        # TODO
        pass

class TestFuncApp(PCTestCase):
    def testGood(self):
        text = 'blah($s)'
        a = PHPJoin(WORD,'(', Either(THING, Nothing())).read(text)
        print a
        b = FUNC_APP.read(text)
        print b
        self.assertReadsFully(FUNC_APP, "blah($x)")
        self.assertReadsFully(FUNC_APP, "blah ($x)")
        self.assertReadsFully(FUNC_APP, "blah ($x, $y)")
        self.assertReadsFully(FUNC_APP, "blah($x, $y ,$z)")
        self.assertReadsFully(FUNC_APP, "blah ()")
        self.assertReadsFully(FUNC_APP, "blah(91)")
        self.assertReadsFully(FUNC_APP, "blah('text')")
        self.assertReadsFully(FUNC_APP, "blah(blah(22))")
        self.assertReadsFully(FUNC_APP, "blah(blah($thing->$subvar))")
        self.assertReadsFully(FUNC_APP, "blah(blah())")

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
        text = '$x = 21;'
        p = ASSIGNMENT.read(text)
        self.assertHasRead(p, 8)
        self.assertOutputs(p, text)

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




'''
class TestPHPEcho(PCTestCase):

    def testEcho(self):
        things = [
            '<?php echo "hi"; ?>']

        for t in things:
            x = PHP_BLOCK.read(t)
            print x
'''
