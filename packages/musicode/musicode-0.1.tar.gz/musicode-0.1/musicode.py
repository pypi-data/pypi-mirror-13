# -*- coding: utf-8 -*-

# musicode rocks \m/

default_header_keys = [
    'name',
    'singer',
    'composer',
    'arranger',
    'key',
    'play',
    'tempo',
    'time',
    'editor',
    'date',
]

default_bar_keys = [
    'notes',
    'chords',
    'durations',
]


def load(text):
    """
    Load music text to dict

    :param str text: music text
    :rtype: dict
    """
    data = load_header(text)
    body = load_body(text)
    bars = []

    for rows in body:
        if len(rows) == 2:
            bars.append({
                'notes': rows[0],
                'chords': [],
                'durations': rows[1]
            })
        elif len(rows) == 3:
            bars.append({
                'notes': rows[0],
                'chords': rows[1],
                'durations': rows[2]
            })

    data.update({'bars': bars})

    return data


def load_header(text):
    """
    Load header

    :param str text: music text
    :rtype: dict
    """
    header = {}

    for row in get_header(text):
        k, v = row.split(':', 2)
        header[k.strip()] = v.strip()

    return header


def load_body(text):
    """
    Load body

    :param str text: music text
    :rtype: list
    """
    body = []
    rows = []

    for row in get_body(text):
        rows.append(row.split())
        if row[0].isdigit() and int(row[0]) > 0:
            body.append(rows)
            rows = []

    return body


def dump(data, header_keys=None, bar_keys=None, separator=' '):
    """
    Dump data to music text

    :param dict data: music data
    :param list|tuple header_keys: specify header keys
    :param list|tuple bar_keys: specify bar keys
    :param str separator: notes separator, default ' '
    :return: music text
    """
    header = dump_header(data, header_keys)
    body = dump_body(data, bar_keys, separator)
    return header + '\n\n' + body


def dump_header(data, header_keys=None):
    """
    Dump data header to music text

    :param dict data: music data
    :param list|tuple header_keys: specify header keys
    :return: music header text
    """
    header = []

    header_keys = header_keys if header_keys else default_header_keys

    for key in header_keys:
        if key in data:
            header.append('%s: %s' % (key, data[key]))

    return '\n'.join(header)


def dump_body(data, bar_keys=None, separator=' '):
    """
    Dump data body to music text

    :param dict data: music data
    :param list|tuple bar_keys: specify bar keys
    :param str separator: notes separator, default ' '
    :return: music body text
    """
    body = []

    bar_keys = bar_keys if bar_keys else default_bar_keys

    for bar in data['bars']:
        rows = col_align([bar[key] for key in bar_keys if bar[key]])
        rows = [separator.join(row).rstrip() for row in rows]
        body.append('\n'.join(rows))

    return '\n\n'.join(body)


def col_align(rows, left=True):
    """
    2D list column align

    :param list|tuple rows: rows
    :param bool left: default True
    :rtype: list
    """
    cols = [list(c) for c in zip(*rows)]

    # Get max length for each column
    max_len = [max([len(item) for item in col]) for col in cols]

    # add space
    for i, col in enumerate(cols):
        for j, elem in enumerate(col):
            if left:
                col[j] += ' ' * (max_len[i] - len(elem))
            else:
                col[j] = ' ' * (max_len[i] - len(elem)) + col[j]

    return [list(r) for r in zip(*cols)]


def formats(text, header_keys=None, bar_keys=None, separator=' '):
    """
    Format music text

    :param str text: music text
    :param list|tuple header_keys: specify header keys
    :param list|tuple bar_keys: specify bar keys
    :param str separator: notes separator, default ' '
    :return: music text
    """
    return dump(load(text), header_keys, bar_keys, separator)


def get_header(text):
    """
    Get music text header

    :param str text: music text
    :return: header
    """
    rows = text.strip().split('\n')
    return [row.strip() for row in rows if ':' in row]


def get_body(text):
    """
    Get music text body

    :param str text: music text
    :return:
    """
    rows = [row.strip() for row in text.strip().split('\n')]
    return [row.title() for row in rows if row and ':' not in row]
