# -*- coding: utf-8 -*-

"""Read and write ARTS XML types

This module provides functionality for reading and writing ARTS XML files.

"""

from __future__ import absolute_import

import gzip

from . import read
from . import write

__all__ = ['load', 'save']


def save(var, filename, precision='.7e'):
    """Save a variable to an ARTS XML file.

    Args:
        var: Variable to be stored.
        filename (str): Name of output XML file.
            If the name ends in .gz, the file is compressed on the fly.
        precision (str): Format for output precision.

    Note:
        Python's gzip library is extremely slow in writing. Consider
        compressing files manually after writing them normally.

    Example:
        >>> x = numpy.array([1.,2.,3.])
        >>> typhon.arts.xml.save(x, 'myvector.xml')

    """
    if filename[:-3] == '.gz':
        xmlopen = gzip.open
    else:
        xmlopen = open
    with xmlopen(filename, mode='w', encoding='UTF-8') as fp:
        axw = write.ARTSXMLWriter(fp, precision=precision)
        axw.write_header()
        axw.write_xml(var)
        axw.write_footer()


def load(filename):
    """Load a variable from an ARTS XML file.

    The input file can be either a plain or gzipped XML file

    Args:
        filename (str): Name of ARTS XML file.

    Returns:
        Data from the XML file. Type depends on data in file.

    """
    if filename[-3:] == '.gz':
        xmlopen = gzip.open
    else:
        xmlopen = open

    with xmlopen(filename, 'rb') as fp:
        return read.parse(fp).getroot().value()
