# -*- encoding: utf-8 -*-
from __future__ import unicode_literals, division, \
                       absolute_import, print_function
import bs4
from .logger import logger

# UnicodeDammit was refactored a lot recently.
# It now falls back on cchardet if it’s in the path.
# Otherwise, we have to make sure that it does *not* fall back on
# chardet as it is slow and has only minimal charset coverage.
if not 'cchardet' in bs4.dammit.__dict__:
    # Either chardet or nothing
    bs4.dammit.chardet_dammit = lambda string: None

def intelligent_decode(markup, override_encodings=None, is_html=False):
    """ One problem remains in the latest version of UnicodeDammit, namely
        that pages that have beautifully declared encodings but contain one
        small erroneous byte sequence somewhere will fail to be decoded with
        the mostly correct encodings, while Windows-1252 somehow succeeds, but
        completely mucks up all umlauts and ligatures. Hence I want to remove
        Windows-1252 from the potential encodings.

        I don’t fall back on cchardet just yet.
    """
    detector = bs4.dammit.EncodingDetector(markup, override_encodings, is_html)
    detector.declared_encoding = \
        detector.find_declared_encoding(markup, is_html)
    # Fall back on forcing it to UTF-8 only if no other encodings
    # could be found. (I use override_encodings for the HTTP encoding,
    # which seems at least less reliable to me than the declared encoding.)
    potential_encodings = \
        filter(bool, [detector.sniffed_encoding, detector.declared_encoding]
                     + list(detector.override_encodings)) \
        or ['utf-8']
    contains_replacement_characters = False
    tried_encodings = []
    unicode_markup = None
    original_encoding = None
    for encoding in potential_encodings:
        tried_encodings.append(encoding)
        try:
            unicode_markup = detector.markup.decode(encoding)
        except Exception as excp:
            logger.info('Unsuccessfully tried encoding %s: %r', encoding, excp)
        if unicode_markup is not None:
            original_encoding = encoding
            break
    if unicode_markup is None:
        for encoding in potential_encodings:
            try:
                unicode_markup = detector.markup.decode(encoding, 'replace')
            except Exception as excp:
                logger.info('Unsuccessfully tried forcing encoding %s: %r',
                            encoding, excp)
            if unicode_markup is not None:
                original_encoding = encoding
                contains_replacement_characters = True
                break
    if unicode_markup is None:
        # Whatever!
        unicode_markup = detector.markup.decode('utf-8', 'replace')
        original_encoding = 'utf-8'
        contains_replacement_characters = True
    return type(b'MockDammit', (object,), {
        'contains_replacement_characters': contains_replacement_characters,
        'original_encoding': original_encoding,
        'detector': detector,
        'is_html': detector.is_html,
        'markup': detector.markup,
        'tried_encodings': tried_encodings,
        'unicode_markup': unicode_markup})

def intelligent_detect_encoding(markup, is_html=False):
    """ Don’t use this function at this time.
    """
    chardet_dammit = bs4.dammit.chardet_dammit
    bs4.dammit.chardet_dammit = lambda string: None
    dammit = bs4.dammit.UnicodeDammit(markup, is_html=is_html)
    bs4.dammit.chardet_dammit = chardet_dammit
    if dammit.contains_replacement_characters:
        return None
    return dammit.original_encoding
