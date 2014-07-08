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
        v = VAR.parse(text)

        self.assertHasRead(v, 6)
        self.assertOutputs(v, text)

        text = '$thing_two '

        v = VAR.parse(text)

        self.assertHasRead(v, 10)
        self.assertOutputs(v, '$thing_two')

        # TODO: test bracketed vars, complex_vars (with bracketing...)

    def testBad(self):
        text = '%other'

        with self.assertRaises(NotHere):
            v = VAR.parse(text)

        text = '$-32'

        with self.assertRaises(NotHere):
            v = VAR.parse(text)

        text = ''

        with self.assertRaises(NotHere):
            v = VAR.parse(text)


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
        self.assertReadsFully(STRING, '"this is a string"')
        self.assertReadsFully(STRING, '"this is a \\"sub\\" string"')
        self.assertReadsFully(STRING, '"this isn\'t a problem"')
        self.assertReadsFully(STRING, '""')

        self.assertReadsFully(STRING, "'this is a string'")
        self.assertReadsFully(STRING, "'this is\\'t a sub-quoted"
                                      " \"string\" string'")
        self.assertReadsFully(STRING, "''")

        # TODO: multi-line strings?

    def testBad(self):
        # TODO
        pass

class TestNumber(PCTestCase):
    def testGood(self):
        self.assertReadsFully(NUMBER, '3')
        self.assertReadsFully(NUMBER, '3.14')
        self.assertReadsFully(NUMBER, '300')
        self.assertReadsFully(NUMBER, '300.9')
        self.assertReadsFully(NUMBER, '-10')
        self.assertReadsFully(NUMBER, '-10.28190')
        self.assertReadsFully(NUMBER, '0')
    def testBad(self):
        # TODO
        pass

class TestOperator(PCTestCase):
    def testGood(self):
        self.assertReadsFully(OPERATOR, '===')
        self.assertReadsFully(OPERATOR, '==')
        self.assertReadsFully(OPERATOR, '=')
        # TODO
        pass
    def testBad(self):
        # TODO
        pass

class TestComment(PCTestCase):
    def testLineComment(self):
        text = '// thing. '
        p = COMMENT.parse(text)
        self.assertHasRead(p, 10)
        self.assertOutputs(p, text)

    def testInlineComment(self):
        text = '/* hidden */'
        p = COMMENT.parse(text)
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
        p = COMMENTS_OR_WHITESPACE.parse(text)
        self.assertHasRead(p, 1)
        self.assertOutputs(p, text)

    def testMultipleSpaces(self):
        text = '   '
        p = COMMENTS_OR_WHITESPACE.parse(text)
        self.assertHasRead(p, 3)
        self.assertOutputs(p, text)

    def testMultipleTypesOfSpaces(self):
        text = '  \t '
        p = COMMENTS_OR_WHITESPACE.parse(text)
        self.assertHasRead(p, 4)
        self.assertOutputs(p, text)

        text = '  \t\n\n  '
        p = COMMENTS_OR_WHITESPACE.parse(text)
        self.assertHasRead(p, 7)
        self.assertOutputs(p, text)

    def testComment(self):
        text = '// thing. '
        p = COMMENTS_OR_WHITESPACE.parse(text)
        self.assertHasRead(p, 10)
        self.assertOutputs(p, text)

    def testNone(self):
        text = 'other stuff'
        p = COMMENTS_OR_WHITESPACE.parse(text)
        self.assertHasRead(p, 0)
        self.assertOutputs(p, '')

    def testSpaceComment(self):
        text = ' // space, then comment!'

        p = COMMENTS_OR_WHITESPACE.parse(text)
        self.assertHasRead(p, len(text))
        self.assertOutputs(p, text)

    def testSpaceInlineCommentSpace(self):
        text = ' /* inline comment */ '

        p = COMMENTS_OR_WHITESPACE.parse(text)
        self.assertHasRead(p, len(text))
        self.assertOutputs(p, text)

    def testMixture(self):
        text = '\n /* inline comment */\n /* more\n things */ \n // stuff\n  '

        p = COMMENTS_OR_WHITESPACE.parse(text)
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
        self.assertReadsFully(THING, "$x + 18")

    def testBad(self):
        # TODO
        pass

class TestFuncApp(PCTestCase):
    def testGood(self):
        text = 'blah($s)'
        a = PHPJoin(WORD,'(', Either(THING, Nothing()),')').parse(text)
        b = FUNC_APP.parse(text)

        self.assertReadsFully(FUNC_APP, "blah($x)")
        self.assertReadsFully(FUNC_APP, "blah ($x)")
        self.assertReadsFully(FUNC_APP, "blah ($x, $y)")
        self.assertReadsFully(FUNC_APP, "blah ($x + $x, $y / 21)")
        self.assertReadsFully(FUNC_APP, "blah($x, $y ,$z)")
        self.assertReadsFully(FUNC_APP, "blah ()")
        self.assertReadsFully(FUNC_APP, "blah ( )")
        self.assertReadsFully(FUNC_APP, "blah (  )")
        self.assertReadsFully(FUNC_APP, "blah(91)")
        self.assertReadsFully(FUNC_APP, "blah('text')")
        self.assertReadsFully(FUNC_APP, "blah(blah(22))")
        self.assertReadsFully(FUNC_APP, "blah(blah($thing->$subvar))")
        self.assertReadsFully(FUNC_APP, "blah(blah())")

    def testBad(self):
        # TODO
        pass
    def testRecursive(self):
        self.assertReadsFully(FUNC_APP, "blah(blah())")
        self.assertReadsFully(FUNC_APP, "foo(bar(baz()))")
        self.assertReadsFully(FUNC_APP, '''foo(bar(), baz(FIBBLE, $teapot),
                                           $apricot)''')

