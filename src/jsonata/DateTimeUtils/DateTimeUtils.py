#
# Copyright Robert Yokota
#
# Licensed under the Apache License, Version 2.0 (the "License")
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# Derived from the following code:
#
#   Project name: jsonata-java
#   Copyright Dashjoin GmbH. https://dashjoin.com
#   Licensed under the Apache License, Version 2.0 (the "License")
#
#   Project name: JSONata4Java
#   (c) Copyright 2018, 2019 IBM Corporation
#   Licensed under the Apache License, Version 2.0 (the "License")
#   1 New Orchard Road,
#   Armonk, New York, 10504-1722
#   United States
#   +1 914 499 1900
#   support: Nathaniel Mills wnm3@us.ibm.com
#

import datetime
import functools
import logging
import math
import re
from collections import deque
from typing import Optional, Sequence

from src.jsonata.DateTimeUtils.Format import Format
from src.jsonata.DateTimeUtils.TCase import TCase
from src.jsonata.DateTimeUtils.MatcherPartTimeZone import MatcherPartTimeZone
from src.jsonata.DateTimeUtils.MatcherPartLookup import MatcherPartLookup
from src.jsonata.DateTimeUtils.MatcherPartLetters import MatcherPartLetters
from src.jsonata.DateTimeUtils.MatcherPartRoman import MatcherPartRoman
from src.jsonata.DateTimeUtils.MatcherPartDecimal import MatcherPartDecimal
from src.jsonata.DateTimeUtils.Formats import Formats
from src.jsonata.DateTimeUtils.PictureMatcher import PictureMatcher
from src.jsonata.Constants.Constants import Constants
from src.jsonata.DateTimeUtils.GroupingSeparator import GroupingSeparator
from src.jsonata.DateTimeUtils.MatcherPart import MatcherPart
from src.jsonata.DateTimeUtils.PictureFormat import PictureFormat
from src.jsonata.DateTimeUtils.SpecPart import SpecPart
from src.jsonata.DateTimeUtils.RomanNumeral import RomanNumeral
from src.jsonata.DateTimeUtils.YearMonth import YearMonth
from src.jsonata.Functions.Functions import Functions


