# Python script to generate single Google-style analogy file
# from BATS dataset

import sys
import codecs
import os

def analogiesFrom(f):
    # read in the word pairs
    word_pairs = []
    with codecs.open(f, 'r', 'utf-8') as stream:
        for line in stream:
            (w1, w2) = [s.strip() for s in line.split()]
            word_pairs.append((w1, w2))
        
    # cross them to form analogies
    # (no self-crossing)
    analogies = []
    for i in range(len(word_pairs)):
        (a, b) = word_pairs[i]
        for j in range(len(word_pairs)):
            if j == i: pass
            else:
                (c, d) = word_pairs[j]
                analogies.append((a,b,c,d))

    return analogies


if len(sys.argv) != 3:
    print("Usage: generate_single_BATS_file.py BATS_DIR OUTF")
    exit()
else:
    bats_dir = sys.argv[1]
    outfile = sys.argv[2]
    supersets = [
        '1_Inflectional_morphology',
        '2_Derivational_morphology',
        '3_Encyclopedic_semantics',
        '4_Lexicographic_semantics'
    ]

    with codecs.open(outfile, 'w', 'utf-8') as stream:
        for superset in supersets:
            files = os.listdir(os.path.join(bats_dir, superset))
            for fname in files:
                stream.write(': %s\n' % os.path.splitext(fname)[0])
                analogies = analogiesFrom(os.path.join(bats_dir, superset, fname))
                for analogy in analogies:
                    stream.write('%s %s %s %s\n' % analogy)
