# -*- coding: utf-8 -*-
#
# This file is part of refextract.
# Copyright (C) 2005, 2006, 2007, 2008, 2009, 2010, 2011, 2013, 2014, 2015, 2016 CERN.
#
# refextract is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# refextract is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with refextract; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.
#
# In applying this license, CERN does not waive the privileges and immunities
# granted to it by virtue of its status as an Intergovernmental Organization
# or submit itself to any jurisdiction.

"""This is where all the public API calls are accessible to extract references.

There are 4 API functions available to extract from PDF file, string or URL. In
addition, there is an API call to return a parsed journal reference structure
from a raw string.
"""


import os
import requests

from tempfile import mkstemp

from .engine import (get_kbs,
                     get_plaintext_document_body,
                     parse_reference_line,
                     parse_references,
                     parse_tagged_reference_line)
from .errors import FullTextNotAvailable
from .find import (find_numeration_in_body,
                   get_reference_section_beginning)
from .tag import tag_reference_line
from .text import extract_references_from_fulltext, rebuild_reference_lines


def extract_references_from_url(url, headers=None, chunk_size=1024, **kwargs):
    """Extract references from the pdf specified in the url.

    The first parameter is the path to the file
    It raises FullTextNotAvailable if the file does not exist.

    The standard reference format is: {title} {volume} ({year}) {page}.

    E.g. you can change that by passing the reference_format:

    >>> extract_references_from_url(path, reference_format="{title},{volume},{page}")

    If you want to also link each reference to some other resource (like a record),
    you can provide a linker_callback function to be executed for every reference
    element found.

    To override KBs for journal names etc., use ``override_kbs_files``:

    >>> extract_references_from_url(path, override_kbs_files={'journals': 'my/path/to.kb'})

    It raises FullTextNotAvailable if the url gives a 404
    """
    # Get temporary filepath to download to
    filename, filepath = mkstemp(
        suffix="_{0}".format(os.path.basename(url)),
    )
    os.close(filename)

    req = requests.get(
        url=url,
        headers=headers,
        stream=True
    )
    if req.status_code == 200:
        with open(filepath, 'wb') as f:
            for chunk in req.iter_content(chunk_size):
                f.write(chunk)

    try:
        try:
            references = extract_references_from_file(filepath, **kwargs)
        except IOError as err:
            if err.code == 404:
                raise FullTextNotAvailable()
            else:
                raise
    finally:
        os.remove(filepath)
    return references


def extract_references_from_file(path,
                                 recid=None,
                                 reference_format="{title} {volume} ({year}) {page}",
                                 linker_callback=None,
                                 override_kbs_files=None):
    """Extract references from a local pdf file.

    The first parameter is the path to the file
    It raises FullTextNotAvailable if the file does not exist.

    The standard reference format is: {title} {volume} ({year}) {page}.

    E.g. you can change that by passing the reference_format:

    >>> extract_references_from_file(path, reference_format="{title},{volume},{page}")

    If you want to also link each reference to some other resource (like a record),
    you can provide a linker_callback function to be executed for every reference
    element found.

    To override KBs for journal names etc., use ``override_kbs_files``:

    >>> extract_references_from_file(path, override_kbs_files={'journals': 'my/path/to.kb'})

    Returns a dictionary with extracted references and stats.
    """
    if not os.path.isfile(path):
        raise FullTextNotAvailable()

    docbody, dummy = get_plaintext_document_body(path)
    reflines, dummy, dummy = extract_references_from_fulltext(docbody)
    if not len(reflines):
        docbody, dummy = get_plaintext_document_body(path, keep_layout=True)
        reflines, dummy, dummy = extract_references_from_fulltext(docbody)

    return parse_references(
        reflines,
        recid=recid,
        reference_format=reference_format,
        linker_callback=linker_callback,
        override_kbs_files=override_kbs_files,
    )


def extract_references_from_string(source,
                                   is_only_references=True,
                                   recid=None,
                                   reference_format="{title} {volume} ({year}) {page}",
                                   linker_callback=None,
                                   override_kbs_files=None):
    """Extract references from a raw string.

    The first parameter is the path to the file
    It raises FullTextNotAvailable if the file does not exist.

    If the string does not only contain references, improve accuracy by
    specifing ``is_only_references=False``.

    The standard reference format is: {title} {volume} ({year}) {page}.

    E.g. you can change that by passing the reference_format:

    >>> extract_references_from_url(path, reference_format="{title},{volume},{page}")

    If you want to also link each reference to some other resource (like a record),
    you can provide a linker_callback function to be executed for every reference
    element found.

    To override KBs for journal names etc., use ``override_kbs_files``:

    >>> extract_references_from_url(path, override_kbs_files={'journals': 'my/path/to.kb'})
    """
    docbody = source.split('\n')
    if not is_only_references:
        reflines, dummy, dummy = extract_references_from_fulltext(docbody)
    else:
        refs_info = get_reference_section_beginning(docbody)
        if not refs_info:
            refs_info, dummy = find_numeration_in_body(docbody)
            refs_info['start_line'] = 0
            refs_info['end_line'] = len(docbody) - 1,

        reflines = rebuild_reference_lines(
            docbody, refs_info['marker_pattern'])
    return parse_references(
        reflines,
        recid=recid,
        reference_format=reference_format,
        linker_callback=linker_callback,
        override_kbs_files=override_kbs_files,
    )


def extract_journal_reference(line, override_kbs_files=None):
    """Extract the journal reference from string.

    Extracts the journal reference from string and parses for specific
    journal information.
    """
    tagged_line = tag_reference_line(
        line, get_kbs(custom_kbs_files=override_kbs_files), {}
    )[0]
    if tagged_line is None:
        return None

    elements, dummy_marker, dummy_stats = parse_tagged_reference_line(
        '', tagged_line, [], [])

    for element in elements:
        if element['type'] == 'JOURNAL':
            return element
