[![Build Status](https://travis-ci.org/danthedeckie/pc.py.svg?branch=master)](https://travis-ci.org/danthedeckie/pc.py) [![Coverage Status](https://img.shields.io/coveralls/danthedeckie/pc.py.svg)](https://coveralls.io/r/danthedeckie/pc.py?branch=master)

PC, a simple python parser/combinator attempt, with the intention
of parsing PHP (eventually), in a whitespace sensative manner, so that
it can either be cleaned up, or otherwise useful.

Mainly because I've never written a parser-combinator lib before, and it
looked interesting.

I've avoided using any regexps at all so far.  The total parser/library is
around 400 lines, about 100 of which are comments/docstrings/blank, so it should be
very easy to read through and understand.

## The main primatives:

class         | What is does:
------------- | ---------------------------------------------------------------
SingleChar    | Matches a single character. (`a`, `;`, `(`, etc.)
SpecificWord  | Matches a Specific word (`if`, `class`, `start`, etc.)
Word          | Matches any word made up from a set of valid characters.
Until         | Matches anything up until an 'end' marker (e.g. `comment until */`)
Nothing       | always matches, but consumes 0 characters.
Joined        | Joins two (or more) other parsables into a single unit.
Either        | Matches any 1 of a selection of parsables
Multiple      | Matches a parsable multiple (or 0, if you want) times.
NamedJoin     | Like a join, but parsed elements are stored in a dict, rather than list.

## Conceptual usage:

You put together Parsable groups using the above primitives:

```python
    PIE = SpecificWord('Lemon meringue pie')
    CAKE = SpecificWord('Chocolate-cake')
    DESERTS = Either(PIE, CAKE)
```

You can then attempt to parse these:

```python
    DESERTS.parse("Chocolate-cake")
```

and it will return a tuple: `(chars_read, dict of parsed parts)`:

```python
    (14, {'text': 'Chocolate-cake', 'class': <SpecificWord:"Chocolate-cake">})
```

each part of the dict usually has a `"text"` or other data that was parsed, and a `class` key
which points to the actual type of data that has been parsed.  For complex parts, (Joined, etc.)
it won't have a `text`, but the sub-parts will.

### Errors:

If it can't parse the text, then it will raise a `NotHere` exception.  This is the main
control mechanism which allows `Either`, `Joined`, `Multiple` etc. to work.

## Example usage:

```python
    >>> ME = SpecificWord('Daniel')
    >>> p = ME.parse("Daniel")
    >>> p
    (6, {'text': 'Daniel', 'class': <SpecificWord:"Daniel">})

    >>> output(p[1])
    "Daniel"

    >>> ME.parse("Becky")
    Traceback (most recent call last):
    ...
    pc.NotHere: Expected "Daniel", instead found: "Becky"
```

And a more complex example:

```python
    >>> VERB = Either('says', 'gives', 'takes', 'likes') # automatically converts into SpecificWord
    >>> NOUN = Either('cat', 'fruit', 'book')
    >>> SPACES = Word(' \t') # Spaces or tabs

    >>> SENTENCE = Joined(NOUN, SPACES, VERB, SPACES, NOUN)

    >>> a = SENTENCE.parse("cat gives    book")
    >>> a
    (18, {"class": <Joined>, "parts": [
            {"text": "cat", "class": <SpecificWord:"cat">},
            {"text": " ", "class": <Word:" \t">},
            {"text": "gives", "class": <SpecificWord:"gives">},
            {"text": " ", "class": <Word:" \t">},
            {"text": "book", "class": <SpecificWord:"book">}
         ]})

    >>> output(a[1])
    "cat gives    book"
```

And the `NamedJoin` (initially):

```python
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

    assert(output(munchies['parts']['subject']) == 'the cats')
    assert(output(munchies['parts']['verb']) == 'have')
    assert(output(munchies['parts']['object']) == 'dinner')
```

This (I'm hoping) will be more useful with parsing function definitions, etc. so
you'll be able to parse it into a `name`, `args`, `docstring`, `body`, and so on,
rather than having to walk around the tree after parsing.  This should work well
where there are optional things, and also where there are things which can be in
different orders.  Javascript (for instance) can have functions defined:

```javascript
var foo = function(){ return 42;}
// or
function bar() { return 42; }
```

and you may well want to parse both of them as function definitions, so that you
can make sure function names have a consistent style throughout a whole project.

## Building something useful

So, cool, it can parse it all into a tree.  Very nice.  But how can this be used usefully?

Well, there are two ways to make use of the tree.  The first is to write a walking function
which descends through the tree and does stuff.  This would work pretty well, but I suspect would
also end up with fairly complex and messy walking functions.

The other way is to make the Parseable bits actually have some level of extensibility.

For instance, to make an uncrustify/fmt/whatever tool, one task is to clean up the indentation.

If you make a `Word(' \t\n')` type of parser which reads any kind of whitespace,
you could easily make an indentation aware version:

```python
    class Indent(Word):
        def output(self, data, clean=False):
            if clean and 'current_indent' in clean:
                lines = data['text'].count('\n')
                return (lines * '\n') + current_indent
            else:
                return data['text']

    INDENT = Indent(' \t\n')    
```

which will return the current indent level, with any extra newlines, and strips out any
extraneous spaces on blank newlines.

Then you'd subclass your function & block parsers to increment and decrement
`clean['current_indent']` appropriately.

Since the parts are all python classes, you can subclass from them easily.  But also, once
all the parsing stuff is done correctly and tested, I'd like to add some 'hooks' (`after_parse`,
`before_output`, etc.) so that you can 'do stuff' without needing to subclass.

## Extras:

There are a couple of useful functions included for debugging & playing purposes:

### `output(parsed_block, clean=False)`

which traverses through the parsed tree, getting output through the `.output` methods of each
class.  The `'clean'` object is passed all the way through the traversal, so you could use this
to either send specific "flags" so lower parts of the tree ("clean up indentation", "rename
variables that match global names", etc.) or to have parts of the parse tree return information
to you (a list of all the variables, unused imports, etc).

### `pretty_print(parsed_block, level=0)`

prints out a parsed tree (to stdout) in a simplified

```
    Multiple:
        Joined:
            Word:"the"
            Word:" "
        Joined:
            Word":"cat"
            Word:" "
        Joined:
            Word:"sat"
            Word":" "
```

type of manner.

### `parts(parsed)`

returns a generator, which walks through the tree yielding each textual match
as it finds it.

```python
    >>> [x for x in parts(example)]
    ['the', ' ', 'cat', ' ', 'sat']
```

for instance.


# Current Status:

I'm writing a PHP parser (also included here, called: php.py) which is very very very much
in progress.  The main pc.py parsed-combinator lib seems at about the stage where I can do that.
I'm sure I'll find plenty of bugs while writing it.

Once PHP is parsing happily, and I've got a reasonable phpfmt tool out of it, then I'll play with
similar languages, such as javascript.  I may then look at other expansions/uses for it.  We'll see.

# Future thoughts:

It would be nice to include more 'sugar', to make writing parsers a little more readable.
Currently there only exists `|` for either:

```python
    SpecificWord('Daniel') | SpecificWord('Becky') | Nothing()
```

which works quite well.  It would be interesting to add `+`, and other
operators.

GPL3 Licenced.
Copyright (C) 2014 Daniel Fairhead
