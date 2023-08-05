#!/usr/bin/env python
# coding=utf-8

"""
A structure describing the properties of a text file.
"""

from __future__ import absolute_import
from __future__ import print_function
from bs4 import BeautifulSoup
import io
import re

from aeneas.idsortingalgorithm import IDSortingAlgorithm
from aeneas.logger import Logger
import aeneas.globalconstants as gc
import aeneas.globalfunctions as gf

__author__ = "Alberto Pettarin"
__copyright__ = """
    Copyright 2012-2013, Alberto Pettarin (www.albertopettarin.it)
    Copyright 2013-2015, ReadBeyond Srl   (www.readbeyond.it)
    Copyright 2015-2016, Alberto Pettarin (www.albertopettarin.it)
    """
__license__ = "GNU AGPL v3"
__version__ = "1.4.0"
__email__ = "aeneas@readbeyond.it"
__status__ = "Production"

class TextFileFormat(object):
    """
    Enumeration of the supported formats for text files.
    """

    SUBTITLES = "subtitles"
    """
    The text file contains the fragments,
    each fragment is contained in one or more consecutive lines,
    separated by (at least) a blank line,
    without explicitly-assigned identifiers.
    Use this format if you want to output to SRT/TTML/VTT
    and you want to keep multilines in the output file::

        Fragment on a single row

        Fragment on two rows
        because it is quite long

        Another one liner

        Another fragment
        on two rows

    """

    PARSED = "parsed"
    """
    The text file contains the fragments,
    one per line, with the syntax ``id|text``,
    where `id` is a non-empty fragment identifier
    and `text` is the text of the fragment::

        f001|Text of the first fragment
        f002|Text of the second fragment
        f003|Text of the third fragment

    """

    PLAIN = "plain"
    """
    The text file contains the fragments,
    one per line, without explicitly-assigned identifiers::

        Text of the first fragment
        Text of the second fragment
        Text of the third fragment

    """

    UNPARSED = "unparsed"
    """
    The text file is a well-formed HTML/XHTML file,
    where the text fragments have already been marked up.

    The text fragments will be extracted by matching
    the ``id`` and/or ``class`` attributes of each elements
    with the provided regular expressions::

        <?xml version="1.0" encoding="UTF-8"?>
        <html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" lang="en" xml:lang="en">
         <head>
          <meta charset="utf-8"/>
          <meta name="viewport" content="width=768,height=1024"/>
          <link rel="stylesheet" href="../Styles/style.css" type="text/css"/>
          <title>Sonnet I</title>
         </head>
         <body>
          <div id="divTitle">
           <h1><span class="ra" id="f001">I</span></h1>
          </div>
          <div id="divSonnet">
           <p>
            <span class="ra" id="f002">From fairest creatures we desire increase,</span><br/>
            <span class="ra" id="f003">That thereby beauty’s rose might never die,</span><br/>
            <span class="ra" id="f004">But as the riper should by time decease,</span><br/>
            <span class="ra" id="f005">His tender heir might bear his memory:</span><br/>
            <span class="ra" id="f006">But thou contracted to thine own bright eyes,</span><br/>
            <span class="ra" id="f007">Feed’st thy light’s flame with self-substantial fuel,</span><br/>
            <span class="ra" id="f008">Making a famine where abundance lies,</span><br/>
            <span class="ra" id="f009">Thy self thy foe, to thy sweet self too cruel:</span><br/>
            <span class="ra" id="f010">Thou that art now the world’s fresh ornament,</span><br/>
            <span class="ra" id="f011">And only herald to the gaudy spring,</span><br/>
            <span class="ra" id="f012">Within thine own bud buriest thy content,</span><br/>
            <span class="ra" id="f013">And tender churl mak’st waste in niggarding:</span><br/>
            <span class="ra" id="f014">Pity the world, or else this glutton be,</span><br/>
            <span class="ra" id="f015">To eat the world’s due, by the grave and thee.</span>
           </p>
          </div>
         </body>
        </html>

    """

    ALLOWED_VALUES = [SUBTITLES, PARSED, PLAIN, UNPARSED]
    """ List of all the allowed values """



