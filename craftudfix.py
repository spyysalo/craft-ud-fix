#!/usr/bin/env python3

import os
import sys
import re

from logging import warning, info


class Word(object):
    def __init__(self, id_, form, lemma, upos, xpos, feats, head, deprel,
                 deps, misc):
        self.id = id_
        self.form = form
        self.lemma = lemma
        self.upos = upos
        self.xpos = xpos
        self.feats = feats
        self.head = head
        self.deprel = deprel
        self.deps = deps
        self.misc = misc

    def __str__(self):
        return '\t'.join([
            self.id, self.form, self.lemma, self.upos, self.xpos, self.feats,
            self.head, self.deprel, self.deps, self.misc
        ])


def argparser():
    from argparse import ArgumentParser
    ap = ArgumentParser(description='Fix CRAFT corpus .conllu data')
    ap.add_argument('conllu', nargs='+', help='CoNLL-U files')
    return ap


def read_sentences(f):
    comments, words = [], []
    for ln, l in enumerate(f, start=1):
        l = l.rstrip('\n')
        if not l or l.isspace():
            if words:
                yield comments, words
            else:
                warning('ignoring empty sentence on {} line {}'.format(
                    f.name, ln))
            comments, words = [], []
        elif l.startswith('#'):
            comments.append(l)
        else:
            fields = l.split('\t')
            words.append(Word(*fields))


def write_sentence(comments, words, out=sys.stdout):
    for c in comments:
        print(c, file=out)
    for w in words:
        print(w, file=out)
    print(file=out)


def fix_feature_column(words):
    """Move features appearing in the XPOS column to the FEATS column."""
    for w in words:
        if '=' in w.xpos:
            if w.feats != '_':
                raise ValueError('fix_feature_column: non-empty FEATS: {}'.\
                                 format(w.feats))
            info('replacing FEATS with XPOS for word: {}'.format(w))
            w.feats = w.xpos
            w.xpos = '_'


def map_upos_column(words):
    "Convert the pos tags from penn to universal"
    penn_tags = ['#', '$', '"', ',', '-LRB-', '-RRB-', '.', ':', 'AFX', 'CC', 'CD', 'DT', 'EX', 'FW', 'HYPH', 'IN', 'JJ', 'JJR', 'JJS', 'LS', 'MD', 'NIL', 'NN', 'NNP', 'NNPS', 'NNS', 'PDT', 'POS', 'PRP', 'PRP$', 'RB', 'RBR', 'RBS', 'RP', 'SYM', 'TO', 'UH', 'VB', 'VBD', 'VBG', 'VBN', 'VBP', 'VBZ', 'WDT', 'WP', 'WP$', 'WRB', '``']
    universal_tags = ['SYM', 'SYM', 'PUNCT', 'PUNCT', 'PUNCT', 'PUNCT', 'PUNCT', 'PUNCT', 'ADJ', 'CCONJ', 'NUM', 'DET', 'PRON', 'X', 'PUNCT', 'ADP', 'ADJ', 'ADJ', 'ADJ', 'X', 'VERB', 'X', 'NOUN', 'PROPN', 'PROPN', 'NOUN', 'DET', 'PART', 'PRON', 'DET', 'ADV', 'ADV', 'ADV', 'ADP', 'SYM', 'PART', 'INTJ', 'VERB', 'VERB', 'VERB', 'VERB', 'VERB', 'VERB', 'DET', 'PRON', 'DET', 'ADV', 'PUNCT']
    for w in words:
        tag_id = [id for id, tag in enumerate(penn_tags) if w.upos == tag][0]
        w.upos = universal_tags[tag_id]


def main(argv):
    args = argparser().parse_args(argv[1:])
    for fn in args.conllu:
        with open(fn) as f:
            for comments, words in read_sentences(f):
                fix_feature_column(words)
                map_upos_column(words)
                write_sentence(comments, words)


if __name__ == '__main__':
    sys.exit(main(sys.argv))
