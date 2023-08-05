#!/usr/bin/env python

'''
Automatically generate Beaker Notebook plots for Elasticsearch responses by
extracting metrics from documents and aggregations.
'''

from collections import defaultdict
from itertools import cycle
import re

import dateutil

from matplotlib import cm
from random import random


class ESPlot():

    _topic_cache = {}

    sep = '.'

    def __init__(self, search,
                 document_key='@timestamp',
                 xaxis_type='time',
                 yaxis_type='linear'):

        self.xaxis_type = xaxis_type
        self.yaxis_type = yaxis_type

        self.cmap = cm.get_cmap('Set1')
        self._color_cycle = cycle(range(1, self.cmap.N))

        self.plot_data = []
        self.metric_data = defaultdict(list)
        self.element_types = {}

        self.search = search

        self.response = search.execute()

        response = self.response.to_dict()

        for doc in response['hits']['hits']:
            key = doc.get(document_key, doc.get('_source', {}).get(document_key))
            if key is None:
                continue
            if isinstance(key, str):
                key = int(dateutil.parser.parse(key).timestamp() * 1000)
            for i in doc:
                if i in [document_key]:
                    continue
                self.process_metric(i, key, doc[i])

        if 'aggregations' in response:
            for key, value in response['aggregations'].items():
                self.process_aggregation(key, value)

        for k, v in self.metric_data.items():
            self.add_elements(k, v)

    def process_aggregation(self, name, data):
        assert 'buckets' in data
        for bucket in data['buckets']:
            self.process_bucket(name, bucket)

    def process_bucket(self, name, bucket, key=None):

        if isinstance(bucket['key'], str):
            bucket_key = key
            bucket_name = self.join(name, bucket['key'])
        else:
            bucket_key = bucket['key']
            bucket_name = name

        for member in bucket:
            if member in ['key', 'key_as_string']:
                continue
            if isinstance(bucket[member], dict) and 'buckets' in bucket[member]:
                for i in bucket[member]['buckets']:
                    self.process_bucket(self.join(bucket_name, member), i, bucket_key)
            elif bucket_key:
                self.process_metric(self.join(bucket_name, member), bucket_key, bucket[member])

    def process_metric(self, name, key, value):
        if isinstance(value, dict):
            if value.keys() == set(['upper', 'lower']):
                if name not in self.element_types:
                    self.element_types[name] = 'stem'
                self.metric_data[name].append({
                    'x': key, 'y': value['lower'], 'y2': value['upper']
                })
            else:
                for metric, value in value.items():
                    if metric in ['value_as_string']:
                        continue
                    self.process_metric(self.join(name, metric), key, value)
        else:
            self.metric_data[name].append({'x': key, 'y': value})

    def add_elements(self, legend, elements, **kwargs):
        ret = {
            'type': self.element_types.get(legend, 'line'),
            'legend': legend,
            'elements': elements,
        }
        ret.update(kwargs)
        if ret['type'] in ('stem', 'bar') and 'width' not in ret and len(elements) > 1:
            ret['width'] = elements[1]['x'] - elements[0]['x']
        if 'color' not in ret:
            ret['color'] = self.next_color()
        self.plot_data.append(ret)

    def join(self, *args):
        return self.sep.join([args[0]] + [i.replace(self.sep, '%%%x' % ord(self.sep)) for i in args[1:]])

    @staticmethod
    def rgb_to_hex(rgb):
        return '#%02x%02x%02x' % tuple(int(i * 256) for i in rgb[:3])

    def next_color(self):
        return self.rgb_to_hex(self.cmap(random()))

    @staticmethod
    def translate(pat):
        i, n = 0, len(pat)
        res = ''
        while i < n:
            c = pat[i]
            i = i+1
            if c == '*':
                res = res + '[^.]*'
            elif c == '#':
                res = res + '.*'
            else:
                res = res + re.escape(c)
        return res + '$\Z(?ms)'

    def topic_match(self, name, pat):
        _cache = self._topic_cache
        try:
            re_pat = _cache[pat]
        except KeyError:
            res = self.translate(pat)
            if len(_cache) >= 100:
                _cache.clear()
            _cache[pat] = re_pat = re.compile(res)
        return re_pat.match(name) is not None

    def show(self, only=None, exclude=None, **kwargs):

        data = self.plot_data

        if only:
            if isinstance(only, str):
                only = [only]
            data = [
                i for i in data
                if any([self.topic_match(i['legend'], j) for j in only])
            ]

        if exclude:
            if isinstance(exclude, str):
                exclude = [exclude]
            data = [
                i for i in data
                if not any([self.topic_match(i['legend'], j) for j in exclude])
            ]

        data.sort(key=lambda x: x['legend'])

        ret = {
            'type': 'Plot',
            'xAxis': {'type': 'time'},
            'useToolTip': True,
            'showLegend': True,
            'data': data,
        }
        ret.update(kwargs)

        return ret
