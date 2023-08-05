#!/usr/bin/python
# vim:fileencoding=utf8
from __future__ import unicode_literals

import unittest

class TestParser(unittest.TestCase):
    def test_parser(self):
        import ufal.parsito

        parser = ufal.parsito.Parser.load('test/data/test.parser')
        self.assertTrue(parser)

        conlluInput = ufal.parsito.TreeInputFormat.newInputFormat("conllu");
        conlluOutput = ufal.parsito.TreeOutputFormat.newOutputFormat("conllu");
        tree = ufal.parsito.Tree()

        conlluInput.setText("""\
# Sentence Dobrý den z Prahy
1	Dobrý	_	ADJ	_	_	_	_	_	_
2	den	_	NOUN	_	_	_	_	_	_
3	z	_	ADP	_	_	_	_	_	_
4	Prahy	_	PROPN	_	_	_	_	_	_

""")
        self.assertTrue(conlluInput.nextTree(tree))
        self.assertFalse(conlluInput.lastError())

        parser.parse(tree)

        self.assertEqual(conlluOutput.writeTree(tree, conlluInput), """\
# Sentence Dobrý den z Prahy
1	Dobrý	_	ADJ	_	_	2	amon	_	_
2	den	_	NOUN	_	_	0	root	_	_
3	z	_	ADP	_	_	4	case	_	_
4	Prahy	_	PROPN	_	_	2	dep	_	_

""")

        self.assertFalse(conlluInput.nextTree(tree))

if __name__ == '__main__':
    unittest.main()