class DateTimeUtils:
    """
    Utility functions for date and time manipulation in Jsonata Python implementation.
    """

    _few = [
        "Zero",
        "One",
        "Two",
        "Three",
        "Four",
        "Five",
        "Six",
        "Seven",
        "Eight",
        "Nine",
        "Ten",
        "Eleven",
        "Twelve",
        "Thirteen",
        "Fourteen",
        "Fifteen",
        "Sixteen",
        "Seventeen",
        "Eighteen",
        "Nineteen",
    ]
    _ordinals = [
        "Zeroth",
        "First",
        "Second",
        "Third",
        "Fourth",
        "Fifth",
        "Sixth",
        "Seventh",
        "Eighth",
        "Ninth",
        "Tenth",
        "Eleventh",
        "Twelfth",
        "Thirteenth",
        "Fourteenth",
        "Fifteenth",
        "Sixteenth",
        "Seventeenth",
        "Eighteenth",
        "Nineteenth",
    ]
    _decades = [
        "Twenty",
        "Thirty",
        "Forty",
        "Fifty",
        "Sixty",
        "Seventy",
        "Eighty",
        "Ninety",
        "Hundred",
    ]
    _magnitudes = ["Thousand", "Million", "Billion", "Trillion"]

    @staticmethod
    def number_to_words(value: int, ordinal: bool) -> str:
        """
        Convert a number to its word representation.
        Args:
            value (int): The number to convert.
            ordinal (bool): Whether to use ordinal form.
        Returns:
            str: Word representation of the number.
        """
        return DateTimeUtils._lookup(value, False, ordinal)

    @staticmethod
    def _lookup(num: int, prev: int, ordinal: bool) -> str:
        """
        Helper for number_to_words. Converts a number to words recursively.
        """
        if num <= 19:
            words = (" and " if prev else "") + (
                DateTimeUtils._ordinals[int(num)]
                if ordinal
                else DateTimeUtils._few[int(num)]
            )
        elif num < 100:
            tens = math.trunc(int(num) / float(10))
            remainder = int(math.fmod(int(num), 10))
            words = (" and " if prev else "") + DateTimeUtils._decades[tens - 2]
            if remainder > 0:
                words += "-" + DateTimeUtils._lookup(remainder, False, ordinal)
            elif ordinal:
                words = words[0 : len(words) - 1] + "ieth"
        elif num < 1000:
            hundreds = math.trunc(int(num) / float(100))
            remainder = int(math.fmod(int(num), 100))
            words = (", " if prev else "") + DateTimeUtils._few[hundreds] + " Hundred"
            if remainder > 0:
                words += DateTimeUtils._lookup(remainder, True, ordinal)
            elif ordinal:
                words += "th"
        else:
            mag = int(math.floor(math.log10(num) / 3))
            if mag > len(DateTimeUtils._magnitudes):
                mag = len(DateTimeUtils._magnitudes)  # the largest word
            factor = int(10 ** (mag * 3))
            mant = int(math.floor(math.trunc(num / float(factor))))
            remainder = num - mant * factor
            words = (
                (", " if prev else "")
                + DateTimeUtils._lookup(mant, False, False)
                + " "
                + str(DateTimeUtils._magnitudes[mag - 1])
            )
            if remainder > 0:
                words += DateTimeUtils._lookup(remainder, True, ordinal)
            elif ordinal:
                words += "th"
        return words

    _word_values = {}

    @staticmethod
    def _static_initializer():
        """
        Initializes word value mappings for number conversion.
        """
        i = 0
        while i < len(DateTimeUtils._few):
            DateTimeUtils._word_values[DateTimeUtils._few[i].casefold()] = i
            i += 1
        i = 0
        while i < len(DateTimeUtils._ordinals):
            DateTimeUtils._word_values[DateTimeUtils._ordinals[i].casefold()] = i
            i += 1
        i = 0
        while i < len(DateTimeUtils._decades):
            lword = DateTimeUtils._decades[i].casefold()
            DateTimeUtils._word_values[lword] = (i + 2) * 10
            DateTimeUtils._word_values[lword[0 : len(lword) - 1] + "ieth"] = (
                DateTimeUtils._word_values[lword]
            )
            i += 1
        DateTimeUtils._word_values["hundredth"] = 100
        DateTimeUtils._word_values["hundreth"] = 100
        i = 0
        while i < len(DateTimeUtils._magnitudes):
            lword = DateTimeUtils._magnitudes[i].casefold()
            val = int(10 ** ((i + 1) * 3))
            DateTimeUtils._word_values[lword] = val
            DateTimeUtils._word_values[lword + "th"] = val
            i += 1
        i = 0
        while i < len(DateTimeUtils._few):
            DateTimeUtils._word_values_long[DateTimeUtils._few[i].casefold()] = int(i)
            i += 1
        i = 0
        while i < len(DateTimeUtils._ordinals):
            DateTimeUtils._word_values_long[DateTimeUtils._ordinals[i].casefold()] = (
                int(i)
            )
            i += 1
        i = 0
        while i < len(DateTimeUtils._decades):
            lword = DateTimeUtils._decades[i].casefold()
            DateTimeUtils._word_values_long[lword] = int((i + 2)) * 10
            DateTimeUtils._word_values_long[lword[0 : len(lword) - 1] + "ieth"] = (
                DateTimeUtils._word_values_long[lword]
            )
            i += 1
        DateTimeUtils._word_values_long["hundredth"] = 100
        DateTimeUtils._word_values_long["hundreth"] = 100
        i = 0
        while i < len(DateTimeUtils._magnitudes):
            lword = DateTimeUtils._magnitudes[i].casefold()
            val = int(10 ** ((i + 1) * 3))
            DateTimeUtils._word_values_long[lword] = val
            DateTimeUtils._word_values_long[lword + "th"] = val
            i += 1

    _word_values_long = {}

    @staticmethod
    def words_to_number(text: str) -> int:
        """
        Convert a string of words to its numeric value.
        Args:
            text (str): The word string to convert.
        Returns:
            int: Numeric value.
        """
        parts = re.split(",\\s|\\sand\\s|[\\s\\-]", text)
        values = [DateTimeUtils._word_values[part] for i, part in enumerate(parts)]
        segs = deque()
        segs.append(0)
        for value in values:
            if value < 100:
                top = segs.pop()
                if top >= 1000:
                    segs.append(top)
                    top = 0
                segs.append(top + value)
            else:
                segs.append(segs.pop() * value)
        return sum(segs)

    #
    # long version of above
    #
    @staticmethod
    def words_to_long(text: str) -> int:
        """
        Convert a string of words to its long integer value.
        Args:
            text (str): The word string to convert.
        Returns:
            int: Long integer value.
        """
        parts = re.split(",\\s|\\sand\\s|[\\s\\-]", text)
        values = [DateTimeUtils._word_values_long[part] for i, part in enumerate(parts)]
        segs = deque()
        segs.append(int(0))
        for value in values:
            if value < 100:
                top = segs.pop()
                if top >= 1000:
                    segs.append(top)
                    top = int(0)
                segs.append(top + value)
            else:
                segs.append(segs.pop() * value)
        return sum(segs)

    @staticmethod
    def _create_roman_values() -> dict[str, int]:
        """
        Create mapping of Roman numeral characters to values.
        Returns:
            dict[str, int]: Roman numeral value mapping.
        """
        values = {"M": 1000, "D": 500, "C": 100, "L": 50, "X": 10, "V": 5, "I": 1}
        return values

    _roman_numerals = [
        RomanNumeral(1000, "m"),
        RomanNumeral(900, "cm"),
        RomanNumeral(500, "d"),
        RomanNumeral(400, "cd"),
        RomanNumeral(100, "c"),
        RomanNumeral(90, "xc"),
        RomanNumeral(50, "l"),
        RomanNumeral(40, "xl"),
        RomanNumeral(10, "x"),
        RomanNumeral(9, "ix"),
        RomanNumeral(5, "v"),
        RomanNumeral(4, "iv"),
        RomanNumeral(1, "i"),
    ]

    _roman_values = _create_roman_values.__func__()

    @staticmethod
    def _decimal_to_roman(value: int) -> str:
        """
        Convert a decimal integer to Roman numeral string.
        Args:
            value (int): The integer to convert.
        Returns:
            str: Roman numeral representation.
        """
        i = 0
        while i < len(DateTimeUtils._roman_numerals):
            numeral = DateTimeUtils._roman_numerals[i]
            if value >= numeral.get_value():
                return numeral.get_letters() + DateTimeUtils._decimal_to_roman(
                    value - numeral.get_value()
                )
            i += 1
        return ""

    @staticmethod
    def roman_to_decimal(roman: str) -> int:
        """
        Convert a Roman numeral string to decimal integer.
        Args:
            roman (str): Roman numeral string.
        Returns:
            int: Decimal value.
        """
        decimal_val = 0
        max_val = 1
        for digit in reversed(roman):
            value = DateTimeUtils._roman_values[digit]
            if value < max_val:
                decimal_val -= value
            else:
                max_val = value
                decimal_val += value
        return decimal_val

    @staticmethod
    def _decimal_to_letters(value: int, a_char: str) -> str:
        """
        Convert a decimal integer to alphabetic letters (A-Z).
        Args:
            value (int): The integer to convert.
            a_char (str): Base character ('A' or 'a').
        Returns:
            str: Letter representation.
        """
        letters = []
        a_code = a_char[0]
        while value > 0:
            letters.insert(0, chr((value - 1) % 26 + ord(a_code)))
            value = math.trunc((value - 1) / float(26))
        return "".join(letters)

    @staticmethod
    def format_integer(value: int, picture: Optional[str]) -> str:
        """
        Format an integer according to a picture specification.
        Args:
            value (int): The integer to format.
            picture (Optional[str]): The format picture.
        Returns:
            str: Formatted integer string.
        """
        fmt = DateTimeUtils._analyse_integer_picture(picture)
        return DateTimeUtils._format_integer(value, fmt)

    @staticmethod
    def parse_integer(value: Optional[str], picture: Optional[str]) -> Optional[int]:
        """
        Parse an integer from a string according to a picture specification.
        Args:
            value (Optional[str]): The string to parse.
            picture (Optional[str]): The format picture.
        Returns:
            Optional[int]: Parsed integer or None.
        """
        format_spec = DateTimeUtils._analyse_integer_picture(picture)
        match_spec = DateTimeUtils._generate_regex_with_component(None, format_spec)
        # //const fullRegex = '^' + matchSpec.regex + '$'
        # //const matcher = new RegExp(fullRegex)
        # // TODO validate input based on the matcher regex
        result = match_spec.parse(value)
        return result

    @staticmethod
    def _create_suffix_map() -> dict[str, str]:
        """
        Create a mapping for ordinal suffixes.
        Returns:
            dict[str, str]: Suffix mapping.
        """
        suffix = {"1": "st", "2": "nd", "3": "rd"}
        return suffix

    _suffix123 = _create_suffix_map.__func__()

    @staticmethod
    def _format_integer(value: int, fmt: Optional[Format]) -> str:
        """
        Format an integer using a Format object.
        Args:
            value (int): The integer to format.
            fmt (Optional[Format]): Format specification.
        Returns:
            str: Formatted integer string.
        """
        formatted_integer = ""
        negative = value < 0
        value = abs(value)
        if fmt.primary == Formats.LETTERS:
            formatted_integer = DateTimeUtils._decimal_to_letters(
                int(value),
                "A" if fmt.case_type == TCase.UPPER else "a",
            )
        elif format.primary == Formats.ROMAN:
            formatted_integer = DateTimeUtils._decimal_to_roman(int(value))
            if format.case_type == TCase.UPPER:
                formatted_integer = formatted_integer.upper()
        elif format.primary == Formats.WORDS:
            formatted_integer = DateTimeUtils.number_to_words(value, format.ordinal)
            if format.case_type == TCase.UPPER:
                formatted_integer = formatted_integer.upper()
            elif format.case_type == TCase.LOWER:
                formatted_integer = formatted_integer.casefold()
        elif format.primary == Formats.DECIMAL:
            formatted_integer = str(value)
            pad_length = format.mandatoryDigits - len(formatted_integer)
            if pad_length > 0:
                formatted_integer = Functions.left_pad(
                    formatted_integer, format.mandatoryDigits, "0"
                )
            if format.zeroCode != 0x30:
                chars = list(formatted_integer)
                i = 0
                while i < len(chars):
                    chars[i] = chr(ord(chars[i]) + format.zeroCode - 0x30)
                    i += 1
                formatted_integer = "".join(chars)
            if format.regular:
                n = int(
                    (len(formatted_integer) - 1) / format.groupingSeparators[0].position
                )
                for i in range(n, 0, -1):
                    pos = (
                        len(formatted_integer)
                        - i * format.groupingSeparators[0].position
                    )
                    formatted_integer = (
                        formatted_integer[0:pos]
                        + format.groupingSeparators[0].character
                        + formatted_integer[pos:]
                    )
            else:
                format.groupingSeparators.reverse()
                for separator in format.groupingSeparators:
                    pos = len(formatted_integer) - separator.position
                    formatted_integer = (
                        formatted_integer[0:pos]
                        + separator.character
                        + formatted_integer[pos:]
                    )

            if format.ordinal:
                last_digit = formatted_integer[len(formatted_integer) - 1 :]
                suffix = DateTimeUtils._suffix123.get(last_digit)
                if suffix is None or (
                    len(formatted_integer) > 1
                    and formatted_integer[len(formatted_integer) - 2] == "1"
                ):
                    suffix = "th"
                formatted_integer += suffix
        elif format.primary == Formats.SEQUENCE:
            raise RuntimeError(
                Constants.ERR_MSG_SEQUENCE_UNSUPPORTED.format(format.token)
            )
        if negative:
            formatted_integer = "-" + formatted_integer

        return formatted_integer

    _decimal_groups = [
        0x30,
        0x0660,
        0x06F0,
        0x07C0,
        0x0966,
        0x09E6,
        0x0A66,
        0x0AE6,
        0x0B66,
        0x0BE6,
        0x0C66,
        0x0CE6,
        0x0D66,
        0x0DE6,
        0x0E50,
        0x0ED0,
        0x0F20,
        0x1040,
        0x1090,
        0x17E0,
        0x1810,
        0x1946,
        0x19D0,
        0x1A80,
        0x1A90,
        0x1B50,
        0x1BB0,
        0x1C40,
        0x1C50,
        0xA620,
        0xA8D0,
        0xA900,
        0xA9D0,
        0xA9F0,
        0xAA50,
        0xABF0,
        0xFF10,
    ]

    @staticmethod
    def _analyse_integer_picture(picture: Optional[str]) -> Format:
        """
        Analyse an integer format picture and return a Format object.
        Args:
            picture (Optional[str]): The format picture.
        Returns:
            Format: Format specification object.
        """
        fmt = Format()
        primary_format = None
        format_modifier = None
        semicolon = picture.rfind(";")
        if semicolon == -1:
            primary_format = picture
        else:
            primary_format = picture[0:semicolon]
            format_modifier = picture[semicolon + 1 :]
            if format_modifier[0] == "o":
                fmt.ordinal = True

        if primary_format == "A":
            fmt.case_type = TCase.UPPER
            fmt.primary = Formats.LETTERS
        elif primary_format == "a":
            fmt.primary = Formats.LETTERS
        elif primary_format == "I":
            fmt.case_type = TCase.UPPER
            fmt.primary = Formats.ROMAN
        elif primary_format == "i":
            fmt.primary = Formats.ROMAN
        elif primary_format == "W":
            fmt.case_type = TCase.UPPER
            fmt.primary = Formats.WORDS
        elif primary_format == "Ww":
            fmt.case_type = TCase.TITLE
            fmt.primary = Formats.WORDS
        elif primary_format == "w":
            fmt.primary = Formats.WORDS
        else:
            zero_code = None
            mandatory_digits = 0
            optional_digits = 0
            grouping_separators = []
            separator_position = 0
            format_codepoints = list(primary_format)
            # ArrayUtils.reverse(format_codepoints)
            for code_point in reversed(format_codepoints):
                digit = False
                i = 0
                while i < len(DateTimeUtils._decimal_groups):
                    group = DateTimeUtils._decimal_groups[i]
                    if chr(group) <= code_point <= chr(group + 9):
                        digit = True
                        mandatory_digits += 1
                        separator_position += 1
                        if zero_code is None:
                            zero_code = group
                        elif group != zero_code:
                            raise RuntimeError(Constants.ERR_MSG_DIFF_DECIMAL_GROUP)
                        break
                    i += 1
                if not digit:
                    if code_point == chr(0x23):
                        separator_position += 1
                        optional_digits += 1
                    else:
                        grouping_separators.append(
                            GroupingSeparator(separator_position, code_point)
                        )
            if mandatory_digits > 0:
                fmt.primary = Formats.DECIMAL
                fmt.zeroCode = zero_code
                fmt.mandatoryDigits = mandatory_digits
                fmt.optionalDigits = optional_digits

                regular = DateTimeUtils._get_regular_repeat(grouping_separators)
                if regular > 0:
                    fmt.regular = True
                    fmt.groupingSeparators.append(
                        GroupingSeparator(regular, grouping_separators[0].character)
                    )
                else:
                    fmt.regular = False
                    fmt.groupingSeparators = grouping_separators
            else:
                fmt.primary = Formats.SEQUENCE
                fmt.token = primary_format

        return fmt

    @staticmethod
    def _get_regular_repeat(separators: Sequence["GroupingSeparator"]) -> int:
        """
        Determine if grouping separators repeat regularly.
        Args:
            separators (Sequence[GroupingSeparator]): List of separators.
        Returns:
            int: Repeat factor or 0 if not regular.
        """
        if not separators:
            return 0

        sep_char = separators[0].character
        for i in range(1, len(separators)):
            if separators[i].character is not sep_char:
                return 0

        indexes = [separator.position for separator in separators]
        factor = int(functools.reduce(math.gcd, indexes))
        for index in range(1, len(indexes) + 1):
            if (
                indexes.index(index * factor) if index * factor in indexes else -1
            ) == -1:
                return 0
        return factor

    @staticmethod
    def _create_default_presentation_modifiers() -> dict[str, str]:
        """
        Create default presentation modifiers for date/time components.
        Returns:
            dict[str, str]: Default modifiers mapping.
        """
        mapping = {
            "Y": "1",
            "M": "1",
            "D": "1",
            "d": "1",
            "F": "n",
            "W": "1",
            "w": "1",
            "X": "1",
            "x": "1",
            "H": "1",
            "h": "1",
            "P": "n",
            "m": "01",
            "s": "01",
            "f": "1",
            "Z": "01:01",
            "z": "01:01",
            "C": "n",
            "E": "n",
        }
        return mapping

    _default_presentation_modifiers = _create_default_presentation_modifiers.__func__()

    @staticmethod
    def _analyse_datetime_picture(picture: str) -> PictureFormat:
        """
        Analyse a datetime format picture and return a PictureFormat object.
        Args:
            picture (str): The format picture.
        Returns:
            PictureFormat: Format specification object.
        """
        fmt = PictureFormat()
        start = 0
        pos = 0
        while pos < len(picture):
            if picture[pos] == "[":
                # check it's not a doubled [[
                if picture[pos + 1] == "[":
                    # literal [
                    fmt.add_literal(picture, start, pos)
                    fmt.parts.append(SpecPart("literal", value="["))
                    pos += 2
                    start = pos
                    continue
                fmt.add_literal(picture, start, pos)
                start = pos
                pos = picture.find("]", start)
                if pos == -1:
                    raise RuntimeError(Constants.ERR_MSG_NO_CLOSING_BRACKET)
                marker = picture[start + 1 : pos]
                marker = "".join(re.split("\\s+", marker))
                def_ = SpecPart("marker", component=marker[0])
                comma = marker.rfind(",")
                pres_mod = None
                if comma != -1:
                    width_mod = marker[comma + 1 :]
                    dash = width_mod.find("-")
                    min_width = None
                    max_width = None
                    if dash == -1:
                        min_width = width_mod
                    else:
                        min_width = width_mod[0:dash]
                        max_width = width_mod[dash + 1 :]
                    def_.width = (
                        DateTimeUtils._parse_width(min_width),
                        DateTimeUtils._parse_width(max_width),
                    )
                    pres_mod = marker[1:comma]
                else:
                    pres_mod = marker[1:]
                if len(pres_mod) == 1:
                    def_.presentation1 = pres_mod
                elif len(pres_mod) > 1:
                    last_char = pres_mod[len(pres_mod) - 1]
                    if "atco".find(last_char) != -1:
                        def_.presentation2 = last_char
                        if last_char == "o":
                            def_.ordinal = True
                        def_.presentation1 = pres_mod[0 : len(pres_mod) - 1]
                    else:
                        def_.presentation1 = pres_mod
                else:
                    def_.presentation1 = DateTimeUtils._default_presentation_modifiers[
                        def_.component
                    ]
                if def_.presentation1 is None:
                    raise RuntimeError(
                        Constants.ERR_MSG_UNKNOWN_COMPONENT_SPECIFIER.format(
                            def_.component
                        )
                    )
                if def_.presentation1[0] == "n":
                    def_.names = TCase.LOWER
                elif def_.presentation1[0] == "N":
                    if len(def_.presentation1) > 1 and def_.presentation1[1] == "n":
                        def_.names = TCase.TITLE
                    else:
                        def_.names = TCase.UPPER
                elif "YMDdFWwXxHhmsf".find(def_.component) != -1:
                    integer_pattern = def_.presentation1
                    if def_.presentation2 is not None:
                        integer_pattern += ";" + def_.presentation2
                    def_.integerFormat = DateTimeUtils._analyse_integer_picture(
                        integer_pattern
                    )
                    def_.integerFormat.ordinal = def_.ordinal
                    if def_.width is not None and def_.width[0] is not None:
                        if def_.integerFormat.mandatoryDigits < def_.width[0]:
                            def_.integerFormat.mandatoryDigits = def_.width[0]
                    if def_.component == "Y":
                        def_.n = -1
                        if def_.width is not None and def_.width[1] is not None:
                            def_.n = def_.width[1]
                            def_.integerFormat.mandatoryDigits = def_.n
                        else:
                            w = (
                                def_.integerFormat.mandatoryDigits
                                + def_.integerFormat.optionalDigits
                            )
                            if w >= 2:
                                def_.n = w
                if def_.component == "Z" or def_.component == "z":
                    def_.integerFormat = DateTimeUtils._analyse_integer_picture(
                        def_.presentation1
                    )
                    def_.integerFormat.ordinal = def_.ordinal
                fmt.parts.append(def_)
                start = pos + 1
            pos += 1
        fmt.add_literal(picture, start, pos)
        return fmt

    @staticmethod
    def _parse_width(wm: Optional[str]) -> Optional[int]:
        """
        Parse width modifier from string.
        Args:
            wm (Optional[str]): Width modifier string.
        Returns:
            Optional[int]: Parsed width or None.
        """
        if wm is None or wm == "*":
            return None
        else:
            return int(wm)

    _days = [
        "",
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
        "Sunday",
    ]
    _months = [
        "January",
        "February",
        "March",
        "April",
        "May",
        "June",
        "July",
        "August",
        "September",
        "October",
        "November",
        "December",
    ]

    _iso8601_spec = None

    @staticmethod
    def format_datetime(
        millis: int, picture: Optional[str], timezone: Optional[str]
    ) -> str:
        """
        Format a datetime value according to a picture and timezone.
        Args:
            millis (int): Milliseconds since epoch.
            picture (Optional[str]): Format picture.
            timezone (Optional[str]): Timezone offset.
        Returns:
            str: Formatted datetime string.
        """
        offset_hours = 0
        offset_minutes = 0

        if timezone is not None:
            offset = int(timezone)
            offset_hours = math.trunc(offset / float(100))
            offset_minutes = int(math.fmod(offset, 100))
        format_spec = None
        if picture is None:
            if DateTimeUtils._iso8601_spec is None:
                DateTimeUtils._iso8601_spec = DateTimeUtils._analyse_datetime_picture(
                    "[Y0001]-[M01]-[D01]T[H01]:[m01]:[s01].[f001][Z01:01t]"
                )
            format_spec = DateTimeUtils._iso8601_spec
        else:
            format_spec = DateTimeUtils._analyse_datetime_picture(picture)

        offset_millis = (60 * offset_hours + offset_minutes) * 60 * 1000
        date_time = datetime.datetime.fromtimestamp(
            (millis + offset_millis) / 1000.0, datetime.timezone.utc
        )
        result = ""
        for part in format_spec.parts:
            if part.type == "literal":
                result += part.value
            else:
                result += DateTimeUtils._format_component(
                    date_time, part, offset_hours, offset_minutes
                )

        return result

    @staticmethod
    def _format_component(
        date: datetime.datetime,
        marker_spec: SpecPart,
        offset_hours: int,
        offset_minutes: int,
    ) -> str:
        """
        Format a single component of a datetime value.
        Args:
            date (datetime.datetime): The datetime object.
            marker_spec (SpecPart): Specification for the component.
            offset_hours (int): Timezone offset hours.
            offset_minutes (int): Timezone offset minutes.
        Returns:
            str: Formatted component string.
        """
        component_value = DateTimeUtils._get_datetime_fragment(
            date, marker_spec.component
        )

        if "YMDdFWwXxHhms".find(marker_spec.component) != -1:
            if marker_spec.component == "Y":
                if marker_spec.n != -1:
                    component_value = str(
                        int(
                            (
                                int(
                                    math.fmod(
                                        int(float(component_value)), 10**marker_spec.n
                                    )
                                )
                            )
                        )
                    )
            if marker_spec.names is not None:
                if marker_spec.component == "M" or marker_spec.component == "x":
                    component_value = DateTimeUtils._months[
                        int(float(component_value)) - 1
                    ]
                elif marker_spec.component == "F":
                    component_value = DateTimeUtils._days[int(float(component_value))]
                else:
                    raise RuntimeError(
                        Constants.ERR_MSG_INVALID_NAME_MODIFIER.format(
                            marker_spec.component
                        )
                    )
                if marker_spec.names == TCase.UPPER:
                    component_value = component_value.upper()
                elif marker_spec.names == TCase.LOWER:
                    component_value = component_value.casefold()
                if (
                    marker_spec.width is not None
                    and len(component_value) > marker_spec.width[1]
                ):
                    component_value = component_value[0 : marker_spec.width[1]]
            else:
                component_value = DateTimeUtils._format_integer(
                    int(float(component_value)), marker_spec.integerFormat
                )
        elif marker_spec.component == "f":
            component_value = DateTimeUtils._format_integer(
                int(float(component_value)), marker_spec.integerFormat
            )
        elif marker_spec.component == "Z" or marker_spec.component == "z":
            offset = offset_hours * 100 + offset_minutes
            if marker_spec.integerFormat.regular:
                component_value = DateTimeUtils._format_integer(
                    offset, marker_spec.integerFormat
                )
            else:
                num_digits = marker_spec.integerFormat.mandatoryDigits
                if num_digits == 1 or num_digits == 2:
                    component_value = DateTimeUtils._format_integer(
                        offset_hours, marker_spec.integerFormat
                    )
                    if offset_minutes != 0:
                        component_value += ":" + DateTimeUtils.format_integer(
                            offset_minutes, "00"
                        )
                elif num_digits == 3 or num_digits == 4:
                    component_value = DateTimeUtils._format_integer(
                        offset, marker_spec.integerFormat
                    )
                else:
                    raise RuntimeError(Constants.ERR_MSG_TIMEZONE_FORMAT)
            if offset >= 0:
                component_value = "+" + component_value
            if marker_spec.component == "z":
                component_value = "GMT" + component_value
            if (
                offset == 0
                and marker_spec.presentation2 is not None
                and marker_spec.presentation2 == "t"
            ):
                component_value = "Z"
        elif marker_spec.component == "P":
            # §9.8.4.7 Formatting Other Components
            # Formatting P for am/pm
            # getDateTimeFragment() always returns am/pm lower case so check for UPPER here
            if marker_spec.names == TCase.UPPER:
                component_value = component_value.upper()
        return component_value

    @staticmethod
    def _get_datetime_fragment(date: datetime.datetime, component: str) -> str:
        """
        Extract a fragment/component from a datetime object.
        Args:
            date (datetime.datetime): The datetime object.
            component (str): Component specifier.
        Returns:
            str: Extracted value as string.
        """
        component_value = ""
        if component == "Y":  # year
            component_value = str(date.year)
        elif component == "M":  # month in year
            component_value = str(date.month)
        elif component == "D":  # day in month
            component_value = str(date.day)
        elif component == "d":  # day in year
            component_value = str(date.timetuple().tm_yday)
        elif component == "F":  # day of week
            component_value = str(date.isoweekday())
        elif component == "W":  # week in year
            component_value = str(date.isocalendar().week)
        elif component == "w":  # week in month
            component_value = str(DateTimeUtils.week_in_month(date))
        elif component == "X":
            component_value = str(DateTimeUtils.iso_week_numbering_year(date))
        elif component == "x":
            component_value = str(DateTimeUtils.iso_week_numbering_month(date))
        elif component == "H":  # hour in day (24 hours)
            component_value = str(date.hour)
        elif component == "h":  # hour in day (12 hours)
            hour = date.hour
            if hour > 12:
                hour -= 12
            elif hour == 0:
                hour = 12
            component_value = str(hour)
        elif component == "P":
            component_value = "am" if date.hour < 12 else "pm"
        elif component == "m":
            component_value = str(date.minute)
        elif component == "s":
            component_value = str(date.second)
        elif component == "f":
            component_value = str(date.microsecond / 1000.0)
        elif component == "Z" or component == "z":

            logging.warning(
                "Component %s not implemented for date extraction.", component
            )
        elif component == "C":
            component_value = "ISO"
        elif component == "E":
            component_value = "ISO"
        return component_value

    @staticmethod
    def week_in_month(dt: datetime.datetime) -> int:
        """
        Calculate the week number in the month for a given date.
        Args:
            dt (datetime.datetime): The date.
        Returns:
            int: Week number in month.
        """
        this_month = YearMonth(dt.year, dt.month)
        start_of_week1 = DateTimeUtils.start_of_first_week(this_month)
        today = datetime.date(this_month.year, this_month.month, dt.day)
        week = DateTimeUtils.delta_weeks(start_of_week1, today)
        if week > 4:
            start_of_following_month = DateTimeUtils.start_of_first_week(
                this_month.next_month()
            )
            if today >= start_of_following_month:
                week = 1
        elif week < 1:
            start_of_previous_month = DateTimeUtils.start_of_first_week(
                this_month.previous_month()
            )
            week = DateTimeUtils.delta_weeks(start_of_previous_month, today)
        return math.floor(week)

    @staticmethod
    def iso_week_numbering_year(dt: datetime.datetime) -> int:
        """
        Get the ISO week numbering year for a given date.
        Args:
            dt (datetime.datetime): The date.
        Returns:
            int: ISO week numbering year.
        """
        this_year = YearMonth(dt.year, 1)
        start_of_iso_year = DateTimeUtils.start_of_first_week(this_year)
        end_of_iso_year = DateTimeUtils.start_of_first_week(this_year.next_year())
        now = datetime.date(dt.year, dt.month, dt.day)
        if now < start_of_iso_year:
            return this_year.year - 1
        elif now >= end_of_iso_year:
            return this_year.year + 1
        else:
            return this_year.year

    @staticmethod
    def iso_week_numbering_month(dt: datetime.datetime) -> int:
        """
        Get the ISO week numbering month for a given date.
        Args:
            dt (datetime.datetime): The date.
        Returns:
            int: ISO week numbering month.
        """
        this_month = YearMonth(dt.year, dt.month)
        start_of_iso_month = DateTimeUtils.start_of_first_week(this_month)
        next_month = this_month.next_month()
        end_of_iso_month = DateTimeUtils.start_of_first_week(next_month)
        now = datetime.date(dt.year, dt.month, dt.day)
        if now < start_of_iso_month:
            return this_month.previous_month().month
        elif now >= end_of_iso_month:
            return next_month.month
        else:
            return this_month.month

    @staticmethod
    def start_of_first_week(year_month: "YearMonth") -> datetime.date:
        """
        Calculate the start date of the first ISO week for a year/month.
        Args:
            year_month (YearMonth): YearMonth object.
        Returns:
            datetime.date: Start date of first week.
        """
        # ISO 8601 defines the first week of the year to be the week that contains the first Thursday
        # XPath F&O extends this same definition for the first week of a month
        # the week starts on a Monday - calculate the millis for the start of the first week
        # millis for given 1st Jan of that year (at 00:00 UTC)
        jan1 = datetime.date(year_month.year, year_month.month, 1)
        day_of_jan1 = jan1.isoweekday()
        # if Jan 1 is Fri, Sat or Sun, then add the number of days ( in millis) to jan1 to get the start of week 1
        return (
            jan1 + datetime.timedelta(days=8 - day_of_jan1)
            if day_of_jan1 > 4
            else jan1 - datetime.timedelta(days=day_of_jan1 - 1)
        )

    @staticmethod
    def delta_weeks(start: datetime.date, end: datetime.date) -> int:
        """
        Calculate the number of weeks between two dates.
        Args:
            start (datetime.date): Start date.
            end (datetime.date): End date.
        Returns:
            int: Number of weeks.
        """
        return int((end - start).total_seconds() / (7 * 24 * 60 * 60) + 1)

    @staticmethod
    def parse_datetime(timestamp: Optional[str], picture: str) -> Optional[int]:
        """
        Parse a datetime string according to a picture specification.
        Args:
            timestamp (Optional[str]): The datetime string.
            picture (str): Format picture.
        Returns:
            Optional[int]: Milliseconds since epoch or None.
        """
        format_spec = DateTimeUtils._analyse_datetime_picture(picture)
        match_spec = DateTimeUtils._generate_regex(format_spec)
        full_regex = "^"
        for part in match_spec.parts:
            full_regex += "(" + part.regex + ")"
        full_regex += "$"
        pattern = re.compile(full_regex, re.IGNORECASE)
        match = pattern.search(timestamp)
        if match is not None:
            dm_a = 161
            dm_b = 130
            dm_c = 84
            dm_d = 72
            tm_a = 23
            tm_b = 47

            components = {}
            i = 1
            while i <= len(match.groups()):
                mpart = match_spec.parts[i - 1]
                try:
                    components[mpart.component] = mpart.parse(match.group(i))
                except NotImplementedError as e:
                    logging.warning(
                        "NotImplementedError in component %s: %s", mpart.component, e
                    )
                i += 1

            if not components:
                # nothing specified
                return None

            mask = 0

            for part in "YXMxWwdD":
                mask <<= 1
                if components.get(part) is not None:
                    mask += 1
            date_a = DateTimeUtils._is_type(dm_a, mask)
            date_b = not date_a and DateTimeUtils._is_type(dm_b, mask)
            date_c = DateTimeUtils._is_type(dm_c, mask)
            date_d = not date_c and DateTimeUtils._is_type(dm_d, mask)

            mask = 0
            for part in "PHhmsf":
                mask <<= 1
                if components.get(part) is not None:
                    mask += 1

                logging.debug("Checked part %s for mask calculation.", part)

            time_a = DateTimeUtils._is_type(tm_a, mask)
            time_b = not time_a and DateTimeUtils._is_type(tm_b, mask)

            date_comps = (
                "YB" if date_b else "XxwF" if date_c else "XWF" if date_d else "YMD"
            )
            time_comps = "Phmsf" if time_b else "Hmsf"
            comps = date_comps + time_comps

            now = datetime.datetime.now(datetime.timezone.utc)

            start_specified = False
            end_specified = False
            for part in comps:
                if components.get(part) is None:
                    if start_specified:
                        components[part] = 1 if "MDd".find(part) != -1 else 0
                        end_specified = True
                    else:
                        components[part] = int(
                            float(DateTimeUtils._get_datetime_fragment(now, part))
                        )
                else:
                    start_specified = True
                    if end_specified:
                        raise RuntimeError(Constants.ERR_MSG_MISSING_FORMAT)
            if components.get("M") is not None and components["M"] > 0:
                components["M"] = components["M"] - 1
            else:
                components["M"] = 0
            if date_b:
                first_jan = datetime.datetime(components["Y"], 1, 1, 0, 0)
                first_jan = first_jan + datetime.timedelta(days=components["d"] - 1)
                components["M"] = first_jan.month - 1
                components["D"] = first_jan.day
            if date_c:
                # TODO implement this
                # parsing this format not currently supported
                raise RuntimeError(Constants.ERR_MSG_MISSING_FORMAT)
            if date_d:
                # TODO implement this
                # parsing this format (ISO week date) not currently supported
                raise RuntimeError(Constants.ERR_MSG_MISSING_FORMAT)
            if time_b:
                components["H"] = 0 if components["h"] == 12 else components["h"]
                if components["P"] == 1:
                    components["H"] = components["H"] + 12
            cal = datetime.datetime(
                components["Y"],
                components["M"] + 1,
                components["D"],
                components["H"],
                components["m"],
                components["s"],
                components["f"] * 1000,
                datetime.timezone.utc,
            )
            millis = cal.timestamp() * 1000
            if components.get("Z") is not None:
                millis -= components["Z"] * 60 * 1000
            elif components.get("z") is not None:
                millis -= components["z"] * 60 * 1000
            return int(millis)
        return None

    @staticmethod
    def _is_type(type_code: int, mask: int) -> bool:
        """
        Check if a mask matches a type code.
        Args:
            type_code (int): Type code.
            mask (int): Mask value.
        Returns:
            bool: True if matches, else False.
        """
        return ((~type_code & mask) == 0) and (type_code & mask) != 0

    @staticmethod
    def _generate_regex(format_spec: PictureFormat) -> "PictureMatcher":
        """
        Generate a regex matcher for a PictureFormat specification.
        Args:
            format_spec (PictureFormat): Format specification.
        Returns:
            PictureMatcher: Matcher object.
        """
        matcher = PictureMatcher()
        for part in format_spec.parts:
            res = None
            if part.type == "literal":
                p = re.compile("[.*+?^${}()|\\[\\]\\\\]")

                regex = re.sub(p, r"\g<0>", part.value)
                res = MatcherPart(regex)
            elif part.component == "Z" or part.component == "z":
                separator = (
                    len(part.integerFormat.groupingSeparators) == 1
                    and part.integerFormat.regular
                )
                regex = ""
                if part.component == "z":
                    regex = "GMT"
                regex += "[-+][0-9]+"
                if separator:
                    regex += (
                        part.integerFormat.groupingSeparators[0].character + "[0-9]+"
                    )
                res = MatcherPartTimeZone(regex, part, separator)
            elif part.integerFormat is not None:
                res = DateTimeUtils._generate_regex_with_component(
                    part.component, part.integerFormat
                )
            else:
                regex = "[a-zA-Z]+"
                lookup = {}
                if part.component == "M" or part.component == "x":
                    i = 0
                    while i < len(DateTimeUtils._months):
                        if part.width is not None and part.width[1] is not None:
                            lookup[DateTimeUtils._months[i][0 : part.width[1]]] = i + 1
                        else:
                            lookup[DateTimeUtils._months[i]] = i + 1
                        i += 1
                elif part.component == "F":
                    i = 1
                    while i < len(DateTimeUtils._days):
                        if part.width is not None and part.width[1] is not None:
                            lookup[DateTimeUtils._days[i][0 : part.width[1]]] = i
                        else:
                            lookup[DateTimeUtils._days[i]] = i
                        i += 1
                elif part.component == "P":
                    lookup["am"] = 0
                    lookup["AM"] = 0
                    lookup["pm"] = 1
                    lookup["PM"] = 1
                else:
                    raise RuntimeError(
                        Constants.ERR_MSG_INVALID_NAME_MODIFIER.format(part.component)
                    )
                res = MatcherPartLookup(regex, lookup)
            res.component = part.component
            matcher.parts.append(res)
        return matcher

    @staticmethod
    def _generate_regex_with_component(
        component: Optional[str], format_spec: Optional[Format]
    ) -> MatcherPart:
        """
        Generate a regex matcher for a component and format specification.
        Args:
            component (Optional[str]): Component specifier.
            format_spec (Optional[Format]): Format specification.
        Returns:
            MatcherPart: Matcher object.
        """
        is_upper = format_spec.case_type == TCase.UPPER
        if format_spec.primary == Formats.LETTERS:
            regex = "[A-Z]+" if is_upper else "[a-z]+"
            matcher = MatcherPartLetters(regex, is_upper)
        elif format_spec.primary == Formats.ROMAN:
            regex = "[MDCLXVI]+" if is_upper else "[mdclxvi]+"
            matcher = MatcherPartRoman(regex, is_upper)
        elif format_spec.primary == Formats.WORDS:
            words = set(DateTimeUtils._word_values.keys())
            words.add("and")
            words.add("[\\-, ]")
            regex = "(?:" + "|".join(words) + ")+"
            from src.jsonata.DateTimeUtils.MatcherPartWords import MatcherPartWords

            matcher = MatcherPartWords(regex)
        elif format_spec.primary == Formats.DECIMAL:
            regex = "[0-9]+"
            if component == "Y":
                regex = "[0-9]{2,4}"
            elif (
                (component == "M")
                or (component == "D")
                or (component == "H")
                or (component == "h")
                or (component == "m")
                or (component == "s")
            ):
                regex = "[0-9]{1,2}"

            if format_spec.ordinal:
                regex += "(?:th|st|nd|rd)"
            matcher = MatcherPartDecimal(regex, format_spec)
        else:
            raise RuntimeError(Constants.ERR_MSG_SEQUENCE_UNSUPPORTED)
        return matcher

    @staticmethod
    def letters_to_decimal(letters: str, a_char: str) -> int:
        """
        Convert a string of letters to its decimal value.
        Args:
            letters (str): Letter string.
            a_char (str): Base character ('A' or 'a').
        Returns:
            int: Decimal value.
        """
        decimal = 0
        chars = list(letters)
        i = 0
        while i < len(chars):
            decimal += (ord(chars[len(chars) - i - 1]) - ord(a_char) + 1) * 26**i
            i += 1
        return decimal


# Removed access to protected member
