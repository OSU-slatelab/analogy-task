'''
Parser for generated single-file BATS analogy dataset
'''

import codecs
from lib import eval_mode
                
def _parseLine(line, multi_b, multi_d, to_lower=False):
    if to_lower:
        line = line.lower()
    (a,b,c,d) = [s.strip() for s in line.split()]
    b = b.split('/')
    d = d.split('/')
    if not multi_b:
        b = b[0]
    if not multi_d:
        d = d[0]
    return (a,b,c,d)

def read(analogy_file, setting, to_lower=False):
    multi_b = setting == eval_mode.ALL_INFO
    multi_d = setting in [eval_mode.ALL_INFO, eval_mode.MULTI_ANSWER]

    analogies = {}
    with codecs.open(analogy_file, 'r', 'utf-8') as stream:
        cur_relation, cur_analogies = None, []
        for line in stream:
            # relation separators
            if line[0] == ':':
                if cur_relation:
                    analogies[cur_relation] = cur_analogies
                cur_relation = line[2:].strip()
                cur_analogies = []
            # everything else is an analogy
            else:
                analogy = _parseLine(line, multi_b, multi_d, to_lower=to_lower)
                cur_analogies.append(analogy)
        analogies[cur_relation] = cur_analogies
    return analogies
