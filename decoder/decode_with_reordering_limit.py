#!/usr/bin/env python
import optparse
import sys
import models
from collections import namedtuple

optparser = optparse.OptionParser()
optparser.add_option("-i", "--input", dest="input", default="data/input", help="File containing sentences to translate (default=data/input)")
optparser.add_option("-t", "--translation-model", dest="tm", default="data/tm", help="File containing translation model (default=data/tm)")
optparser.add_option("-l", "--language-model", dest="lm", default="data/lm", help="File containing ARPA-format language model (default=data/lm)")
optparser.add_option("-n", "--num_sentences", dest="num_sents", default=sys.maxint, type="int", help="Number of sentences to decode (default=no limit)")
optparser.add_option("-k", "--translations-per-phrase", dest="k", default=1, type="int", help="Limit on number of translations to consider per phrase (default=1)")
optparser.add_option("-s", "--stack-size", dest="s", default=1, type="int", help="Maximum stack size (default=1)")
optparser.add_option("-v", "--verbose", dest="verbose", action="store_true", default=False,  help="Verbose mode (default=off)")
optparser.add_option("-d", "--reorder_limit", dest="d", default=6, type="int", help="Limit on the amount of reordering (default=6)")
opts = optparser.parse_args()[0]

tm = models.TM(opts.tm, opts.k)
lm = models.LM(opts.lm)
french = [tuple(line.strip().split()) for line in open(opts.input).readlines()[:opts.num_sents]]

# tm should translate unknown words as-is with probability 1
for word in set(sum(french,())):
  if (word,) not in tm:
    tm[(word,)] = [models.phrase(word, 0.0)]

def get_possible_options(f, h):
    output = []
    last_on_bit = h.last_on_bit
    if h.last_on_bit is None:
      last_on_bit = -1
    for i in range(0, len(f)):
      for j in range(i+1, len(f)+1):
        if (h.bitmap[i:j] == [0]*(j-i)) and (i - last_on_bit <= opts.d):
          if f[i:j] in tm:
            for phrase in tm[f[i:j]]:
              output.append((phrase, i, j-1, max(last_on_bit, j-1)))
    return output

sys.stderr.write("Decoding %s...\n" % (opts.input,))
for num, f in enumerate(french):
    # The following code implements a non-monotone decoding
    # algorithm (one that incorporates swapping in the target phrases).
    # Hence all hypotheses in stacks[i] represent translations of 
    # any i words of the input sentence.
    hypothesis = namedtuple("hypothesis", "logprob, lm_state, predecessor, phrase, bitmap, last_on_bit")
    initial_hypothesis = hypothesis(0.0, lm.begin(), None, None, [0]*len(f), None)
    print("Sentence " + str(num))
    stacks = [{} for _ in f] + [{}]
    stacks[0][lm.begin()] = initial_hypothesis
    for i, stack in enumerate(stacks[:-1]):
        for h in sorted(stack.itervalues(),key=lambda h: -h.logprob)[:opts.s]: # prune, used to be opts.s
            possible_options = get_possible_options(f, h)
            for (phrase, start, end, last_on_bit) in possible_options:
                logprob = h.logprob + phrase.logprob
                lm_state = h.lm_state
                for word in phrase.english.split():
                    (lm_state, word_logprob) = lm.score(lm_state, word)
                    logprob += word_logprob
                new_bitmap = h.bitmap[:]
                for x in range(start, end+1):
                    new_bitmap[x] = 1
                num_translated_words = new_bitmap.count(1)
                logprob += lm.end(lm_state) if num_translated_words == len(f) else 0.0
                new_hypothesis = hypothesis(logprob, lm_state, h, phrase, new_bitmap, last_on_bit)
                if lm_state not in stacks[num_translated_words] or stacks[num_translated_words][lm_state].logprob < logprob: # second case is recombination
                    stacks[num_translated_words][lm_state] = new_hypothesis 
    winner = max(stacks[-1].itervalues(), key=lambda h: h.logprob)
    def extract_english(h): 
        return "" if h.predecessor is None else "%s%s " % (extract_english(h.predecessor), h.phrase.english)
    print extract_english(winner)

    if opts.verbose:
        def extract_tm_logprob(h):
            return 0.0 if h.predecessor is None else h.phrase.logprob + extract_tm_logprob(h.predecessor)
        tm_logprob = extract_tm_logprob(winner)
        sys.stderr.write("LM = %f, TM = %f, Total = %f\n" % (winner.logprob - tm_logprob, tm_logprob, winner.logprob))


        
