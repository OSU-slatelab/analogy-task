#!/bin/bash

PY=python3

${PY} -m experiment \
    --dataset Google \
    --predictions-file data/logs/Google.w2v_GoogleNews.predictions \
    -l data/logs/Google.w2v_GoogleNews.log
