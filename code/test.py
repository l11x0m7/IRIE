#!/usr/bin/env python
# coding=utf-8
import json

with open('../data/pagerank.json') as fr:
    data = fr.readlines()[0].strip()
    data = json.loads(data)
    for l,r in data.iteritems():
        print l + '\t' + json.dumps(r)
