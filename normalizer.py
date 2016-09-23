
from porter2 import stem
import re
import warnings
import os.path

def remove_all(lst, item):
    """Remove all occurences of *item* in *lst*."""
    while item in lst:
        lst.remove(item)
    return lst

unique = lambda s: list(set(s))

def _remove_punctuation(text):
    return text \
            .replace('.', '') \
            .replace(',', '') \
            .replace('!', '') \
            .replace('?', '') \
            .replace(':', '') \
            .replace(';', '') \
            .replace('(', '') \
            .replace(')', '') \
            .replace('{', '') \
            .replace('}', '') \
            .replace('[', '') \
            .replace(']', '')

class Dictionary(object):
    def __init__(self, stems=None, words=None):
        if stems is None:
            stems = os.path.join(os.path.dirname(__file__), 'stems.t')
        if words is None:
            words = os.path.join(os.path.dirname(__file__), 'words.t')

        self.stems = [l.strip() for l in open(stems)]
        self.words = [l.strip() for l in open(words)]

    @staticmethod
    def build_dict(src, dst_stems='stems.t', dst_words='words.t'):
        words = [l.strip().lower() for l in open(src)]
        words = unique(words)
        words = sorted(words)

        fw = open(dst_words, 'w')
        for w in words:
            fw.write(w + '\n')
        fw.close()

        words = map(stem, words)
        words = unique(words)
        words = sorted(words)

        fs = open(dst_stems, 'w')
        for w in words:
            fs.write(w + '\n')
        fs.close()

    def check(self, candidate):
        if len(candidate) == 0:
            return False

        normed = stem(candidate.lower())
        return normed in self.stems

    def match(self, candidate):
        if len(candidate) == 0:
            return False

        normed = candidate.lower()
        return normed in self.words

def annotation(text, words, options):
    """

    Systematic errors
    * Leading / trailing whitespaces
    * Punctuation
    * Misplaced hyphens:  hello-\nworld -> hello-world -> helloworld
    * Missing whitespace: hello\nworld -> helloworld -> hello world
    * Formula errors

    """
    # Leading / trailing whitespaces
    normed = text.strip()

    # Remove stuff in brackets
    normed = re.sub('\s*\[.*?\]\s*', ' ', normed).strip()

    # Remove punctuation
    normed = _remove_punctuation(normed).strip()

    # Unicode hyphens
    normed = normed.replace('\xe2\x80\x94', ' - ').strip()

    mods = []
    for w in normed.lower().split():
        if w == '-' or len(w.strip()) == 0: # Invalid or empty words
            continue

        elif '-' in w: # Misplaced hyphens
            repl = w.replace('-', '')
            if words.check(repl):
                mods.append((w, repl))

        elif not words.check(w): # Missing whitespace
            splits = [[w[:i], w[i:]] for i in range(len(w)+1) if words.check(w[:i]) and words.check(w[i:])]
            if len(splits) == 0:
                if options.verbose:
                    warnings.warn('No solution found for {}'.format(w))

            elif len(splits) == 1: # Unique result
                mods.append((w, ' '.join(splits[0])))

            else: # Several results
                score = [sum(map(words.match, s)) for s in splits]
                tmp = sorted(score, reverse=True)
                if tmp[0] != tmp[1]: # Unique result
                    idx = score.index(max(score))
                    mods.append((w, ' '.join(splits[idx])))
                elif options.verbose:
                    warnings.warn('No unique solution found for {}'.format(w))


    for src, trg in mods:
        text = text.replace(src, trg)

    return text



if __name__ == '__main__':
    c = Dictionary()
    annots = [l.strip() for l in open('/tmp/annots.t')]
    get_words = lambda text: _remove_punctuation(text).split()

## EOF ##
