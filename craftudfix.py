#!/usr/bin/env python3

import os
import sys
import re

from logging import warning, info


# https://universaldependencies.org/tagset-conversion/en-penn-uposf.html
PTB_UPOS_MAP = {
    '#': 'SYM',
    '$': 'SYM',
    "''": 'PUNCT',
    ',': 'PUNCT',
    '-LRB-': 'PUNCT',
    '-RRB-': 'PUNCT',
    '.': 'PUNCT',
    ':': 'PUNCT',
    'AFX': 'ADJ',
    'CC': 'CCONJ',
    'CD': 'NUM',
    'DT': 'DET',
    'EX': 'PRON',
    'FW': 'X',
    'HYPH': 'PUNCT',
    'IN': 'ADP',
    'JJ': 'ADJ',
    'JJR': 'ADJ',
    'JJS': 'ADJ',
    'LS': 'X',
    'MD': 'VERB',
    'NIL': 'X',
    'NN': 'NOUN',
    'NNP': 'PROPN',
    'NNPS': 'PROPN',
    'NNS': 'NOUN',
    'PDT': 'DET',
    'POS': 'PART',
    'PRP': 'PRON',
    'PRP$': 'DET',
    'RB': 'ADV',
    'RBR': 'ADV',
    'RBS': 'ADV',
    'RP': 'ADP',
    'SYM': 'SYM',
    'TO': 'PART',
    'UH': 'INTJ',
    'VB': 'VERB',
    'VBD': 'VERB',
    'VBG': 'VERB',
    'VBN': 'VERB',
    'VBP': 'VERB',
    'VBZ': 'VERB',
    'WDT': 'DET',
    'WP': 'PRON',
    'WP$': 'DET',
    'WRB': 'ADV',
    '``': 'PUNCT'
}

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
    ap.add_argument('-v31', default=False, action='store_true',
                    help='apply fixes specific to CRAFT v3.1')
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
    """Convert the UPOS column tags from Penn to UD."""
    for w in words:
        w.upos = PTB_UPOS_MAP.get(w.upos, w.upos)


def remove_extra_whitespace(words):
    """Remove initial and trailing whitespace from FORM and LEMMA columns."""
    for w in words:
        w.form = w.form.strip()
        w.lemma = w.lemma.strip()


def main(argv):
    args = argparser().parse_args(argv[1:])
    for fn in args.conllu:
        with open(fn) as f:
            for comments, words in read_sentences(f):
                if args.v31:
                    fix_feature_column(words)
                    map_upos_column(words)
                remove_extra_whitespace(words)
                write_sentence(comments, words)


if __name__ == '__main__':
    sys.exit(main(sys.argv))