class TextFragment(object):
    """
    A text fragment.

    Note: internally, all the text objects are Unicode strings.

    :param identifier: the identifier of the fragment
    :type  identifier: Unicode string
    :param language: the language of the text of the fragment
    :type  language: :class:`aeneas.language.Language` enum
    :param lines: the lines in which text is split up
    :type  lines: list of Unicode strings
    :param filtered_lines: the lines in which text is split up,
                           possibly filtered for the alignment purpose
    :type  filtered_lines: list of Unicode strings

    :raise TypeError: if ``identifier`` is not a Unicode string
    :raise TypeError: if ``lines`` is not an instance of ``list`` or
                      it contains an element which is not a Unicode string
    """

    TAG = u"TextFragment"

    def __init__(
            self,
            identifier=None,
            language=None,
            lines=None,
            filtered_lines=None
    ):
        self.identifier = identifier
        self.language = language
        self.lines = lines
        self.filtered_lines = filtered_lines

    def __len__(self):
        if self.lines is None:
            return 0
        return len(self.lines)

    def __unicode__(self):
        return u"%s %s" % (self.identifier, self.text)

    def __str__(self):
        return gf.safe_str(self.__unicode__())

    @property
    def chars(self):
        """
        Return the number of characters of the text fragment,
        not including the line separators.

        :rtype: int
        """
        return sum([len(line) for line in self.lines])

    @property
    def identifier(self):
        """
        The identifier of the text fragment.

        :rtype: Unicode string
        """
        return self.__identifier
    @identifier.setter
    def identifier(self, identifier):
        if (identifier is not None) and (not gf.is_unicode(identifier)):
            raise TypeError("identifier is not a Unicode string")
        self.__identifier = identifier

    @property
    def language(self):
        """
        The language of the text fragment.

        :rtype: :class:`aeneas.language.Language` enum
        """
        return self.__language
    @language.setter
    def language(self, language):
        # NOTE disabling this check to allow for language codes not listed in Language
        #if (language is not None) and (language not in Language.ALLOWED_VALUES):
        #    raise ValueError("language value is not allowed")
        self.__language = language

    @property
    def lines(self):
        """
        The lines of the text fragment.

        :rtype: list of Unicode strings
        """
        return self.__lines
    @lines.setter
    def lines(self, lines):
        if lines is not None:
            if not isinstance(lines, list):
                raise TypeError("lines is not an instance of list")
            for line in lines:
                if not gf.is_unicode(line):
                    raise TypeError("lines contains an element which is not a Unicode string")
        self.__lines = lines

    @property
    def text(self):
        """
        The text of the text fragment.

        :rtype: Unicode string
        """
        return u" ".join(self.lines)

    @property
    def characters(self):
        """
        The number of characters in this text fragment.

        :rtype: int
        """
        return len(self.text)

    @property
    def filtered_text(self):
        """
        The filtered text of the text fragment.

        :rtype: Unicode string
        """
        return u" ".join(self.filtered_lines)

    @property
    def filtered_characters(self):
        """
        The number of filtered characters in this text fragment.

        :rtype: int
        """
        return len(self.filtered_text)



