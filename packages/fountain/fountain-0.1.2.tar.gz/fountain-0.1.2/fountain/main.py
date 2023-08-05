#!/usr/bin/env python3

import codecs
import json
import re
import sys

slug = re.compile(r'^(?P<IntExt>\.|INT\b\.?|EXT\b\.?|EST\b\.?|INT\./EXT\b\.?|INT/EXT\b\.?|I/E\.?)(?P<rest>.*\w)', re.I | re.L)
transition = re.compile(r'(?P<transition>.*TO):\s*$')
transition_forced = re.compile(r'^>\s*(?P<transition>[^:]+):?\s*$')
titles = re.compile(r'(^[\w ]+:)', re.LOCALE|re.MULTILINE|re.DOTALL)

place_specifier = {
    'int': 'int',
    'int.': 'int',
    'ext': 'ext',
    'ext.': 'ext',
    'est': 'ext',
    'est.': 'ext',
    'int.ext': 'intext',
    'int.ext.': 'intext',
    'int/ext': 'intext',
    'int/ext.': 'intext',
    'i/e': 'intext',
    'i/e.': 'intext',
    'ext.int': 'extint',
    'ext.int.': 'extint',
    'ext/int': 'exint',
    'ext/int.': 'extint',
    'e/i': 'extint',
    'e/i.': 'extint',
}

class Fountain():

    tokens = []

    def process_token(self, token, is_first_token=False):
        def process_titlepage(token):
            title_page = "".join(token['lines'])
            elements = [e.strip() for e in titles.split(title_page) if e.strip()]

            if len(elements) < 2:
                return False

            i = iter(elements)
            title_map = dict(list(zip(i, i)))
            normalized_titles = {}
            keys = [(k, k.lower()[:-1]) for k in list(title_map.keys())]
            for k in keys:
                normalized_titles[k[1]] = title_map[k[0]]

            token['title-fields']  = normalized_titles

            return True

        def process_slugline(token):
            if len(token['lines']) != 1: return False
            line = token['lines'][0]
            match = slug.match(line)
            if not match: return False

            if line.startswith("."):
                token['forced'] = True
                token['description'] = line[1:].strip().upper()
            else:
                prefix = match.group('IntExt').lower()
                token['place'] = place_specifier[prefix]
                elements = match.group('rest').rsplit('-', 1)
                token['location'] = elements[0].strip().upper()
                try:
                    token['time'] = elements[1].strip().upper()
                except:
                    pass

            return True

        def process_dialogue(token):
            first_line = token['lines'][0]
            if len(token['lines']) < 2: return False
            if not first_line.isupper(): return False

            token['character'] = first_line.strip()
            token['text'] = [l.strip() for l in token['lines'][1:]]

            return True

        def process_transition(token):
            if len(token['lines']) != 1: return False
            line = token['lines'][0]
            forced_match = transition_forced.search(line)
            match = transition.search(line)
            if forced_match:
                token['transition'] = forced_match.group('transition').strip().upper()
                return True
            elif match:
                token['transition'] = match.group('transition').strip().upper()
                return True
            return False

        if process_slugline(token): token['type'] = 'slugline'
        elif process_dialogue(token): token['type'] = 'dialogue'
        elif process_transition(token): token['type'] = 'transition'
        elif is_first_token and process_titlepage(token): token['type'] = 'titles'
        else: token['type'] = 'action'

    def tokenize(self, f):
        tokens = []
        current_token = None
        is_first_token = True

        for line in f:
            if not line or line.isspace():
                if current_token:
                    self.process_token(current_token, is_first_token)
                    is_first_token = False
                    tokens.append(current_token)
                current_token = None
            else:
                if not current_token:
                    current_token = { 'lines': [] }
                current_token['lines'].append(line)

        if current_token:
            self.process_token(current_token, is_first_token)
            is_first_token = False
            tokens.append(current_token)

        self.tokens = tokens
        return tokens
