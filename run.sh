#!/bin/bash
#
# Sample script for running analogy completion experiment.
#
# By default, uses the embeddings file configured in config.ini
# and evaluates on the Google analogy test set.
#
# Default embeddings are a subset of the 300-dimensional
# GoogleNews skip-gram word embeddings, filtered to only the words
# used in the Google analogy set.
# They will produce a macro accuracy of 81.3%, with macro
# MAP and MRR of 53.3%.
#
# Requires having run ./setup.sh first.

if [ ! -e dependencies/pyconfig.sh ]; then
    echo "Please run ./setup.sh before running this script!"
    exit
else
    source dependencies/pyconfig.sh
fi

${PY} -m experiment \
    --dataset Google \
    --predictions-file data/logs/Google.w2v_GoogleNews.predictions \
    -l data/logs/Google.w2v_GoogleNews.log