class TextFile(object):
    """
    A list of text fragments.

    Note: internally, all the text objects are Unicode strings.

    :param file_path: the path to the text file.
                      If not ``None`` (and also ``file_format`` is not ``None``),
                      the file will be read immediately.
    :type  file_path: string (path)
    :param file_format: the format of the text file
    :type  file_format: :class:`aeneas.textfile.TextFileFormat` enum
    :param parameters: additional parameters used to parse the text file
    :type  parameters: dict
    :param logger: the logger object
    :type  logger: :class:`aeneas.logger.Logger`

    :raise OSError: if ``file_path`` cannot be read
    :raise TypeError: if ``parameters`` is not an instance of ``dict``
    :raise ValueError: if ``file_format`` value is not allowed
    """

    DEFAULT_ID_FORMAT = u"f%06d"

    TAG = u"TextFile"

    def __init__(
            self,
            file_path=None,
            file_format=None,
            parameters=None,
            logger=None
        ):
        self.file_path = file_path
        self.file_format = file_format
        self.parameters = parameters
        self.fragments = []
        self.logger = Logger()
        if logger is not None:
            self.logger = logger
        if self.parameters is None:
            self.parameters = {}
        if (self.file_path is not None) and (self.file_format is not None):
            self._read_from_file()

    def __len__(self):
        return len(self.fragments)

    def __unicode__(self):
        return u"\n".join([f.__unicode__() for f in self.fragments])

    def __str__(self):
        return gf.safe_str(self.__unicode__())

    def _log(self, message, severity=Logger.DEBUG):
        """ Log """
        self.logger.log(message, severity, self.TAG)

    @property
    def chars(self):
        """
        Return the number of characters of the text file,
        not counting line or fragment separators.

        :rtype: int
        """
        return sum([fragment.chars for fragment in self.fragments])

    @property
    def file_path(self):
        """
        The path of the text file.

        :rtype: string (path)
        """
        return self.__file_path
    @file_path.setter
    def file_path(self, file_path):
        if (file_path is not None) and (not gf.file_can_be_read(file_path)):
            raise OSError("Text file '%s' cannot be read" % file_path)
        self.__file_path = file_path

    @property
    def file_format(self):
        """
        The format of the text file.

        :rtype: :class:`aeneas.textfile.TextFileFormat` enum
        """
        return self.__file_format
    @file_format.setter
    def file_format(self, file_format):
        if (file_format is not None) and (file_format not in TextFileFormat.ALLOWED_VALUES):
            raise ValueError("Text file format '%s' is not allowed" % file_format)
        self.__file_format = file_format

    @property
    def parameters(self):
        """
        Additional parameters used to parse the text file.

        :rtype: dict
        """
        return self.__parameters
    @parameters.setter
    def parameters(self, parameters):
        if (parameters is not None) and (not isinstance(parameters, dict)):
            raise TypeError("parameters is not an instance of dict")
        self.__parameters = parameters

    @property
    def characters(self):
        """
        The number of characters in this text.

        :rtype: int
        """
        chars = 0
        for fragment in self.fragments:
            chars += fragment.characters
        return chars

    @property
    def fragments(self):
        """
        The current list of text fragments.

        :rtype: list of :class:`aeneas.textfile.TextFragment`
        """
        return self.__fragments
    @fragments.setter
    def fragments(self, fragments):
        if fragments is not None:
            if not isinstance(fragments, list):
                raise TypeError("fragments is not an instance of list")
            for fragment in fragments:
                if not isinstance(fragment, TextFragment):
                    raise TypeError("fragments contains an element which is not an instance of TextFragment")
        self.__fragments = fragments

    def append_fragment(self, fragment):
        """
        Append the given text fragment to the current list.

        :param fragment: the text fragment to be appended
        :type  fragment: :class:`aeneas.textfile.TextFragment`
        """
        self.fragments.append(fragment)

    def get_slice(self, start=None, end=None):
        """
        Return a new list of text fragments,
        indexed from start (included) to end (excluded).

        :param start: the start index
        :type  start: int
        :param end: the end index
        :type  end: int
        :rtype: :class:`aeneas.textfile.TextFile`
        """
        if start is not None:
            start = min(max(0, start), len(self) - 1)
        else:
            start = 0
        if end is not None:
            end = min(max(0, end), len(self))
            end = max(end, start + 1)
        else:
            end = len(self)
        new_text = TextFile()
        for fragment in self.fragments[start:end]:
            new_text.append_fragment(fragment)
        return new_text

    def set_language(self, language):
        """
        Set the given language for all the text fragments.

        :param language: the language of the text fragments
        :type  language: :class:`aeneas.language.Language` enum
        """
        self._log([u"Setting language: '%s'", language])
        for fragment in self.fragments:
            fragment.language = language

    def clear(self):
        """
        Clear the list of text fragments.
        """
        self._log(u"Clearing text fragments")
        self.fragments = []

    def read_from_list(self, lines):
        """
        Read text fragments from a given list of strings::

            [fragment_1, fragment_2, ..., fragment_n]

        :param lines: the text fragments
        :type  lines: list of strings
        """
        self._log(u"Reading text fragments from list")
        self._read_plain(lines)

    def read_from_list_with_ids(self, lines):
        """
        Read text fragments from a given list of tuples::

            [(id_1, text_1), (id_2, text_2), ..., (id_n, text_n)].

        :param lines: the list of ``[id, text]`` fragments (see above)
        :type  lines: list of tuples (see above)
        """
        self._log(u"Reading text fragments from list with ids")
        self._create_text_fragments([(line[0], [line[1]]) for line in lines])

    def _read_from_file(self):
        """
        Read text fragments from file.
        """
        # test if we can read the given file
        if not gf.file_can_be_read(self.file_path):
            self._log([u"File '%s' cannot be read", self.file_path], Logger.CRITICAL)
            raise OSError("Input file cannot be read")

        if self.file_format not in TextFileFormat.ALLOWED_VALUES:
            self._log([u"Text file format '%s' is not supported.", self.file_format], Logger.CRITICAL)
            raise ValueError("Text file format not supported")

        # read the contents of the file
        self._log([u"Reading contents of file '%s'", self.file_path])
        with io.open(self.file_path, "r", encoding="utf-8") as text_file:
            lines = text_file.readlines()

        # clear text fragments
        self.clear()

        # parse the contents
        map_read_function = {
            TextFileFormat.SUBTITLES: self._read_subtitles,
            TextFileFormat.PARSED: self._read_parsed,
            TextFileFormat.PLAIN: self._read_plain,
            TextFileFormat.UNPARSED: self._read_unparsed
        }
        map_read_function[self.file_format](lines)

        # log the number of fragments
        self._log([u"Parsed %d fragments", len(self.fragments)])

    def _read_subtitles(self, lines):
        """
        Read text fragments from a subtitles format text file.

        :param lines: the lines of the subtitles text file
        :type  lines: list of strings

        :raise ValueError: if the id regex is not valid
        """
        self._log(u"Parsing fragments from subtitles text format")
        id_format = self._get_id_format()
        lines = [line.strip() for line in lines]
        pairs = []
        i = 1
        current = 0
        while current < len(lines):
            line_text = lines[current]
            if len(line_text) > 0:
                fragment_lines = [line_text]
                following = current + 1
                while (following < len(lines)) and (len(lines[following]) > 0):
                    fragment_lines.append(lines[following])
                    following += 1
                identifier = id_format % i
                pairs.append((identifier, fragment_lines))
                current = following
                i += 1
            current += 1
        self._create_text_fragments(pairs)

    def _read_parsed(self, lines):
        """
        Read text fragments from a parsed format text file.

        :param lines: the lines of the parsed text file
        :type  lines: list of strings
        :param parameters: additional parameters for parsing
                           (e.g., class/id regex strings)
        :type  parameters: dict
        """
        self._log(u"Parsing fragments from parsed text format")
        pairs = []
        for line in lines:
            pieces = line.split(gc.PARSED_TEXT_SEPARATOR)
            if len(pieces) == 2:
                identifier = pieces[0].strip()
                text = pieces[1].strip()
                if len(identifier) > 0:
                    pairs.append((identifier, [text]))
        self._create_text_fragments(pairs)

    def _read_plain(self, lines):
        """
        Read text fragments from a plain format text file.

        :param lines: the lines of the plain text file
        :type  lines: list of strings
        :param parameters: additional parameters for parsing
                           (e.g., class/id regex strings)
        :type  parameters: dict

        :raise ValueError: if the id regex is not valid
        """
        self._log(u"Parsing fragments from plain text format")
        id_format = self._get_id_format()
        lines = [line.strip() for line in lines]
        pairs = []
        i = 1
        for line in lines:
            identifier = id_format % i
            text = line.strip()
            pairs.append((identifier, [text]))
            i += 1
        self._create_text_fragments(pairs)

    def _read_unparsed(self, lines):
        """
        Read text fragments from an unparsed format text file.

        :param lines: the lines of the unparsed text file
        :type  lines: list of strings
        """
        def filter_attributes():
            """ Return a dict with the bs4 filter parameters """
            attributes = {}
            for attribute_name, filter_name in [
                    ("class", gc.PPN_JOB_IS_TEXT_UNPARSED_CLASS_REGEX),
                    ("id", gc.PPN_JOB_IS_TEXT_UNPARSED_ID_REGEX)
            ]:
                if filter_name in self.parameters:
                    regex_string = self.parameters[filter_name]
                    if regex_string is not None:
                        self._log([u"Regex for %s: '%s'", attribute_name, regex_string])
                        regex = re.compile(r".*\b" + regex_string + r"\b.*")
                        attributes[attribute_name] = regex
            return attributes
        #
        # TODO better and/or parametric parsing,
        #      for example, removing tags but keeping text, etc.
        #
        self._log(u"Parsing fragments from unparsed text format")

        # transform text in a soup object
        self._log(u"Creating soup")
        soup = BeautifulSoup("\n".join(lines), "lxml")

        # extract according to class_regex and id_regex
        text_from_id = {}
        ids = []
        filter_attributes = filter_attributes()
        self._log([u"Finding elements matching attributes '%s'", filter_attributes])
        nodes = soup.findAll(attrs=filter_attributes)
        for node in nodes:
            try:
                f_id = gf.safe_unicode(node["id"])
                f_text = gf.safe_unicode(node.text)
                text_from_id[f_id] = f_text
                ids.append(f_id)
            except KeyError:
                self._log(u"KeyError while parsing a node", Logger.WARNING)

        # sort by ID as requested
        id_sort = gf.safe_get(
            dictionary=self.parameters,
            key=gc.PPN_JOB_IS_TEXT_UNPARSED_ID_SORT,
            default_value=IDSortingAlgorithm.UNSORTED,
            can_return_none=False
        )
        self._log([u"Sorting text fragments using '%s'", id_sort])
        sorted_ids = IDSortingAlgorithm(id_sort).sort(ids)

        # append to fragments
        self._log(u"Appending fragments")
        self._create_text_fragments([(key, [text_from_id[key]]) for key in sorted_ids])

    def _get_id_format(self):
        """ Return the id regex from the parameters"""
        id_format = gf.safe_get(
            self.parameters,
            gc.PPN_TASK_OS_FILE_ID_REGEX,
            self.DEFAULT_ID_FORMAT,
            can_return_none=False
        )
        try:
            identifier = id_format % 1
        except (TypeError, ValueError):
            self._log([u"String '%s' is not a valid id format", id_format], Logger.WARNING)
            raise ValueError("String '%s' is not a valid id format" % id_format)
        return id_format

    def _create_text_fragments(self, pairs):
        """
        Create text fragment objects and append them to this list.

        :param pairs: a list of pairs, each pair being (id, [line_1, ..., line_n])
        :type  pairs: list of tuples (see above)
        """
        self._log(u"Creating TextFragment objects")
        text_filter = self._build_text_filter()
        for pair in pairs:
            self.append_fragment(
                TextFragment(
                    identifier=pair[0],
                    lines=pair[1],
                    filtered_lines=text_filter.apply_filter(pair[1])
                )
            )

    def _build_text_filter(self):
        """
        Build a suitable TextFilter object.
        """
        text_filter = TextFilter(logger=self.logger)
        self._log(u"Created TextFilter object")
        for key, cls, param_name in [
                (
                    gc.PPN_TASK_IS_TEXT_FILE_IGNORE_REGEX,
                    TextFilterIgnoreRegex,
                    "regex"
                ),
                (
                    gc.PPN_TASK_IS_TEXT_FILE_TRANSLITERATE_MAP,
                    TextFilterTransliterate,
                    "map_file_path"
                )
        ]:
            cls_name = cls.__name__
            param_value = gf.safe_get(self.parameters, key, None)
            if param_value is not None:
                self._log([u"Creating %s object...", cls_name])
                params = {
                    param_name : param_value,
                    "logger" : self.logger
                }
                try:
                    inner_filter = cls(**params)
                    text_filter.append(inner_filter)
                    self._log([u"Creating %s object... done", cls_name])
                    print("HERE")
                except ValueError:
                    self._log([u"Creating %s object... failed", cls_name], Logger.WARNING)
        return text_filter



