"""
Tests for nuke_filewalker.FileIndexer
"""

import unittest

from nukefilewalker.indexer import FileIndexer


class IndexerTestCase(unittest.TestCase):
    """
    Tests for nuke_filewalker.FileIndexer
    """
    def setUp(self):
        self.indexer = FileIndexer(['tests/testfile1.txt', 'tests/testfile2.txt'])

    def test_tokenize(self):
        """
        FileIndexer.tokenize should tokenize a blob of text into words.
        """
        with open('tests/testfile1.txt') as fp:
            blob = fp.read()
            self.assertEqual(self.indexer.tokenize(blob), [
                'i', 'am', 'beginning', 'to', 'feel', 'like', 'a', 'rap',
                'god', 'rap', 'god', 'all', 'my', 'people', 'from', 'the',
                'front', 'to', 'the', 'back', 'nod', 'back', 'nod', 'now',
                'who', 'thinks', 'their', 'arms', 'are', 'long', 'enough',
                'to', 'slap', 'box', 'slap', 'box', 'they', 'said', 'i',
                'rap', 'like', 'a', 'robot', 'so', 'call', 'me', 'rap', 'bot'
            ])

    def test_start_indexing(self):
        """
        FileIndexer.start_indexing should index multiple files and store all
        the words in a list.
        """
        self.indexer.start_indexing()
        self.assertEqual(self.indexer.words, [
            'i', 'am', 'beginning', 'to', 'feel', 'like', 'a', 'rap',
            'god', 'rap', 'god', 'all', 'my', 'people', 'from', 'the',
            'front', 'to', 'the', 'back', 'nod', 'back', 'nod', 'now',
            'who', 'thinks', 'their', 'arms', 'are', 'long', 'enough',
            'to', 'slap', 'box', 'slap', 'box', 'they', 'said', 'i',
            'rap', 'like', 'a', 'robot', 'so', 'call', 'me', 'rap', 'bot',
            'i', 'am', 'a', 'space', 'bound', 'rocket', 'ship', 'and',
            'your', 'heart', 'is', 'the', 'moon', 'and', 'i', 'am', 'aiming',
            'right', 'at', 'you', 'right', 'at', 'you', 'two', 'hundred',
            'fifty', 'thousand', 'miles', 'on', 'a', 'clear', 'night', 'in',
            'june', 'and', 'i', 'am', 'aiming', 'right', 'at', 'you',
            'right', 'at', 'you', 'right', 'at', 'you'
        ])

    def test_most_encountered_words_default_count(self):
        """
        FileIndexer.most_encountered_words called without a parameter
        should return the top 10 most common words across all the files
        being indexed.
        """
        self.indexer.start_indexing()
        self.assertEqual(self.indexer.most_encountered_words(), [
            ('right', 5), ('you', 5), ('i', 5), ('at', 5), ('am', 4),
            ('rap', 4), ('a', 4), ('and', 3), ('to', 3), ('the', 3),
        ])

    def test_most_encountered_words_new_count(self):
        """
        FileIndexer.most_encountered_words should return the specified
        number of most common words when called with a parameter for
        count.
        """
        self.indexer.start_indexing()
        self.assertEqual(self.indexer.most_encountered_words(5), [
            ('right', 5), ('you', 5), ('i', 5), ('at', 5), ('am', 4)
        ])
