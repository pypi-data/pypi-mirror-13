#!/usr/bin/env python
"""
Nuke Filewalker
===============

Nuke Filewalker is a simple file indexer that takes blobs of text from
files and tokenizes these blobs into words and can keep track of the most
encountered words (along with how many time each word occurs) across all
text files that it indexes.

This module can also act as a standalone script.

usage: file_indexer.py [-h] [-c COUNT] [filepaths [filepaths ...]]

A command-line program that indexes multiple plain text files and prints the
most enountered words and the number of times each word was encountered.

positional arguments:
  filepaths             Paths to files to be indexed.

optional arguments:
  -h, --help            show this help message and exit
  -c COUNT, --count COUNT
                        The number of most encountered words to print.


@author: Eeshan Garg <jerryguitarist@gmail.com>
"""
from __future__ import print_function

import re
import argparse
from collections import Counter


class FileIndexer(object):
    """
    Provides an interface for indexing multiple plain text files and
    tokenizing the text into words and for getting the most enountered
    words along with how many times each was encountered.

    @ivar filepaths: List of paths to or names of files to be indexed.
    @type filepaths: C{list} of C{str}

    @ivar regex: The regular expression pattern to use when tokenizing
        a blob of text into words. This is passed as an argument to
        C{re.findall}. The default pattern is '\w+', which is equivalent
        to the set [a-zA-Z0-9_].
    @type regex: C{str}

    @ivar words: The list that is extended as blobs of text are tokenized
        into words. This list ends up containing all the words in all the
        files that are being indexed.
    @type words: C{list}
    """
    def __init__(self, filepaths, regex='\w+'):
        self.filepaths = filepaths
        self.regex = regex
        self.words = []

    def start_indexing(self):
        """
        Read all the files and tokenize their text into words and
        accumulate all the words in a list.
        """
        for filepath in self.filepaths:
            with open(filepath) as fp:
                blob = fp.read()
                self.words.extend(self.tokenize(blob))

    def tokenize(self, blob):
        """
        Tokenize a blob of text using a regular expression pattern.
        The default pattern assumes that words are delimited by any
        character except a-z, A-Z, 0-9.

        @param blob: The blob of text to tokenize, usually read from
            a plain text file.
        @type blob: C{str}

        @return: All the words across all text files being indexed.
        @rtype: C{list}
        """
        # since the text is to be treated in a case-insensitive
        # manner, we can convert all the text to lowercase
        return re.findall(self.regex, blob.lower())

    def most_encountered_words(self, count=10):
        """
        Returns the most encountered words across all the files indexed
        so far along with a count of how many times each word occurs
        (highest to lowest).

        @param count: Optional keyword argument specifying how many of
            the most encountered words and their counts should be returned
            in the order from highest to lowest. For example, with a default
            value of 10, the top 10 most encountered words and their counts
            would be returned.
        @type count: C{int}

        @return: Most encountered words and their counts, a C{list} of
            C{tuple} in the form of (word, count) such as ('the', 234).
        @rtype: C{list} of C{tuple}
        """
        return Counter(self.words).most_common(count)


def parse_args():
    """
    Parse command-line arguments.

    @return: The command line arguments.
    @rtype: C{argparse.Namespace}
    """
    parser = argparse.ArgumentParser(
        description=(
         'A command-line program that indexes multiple plain text files and '
         'prints the most enountered words and the number of times '
         'each word was encountered.'
        )
    )
    parser.add_argument('filepaths', nargs='*',
                        help='Paths to files to be indexed.')
    parser.add_argument('-c', '--count', type=int, default=10,
                        help='The number of most encountered words to print.')
    args = parser.parse_args()
    return args


def main():
    args = parse_args()
    indexer = FileIndexer(args.filepaths)
    indexer.start_indexing()
    words = indexer.most_encountered_words(args.count)
    for word, count in words:
        print("{} - {}".format(word, count))


if __name__ == "__main__":
    main()