class TextFilter(object):
    """
    A text filter is a function acting on a list of strings,
    and returning a new list of strings derived from the former
    (with the same number of elements).

    For example, a filter might apply a regex to the input string,
    or it might transliterate its characters.

    Filters can be chained.

    Note: internally, all the text objects are Unicode strings.

    :param logger: the logger object
    :type  logger: :class:`aeneas.logger.Logger`
    """

    TAG = u"TextFilter"

    SPACES_REGEX = re.compile(" [ ]+")

    def __init__(self, logger=None):
        self.filters = []
        self.logger = Logger()
        if logger is not None:
            self.logger = logger

    def _log(self, message, severity=Logger.DEBUG):
        """ Log """
        self.logger.log(message, severity, self.TAG)

    def append(self, new_filter):
        """
        Append (to the right) a new filter to this filter.

        :param new_filter: the filter to be appended
        :type  new_filter: :class:`aeneas.textfile.TextFilter`
        """
        self.filters.append(new_filter)

    def apply_filter(self, strings):
        """
        Apply the text filter filter to the given list of strings.

        :param strings: the list of input strings
        :type  strings: list of Unicode strings
        """
        result = strings
        for filt in self.filters:
            result = filt.apply_filter(result)
        self._log([u"Applying regex: '%s' => '%s'", strings, result])
        return result



