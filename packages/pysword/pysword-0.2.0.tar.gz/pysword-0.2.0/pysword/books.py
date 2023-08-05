###############################################################################
# PySword - A native Python reader of the SWORD Project Bible Modules         #
# --------------------------------------------------------------------------- #
# Copyright (c) 2008-2015 Various developers:                                 #
# Kenneth Arnold, Joshua Gross, Ryan Hiebert, Matthew Wardrop, Tomas Groth    #
# --------------------------------------------------------------------------- #
# This program is free software; you can redistribute it and/or modify it     #
# under the terms of the GNU General Public License as published by the Free  #
# Software Foundation; version 2 of the License.                              #
#                                                                             #
# This program is distributed in the hope that it will be useful, but WITHOUT #
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or       #
# FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for    #
# more details.                                                               #
#                                                                             #
# You should have received a copy of the GNU General Public License along     #
# with this program; if not, write to the Free Software Foundation, Inc., 59  #
# Temple Place, Suite 330, Boston, MA 02111-1307 USA                          #
###############################################################################

from pysword.canons import *


class BookStructure(object):
    def __init__(self, name, osis_name, preferred_abbreviation, chapter_lengths):
        """
        :param name: Full English name of book
        :param osis_name: Abbreviation of book
        :param preferred_abbreviation: Preferred abbreviation of book
        :param chapter_lengths: List containing the number of verses for each chapter.
        """
        self.name = name
        self.osis_name = osis_name
        self.preferred_abbreviation = preferred_abbreviation
        self.chapter_lengths = chapter_lengths
        self.num_chapters = len(chapter_lengths)

    def __repr__(self):
        return u'Book(%s)' % self.name

    def name_matches(self, name):
        """
        Check if a name matches the name of this book.
        :param name: The name to match
        :return: True if matching else False
        """
        name = name.lower()
        return name in [self.name.lower(), self.osis_name.lower(), self.preferred_abbreviation.lower()]

    def chapter_offset(self, chapter_index):
        """
        Get offset based on chapter
        :param chapter_index: The chapter index to calculate from.
        :return: The calculated offset.
        """
        # Add chapter lengths to this point; plus 1 for every chapter title; plus 1 for book title
        return sum(self.chapter_lengths[:chapter_index]) + (chapter_index + 1) + 1

    def get_indicies(self, chapters=None, verses=None, offset=0):
        """
        Get indicies for given chapter(s) and verse(s).
        :param chapters: Single chapter number or an array of chapter numbers
        :param verses: Single verse number or an array of verse numbers
        :param offset: The offset to used for this book when reading from file.
        :return: An array of indicies.
        """
        if chapters is None:
            chapters = list(range(1, self.num_chapters+1))
        elif isinstance(chapters, int):
            chapters = [chapters]
        if len(chapters) != 1:
            verses = None
        elif isinstance(verses, int):
            verses = [verses]

        refs = []
        for chapter in chapters:
            if verses is None:
                tmp_verses = list(range(1, self.chapter_lengths[chapter-1]+1))
            else:
                tmp_verses = verses
            refs.extend([offset + self.chapter_offset(chapter-1) + verse-1 for verse in tmp_verses])
        return refs

    @property
    def size(self):
        """
        Size of book.
        """
        # Total verses + chapter heading for each chapter + 1 for book title
        return sum(self.chapter_lengths) + len(self.chapter_lengths) + 1


class BibleStructure(object):

    def __init__(self, versification):
        """
        Initialize structure based on the versification.
        :param versification: The versification to use.
        """
        self._section_order = [u'ot', u'nt']
        self._book_offsets = None  # offsets within sections

        self._books = {
            u'ot': [],
            u'nt': [],
        }
        # Find the canon used. The canons are original defined in SWORD header files.
        canon = default
        if versification == u'catholic2':
            canon = catholic2
        elif versification == u'german':
            canon = german
        elif versification == u'kjva':
            canon = kjva
        elif versification == u'leningrad':
            canon = leningrad
        elif versification == u'luther':
            canon = luther
        elif versification == u'lxx':
            canon = lxx
        elif versification == u'mt':
            canon = mt
        elif versification == u'nrsva':
            canon = nrsva
        elif versification == u'nrsv':
            canon = nrsv
        elif versification == u'orthodox':
            canon = orthodox
        elif versification == u'synodal':
            canon = synodal
        elif versification == u'synodalprot':
            canon = synodalprot
        elif versification == u'vulg':
            canon = vulg
        # Based on the canon create the BookStructure objects needed
        for book in canon[u'ot']:
            self._books[u'ot'].append(BookStructure(*book))
        for book in canon[u'nt']:
            self._books[u'nt'].append(BookStructure(*book))

    def _update_book_offsets(self):
        """
        Compute index offsets and add other data
        """
        # FIXME: this is still a little hairy.
        self._book_offsets = {}
        for testament, books in self._books.items():
            idx = 2  # start after the testament heading
            for book in books:
                self._book_offsets[book.name] = idx
                offset = 1  # start after the book heading
                idx += book.size

    def _book_offset(self, book_name):
        """
        Find offset for the given book
        :param book_name: Name of book to find offset for
        :return: The offset
        """
        if self._book_offsets is None:
            self._update_book_offsets()
        return self._book_offsets[book_name]

    def find_book(self, name):
        """
        Find book
        :param name: The book to find
        :return: A tuple of the testament the book is in ('ot' or 'nt') and a BookStructure object.
        :raise ValueError: If the book is not in this BibleStructure.
        """
        name = name.lower()
        for testament, books in self._books.items():
            for num, book in enumerate(books):
                if book.name_matches(name):
                    return testament, book
        raise ValueError("Book name \'%s\' does not exist in BibleStructure." % name)

    def ref_to_indicies(self, books=None, chapters=None, verses=None):
        """
        Get references to indicies for given book(s), chapter(s) and verse(s).
        :param books: Single book name or an array of book names
        :param chapters: Single chapter number or an array of chapter numbers
        :param verses: Single verse number or an array of verse numbers
        :return:
        """
        # TODO: CHECK NOT OVERSPECIFIED
        if books is None:
            # Return all books
            books = []
            for section in self._books:
                books.extend([b.name for b in self._books[section]])
        elif isinstance(books, str):
            books = [books]

        refs = {}
        for book in books:
            testament, book = self.find_book(book)
            if testament not in refs:
                refs[testament] = []
            refs[testament].extend(book.get_indicies(chapters=chapters, verses=verses,
                                                     offset=self._book_offset(book.name)))
            # Deal with the one book presented.
        return refs

    def get_books(self):
        """
        Return the bookstructure for this bible.
        :return: book structure
        """
        return self._books