class TestInfixed(PCTestCase):
    def testGood(self):
        self.assertReadsFully(INFIXED, '2 + 21')
        self.assertReadsFully(INFIXED, '$x + 21')
        self.assertReadsFully(INFIXED, '$x + 21 + 8')
        self.assertReadsFully(INFIXED, '$x + (21 + 87)')
        self.assertReadsFully(INFIXED, '$x + 21 + 8 / funcop()')

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
        P = STATEMENT.parse(text)
        # TODO
        pass
    def testBad(self):
        # TODO
        pass
    def testRecursive(self):
        # TODO
        pass


class TestAssignment(PCTestCase):
    def testSimple(self):
        self.assertReadsFully(ASSIGNMENT, '$x = 21')
        self.assertReadsFully(ASSIGNMENT, '$x =dostuff(21)')
        self.assertReadsFully(ASSIGNMENT, '$x_the_thing = dostuff(21)')
        self.assertReadsFully(ASSIGNMENT, '$x_the_thing     = dostuff(21)')
        self.assertReadsFully(ASSIGNMENT, '$x_the_thing=NULL')
        self.assertReadsFully(ASSIGNMENT, '$x["value"] = $elephant->$trunk')
        self.assertReadsFully(ASSIGNMENT, '$x->$y->$z["value"] = $elephant->$trunk')

    def testSpacesAndCommentsInRandomPlaces(self):
        self.assertReadsFully(ASSIGNMENT, '$x /* thing */ = 21')
        self.assertReadsFully(ASSIGNMENT, '''$x /* thing */ \n
            = 21''')
        self.assertReadsFully(ASSIGNMENT, '''$x // thing 
                                             = 21''')
        self.assertReadsFully(ASSIGNMENT, '''$x  =// thing 
                                             21''')


    def testBad(self):
        # TODO
        pass
    def testRecursive(self):
        # TODO
        pass

class TestIf(PCTestCase):
    def testSimple(self):
        self.assertReadsFully(IF, "if ($x == 21) { echo 'yep.'; }")
        self.assertReadsFully(IF, """if ($x == 21) {
                echo 'yep.';
                }""")

    def testRecursive(self):
        self.assertReadsFully(IF, """if ($x == 21) {
                if ($y == 19) { echo "still good"; }
                }""")

class TestFORConditions(PCTestCase):
    def testGood(self):
        self.assertReadsFully(FOR_CONDITIONS, '$x=21;$x<200;$x++')
        self.assertReadsFully(FOR_CONDITIONS, '$x=21,$y = 0;$x<200;$x++')
        self.assertReadsFully(FOR_CONDITIONS, '''$x= "string", $y = 0;
                                                $y < 200, len($x) < 100 ;
                                                /*increment */ $x .= "+" ''')

class TestPHP_Line(PCTestCase):
    def testGood(self):
        # assignment:
        self.assertReadsFully(PHP_LINE, "$x = 21;")
        self.assertReadsFully(PHP_LINE, "$x = func(21);")
        self.assertReadsFully(PHP_LINE, "$x = func(21); // comment")
    def testMuliline(self):
        self.assertReadsFully(PHP_LINE, '''$var // thing.
                                            = more("stuff");''')


class TestPHPStatement(PCTestCase):
    def testGood(self):
        self.assertReadsFully(STATEMENT, "if ($x == 21) { echo 'yep.'; }")
        self.assertReadsFully(STATEMENT, "for ($x = 21; $x<299; $x++) { echo 'yep.'; }")
        self.assertReadsFully(STATEMENT, 'foreach ($x as $y) { echo "y:$y"; }')
        self.assertReadsFully(STATEMENT, "foreach ($xs as $k =>$v) { echo 'yep.'; }")

    def testBad(self):
        # TODO
        pass
    def testRecursive(self):
        # TODO
        pass



class TestPHPEcho(PCTestCase):

    def testEcho(self):
        things = [
            '<?php echo "hi"; ?>',
            '<?php $x = 21; ?>',
            '<?php if($x == 21) { echo "hi"; } ?>',
            '''<?php for($x=0;$x<200;$x++) {
                    echo $x; } ?>''',
            '''<?php
                    for($x=0; $x<200; $x++)
                        echo $x;
                ?>'''

            ]

        for t in things:
            self.assertReadsFully(PHP_BLOCK, t)