class TextFilterIgnoreRegex(TextFilter):
    """
    Delete the text matching the given regex.

    Leading/trailing spaces, and repeated spaces are removed.

    :param regex: the regular expression to be applied
    :type  regex: regex
    :param logger: the logger object
    :type  logger: :class:`aeneas.logger.Logger`

    :raise ValueError: if ``regex`` is not a valid regex
    """

    TAG = u"TextFilterIgnoreRegex"

    def __init__(self, regex, logger=None):
        try:
            self.regex = re.compile(regex)
        except:
            raise ValueError("String '%s' is not a valid regular expression" % regex)
        TextFilter.__init__(self, logger)

    def apply_filter(self, strings):
        return [self._apply_single(s) for s in strings]

    def _apply_single(self, string):
        """ Apply filter to single string """
        if string is None:
            return None
        result = self.regex.sub("", string)
        result = self.SPACES_REGEX.sub(" ", result).strip()
        return result



class TextFilterTransliterate(TextFilter):
    """
    Transliterate the text using the given map file.

    Leading/trailing spaces, and repeated spaces are removed.

    :param map_object: the map object
    :type  map_object: :class:`aeneas.textfile.TransliterationMap`
    :param map_file_path: the path to a map file
    :type  map_file_path: str (path)
    :param logger: the logger object
    :type  logger: :class:`aeneas.logger.Logger`

    :raise OSError: if ``map_file_path`` cannot be read
    :raise TypeError: if ``map_object`` is not an instance
                      of :class:`aeneas.textfile.TransliterationMap`
    """

    TAG = u"TextFilterTransliterate"

    def __init__(self, map_file_path=None, map_object=None, logger=None):
        if map_object is not None:
            if not isinstance(map_object, TransliterationMap):
                raise TypeError("map_object is not an instance of TransliterationMap")
            self.trans_map = map_object
        elif map_file_path is not None:
            self.trans_map = TransliterationMap(
                file_path=map_file_path,
                logger=logger
            )
        TextFilter.__init__(self, logger)

    def apply_filter(self, strings):
        return [self._apply_single(s) for s in strings]

    def _apply_single(self, string):
        """ Apply filter to single string """
        if string is None:
            return None
        result = self.trans_map.transliterate(string)
        result = self.SPACES_REGEX.sub(u" ", result).strip()
        return result



