#!/usr/bin/env python3

import json
import re

document_template = """\documentclass{screenplay}[2012/06/30]
\\usepackage[utf8x]{inputenc}
\PrerenderUnicode{áéíóúÁÉÍÓÚÑñ¿¡üÜ}

%s

\\begin{document}

%s

\end{document}
"""

title_operators = {
  'title': r'\title{%s}'
, 'author': r'\author{%s}'
, 'address': r'\address{%s}'
, 'contact': r'\address{%s}'
, 'real author': r'\realauthor{%s}'
, 'agent': r'\agent{%s}'
,
}

slug_operators = {
  'exint': '\exintslug[%s]{%s}',
  'ext': '\extslug[%s]{%s}',
  'extint': '\extintslug[%s]{%s}',
  'int': '\intslug[%s]{%s}',
  'intext': '\intextslug[%s]{%s}'
}

transition_operator = r'\scflushright{%s\punctchar}'

dialog_operator = """
\\begin{dialogue}{%s}
%s
\\end{dialogue}
"""

def render_explicit_breaks(text):
    return re.sub(r'\n\s*', r'\\\\\n' ,text)

def render_underlines(text):
    return re.sub(r'_([^_]+)_', r'\\underline{\1}', text)

def render_paren(text):
    return re.sub(r'\(([^)]+)\)', r'\\paren{\1}', text)

def format_titles(token):
    results = []
    fields = token['title-fields']
    for k in fields:
        if k in title_operators:
            results.append(title_operators[k] %
                render_underlines(render_explicit_breaks(fields[k])))

    return "\n".join(results)

def format_slugline(token):
    if 'forced' in token:
        result = render_underlines(token['description'])
    else:
        time = ""
        place = token['place']
        location = render_underlines(token['location'])
        if 'time' in token:
            time = render_underlines(token['time'])

        result = slug_operators[place] % (time, location)

    return result

def format_action(token):
    result = render_underlines("".join(token['lines']))
    return result

def format_transition(token):
    result = render_underlines(transition_operator % token['transition'])
    return result

def format_dialogue(token):
    result = render_paren(dialog_operator % (token['character'], "\n".join(token['text'])))
    return result

token_formatter = {
    'action': format_action,
    'dialogue': format_dialogue,
    'slugline': format_slugline,
    'titles': format_titles,
    'transition': format_transition
}

def format_tokens(tokens):
    title = None
    body = []
    for t in tokens:
        token_type = t['type']
        result = token_formatter[token_type](t)
        if token_type == "titles":
            title = result
        else:
            body.append(result)

    title = title or ""
    if title:
        body.insert(0, '\coverpage')

    return document_template % (title, "\n\n".join(body))
