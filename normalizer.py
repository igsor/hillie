"""Normalization helpers

Copyright (c) 2016, Matthias Baumgartner
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions
are met:

1. Redistributions of source code must retain the above copyright
   notice, this list of conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright
   notice, this list of conditions and the following disclaimer in
   the documentation and/or other materials provided with the distribution.

3. Neither the name of the copyright holder nor the names of its contributors
   may be used to endorse or promote products derived from this software
   without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
POSSIBILITY OF SUCH DAMAGE.

"""
# EXPORTS
__all__ = ('Dictionary', 'annotation_fixes')

# IMPORTS
from porter2 import stem
import re
import warnings
import os.path

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
        from basics import unique
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

def annotation_fixes(text, words, verbose=False):
    """

    Systematic errors
    * Leading / trailing whitespaces
    * Punctuation
    * Misplaced hyphens:  hello-\nworld -> hello-world -> helloworld
    * Missing whitespace: hello\nworld -> helloworld -> hello world

    """
    # Unicode hyphens
    text = text.replace('\xe2\x80\x94', ' - ') # Replace in text as well

    # Leading / trailing whitespaces
    normed = text.strip()

    # Remove stuff in brackets
    normed = re.sub('\s*\[.*?\]\s*', ' ', normed).strip()

    # Remove punctuation
    normed = _remove_punctuation(normed).strip()

    mods = []
    cands = normed.split()
    while len(cands) > 0:
        w = cands.pop(0)

        if w == '-' or len(w.strip()) == 0: # Invalid or empty words
            continue

        if '-' in w: # Misplaced hyphens
            repl = w.replace('-', '')
            if words.check(repl):
                mods.append((w, repl))
                continue

        if not words.check(w): # Missing whitespace
            if '-' in w: # Combination of words; Test them individually
                cands.extend(w.split('-'))
                continue

            splits = [[w[:i], w[i:]] for i in range(len(w)+1) if words.check(w[:i]) and words.check(w[i:])]
            if len(splits) == 0:
                if verbose:
                    warnings.warn('No solution found for {}'.format(w))

            elif len(splits) == 1: # Unique result
                mods.append((w, ' '.join(splits[0])))
                continue

            else: # Several results
                score = [sum(map(words.match, s)) for s in splits]
                tmp = sorted(score, reverse=True)
                if tmp[0] != tmp[1]: # Unique result
                    idx = score.index(max(score))
                    mods.append((w, ' '.join(splits[idx])))
                    continue
                elif verbose:
                    warnings.warn('No unique solution found for {}'.format(w))

    for src, trg in mods:
        text = text.replace(src, trg)

    return text.strip()



if __name__ == '__main__':
    # Some tests
    c = Dictionary()
    annots = [l.strip() for l in open('/tmp/annots.t')]
    get_words = lambda text: _remove_punctuation(text).split()

    train = [l.strip() for l in open('/tmp/training.t')]
    samples = [l[len('Original:  '):] for l in train if l.startswith('Original:  ')]
    truths  = [l[len('Suggested: '):] for l in train if l.startswith('Suggested: ')]

    assert(len(samples) == len(truths))

    for idx, t in enumerate(samples):
        samples[idx] = t.replace('--', '\xe2\x80\x94')

    for ip, op in zip(samples, truths):
        if not annotation(ip, c) == op:
            print ip, '\n', annotation(ip, c), '\n', op, '\n'

## EOF ##