class TransliterationMap(object):
    """
    A transliteration map is a dictionary that maps Unicode characters
    to their equivalent Unicode characters or strings (character sequences).
    If a character is unmapped, its image is the character itself.
    If a character is mapped to the empty string, it will be deleted.
    Otherwise, a character will be replaced with the associated string.

    For its format, please read the initial comment
    included at the top of the ``transliteration.map`` sample file.

    :param file_path: the path to the map file to be read
    :type  file_path: str (path)
    :param logger: the logger object
    :type  logger: :class:`aeneas.logger.Logger`

    :raise OSError: if ``file_path`` cannot be read
    """

    TAG = u"TransliterationMap"

    CODEPOINT_REGEX = re.compile(r"U\+([0-9A-Fa-f]+)")
    DELETE_REGEX = re.compile(r"^([^ ]+)$")
    REPLACE_REGEX = re.compile(r"^([^ ]+) ([^ ]+)$")

    def __init__(self, file_path, logger=None):
        self.trans_map = {}
        self.logger = Logger()
        if logger is not None:
            self.logger = logger
        self.file_path = file_path

    def _log(self, message, severity=Logger.DEBUG):
        """ Log """
        self.logger.log(message, severity, self.TAG)

    @property
    def file_path(self):
        """
        The path of the map file.

        :rtype: string (path)
        """
        return self.__file_path
    @file_path.setter
    def file_path(self, file_path):
        if (file_path is not None) and (not gf.file_can_be_read(file_path)):
            raise OSError("Map file '%s' cannot be read" % file_path)
        self.__file_path = file_path
        self._build_map()

    def transliterate(self, string):
        result = []
        for char in string:
            try:
                result.append(self.trans_map[char])
            except:
                result.append(char)
        result = u"".join(result)
        return result

    def _build_map(self):
        """
        Read the map file at path.
        """
        self.trans_map = {}
        with io.open(self.file_path, "r", encoding="utf-8") as file_obj:
            contents = file_obj.read().replace(u"\t", u" ")
            for line in contents.splitlines():
                # ignore lines starting with "#" or blank (after stripping)
                if not line.startswith(u"#"):
                    line = line.strip()
                    if len(line) > 0:
                        self._process_map_rule(line)

    def _process_map_rule(self, line):
        """
        Process the line string containing a map rule.
        """
        result = self.REPLACE_REGEX.match(line)
        if result is not None:
            what = self._process_first_group(result.group(1))
            replacement = self._process_second_group(result.group(2))
            for char in what:
                self.trans_map[char] = replacement
                self._log([u"Adding rule: replace '%s' with '%s'", char, replacement])
        else:
            result = self.DELETE_REGEX.match(line)
            if result is not None:
                what = self._process_first_group(result.group(1))
                for char in what:
                    self.trans_map[char] = ""
                    self._log([u"Adding rule: delete '%s'", char])

    def _process_first_group(self, group):
        """
        Process the first group of a rule.
        """
        if "-" in group:
            # range
            if len(group.split("-")) == 2:
                arr = group.split("-")
                start = self._parse_codepoint(arr[0])
                end = self._parse_codepoint(arr[1])
        else:
            # single char/U+xxxx
            start = self._parse_codepoint(group)
            end = start
        result = []
        if (start > -1) and (end >= start):
            for index in range(start, end + 1):
                result.append(gf.safe_unichr(index))
        return result

    def _process_second_group(self, group):
        """
        Process the second group of a (replace) rule.
        """
        def _replace_codepoint(match):
            """
            Replace the matched Unicode hex code
            with the corresponding unicode character
            """
            result = self._match_to_int(match)
            if result == -1:
                return u""
            return gf.safe_unichr(result)
        result = group
        try:
            result = re.sub(self.CODEPOINT_REGEX, _replace_codepoint, result)
        except:
            pass
        return result

    def _parse_codepoint(self, string):
        """
        Parse the given string, either a Unicode character or U+....,
        and return the corresponding Unicode code point as int.
        """
        if len(string) > 1:
            match = self.CODEPOINT_REGEX.match(string)
            return self._match_to_int(match)
        elif len(string) == 1:
            return self._unichr_to_int(string)
        return -1

    @classmethod
    def _match_to_int(cls, match):
        """
        Convert to int the first group of the match,
        representing the hex number in CODEPOINT_REGEX
        (e.g., 12AB in U+12AB).
        """
        try:
            return int(match.group(1), 16)
        except:
            pass
        return -1

    @classmethod
    def _unichr_to_int(cls, char):
        """
        Convert to int the given character.
        """
        try:
            return ord(char)
        except:
            pass
        return -1



