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
#
# Derived from the following code:
#
#   Project name: jsonata-java
#   Copyright Dashjoin GmbH. https://dashjoin.com
#   Licensed under the Apache License, Version 2.0 (the "License")
#
#   Project name: JSONata
# © Copyright IBM Corp. 2016, 2018 All Rights Reserved
#   This project is licensed under the MIT License, see LICENSE
#

# tokenizer.pyx
# distutils: language = c++
# cython: language_level=3

import math
import re
from libc.math cimport fmod
from cpython cimport bool as cbool

# Replace dataclasses with regular class for performance
cdef class Token:
    cdef public str type
    cdef public object value
    cdef public int position
    cdef public object id

    def __init__(self, str type, object value, int position):
        self.type = type
        self.value = value
        self.position = position
        self.id = None


cdef class Tokenizer:
    cdef int position
    cdef int depth
    cdef str path
    cdef int length

    # Use class-level dictionaries
    operators = {
        '.': 75, '[': 80, ']': 0, '{': 70, '}': 0,
        '(': 80, ')': 0, ',': 0, '@': 80, '#': 80,
        ';': 80, ':': 80, '?': 20, '+': 50, '-': 50,
        '*': 60, '/': 60, '%': 60, '|': 20, '=': 40,
        '<': 40, '>': 40, '^': 40, '**': 60, '..': 20,
        ':=': 10, '!=': 40, '<=': 40, '>=': 40, '~>': 40,
        '?:': 40, '??': 40, 'and': 30, 'or': 25, 'in': 40,
        '&': 50, '!': 0, '~': 0
    }

    escapes = {
        '"': '"', '\\': '\\', '/': '/',
        'b': '\b', 'f': '\f', 'n': '\n',
        'r': '\r', 't': '\t'
    }

    def __init__(self, str path):
        self.position = 0
        self.depth = 0
        self.path = path
        self.length = len(path)

    cpdef Token create(self, str type, object value):
        return Token(type, value, self.position)

    cpdef bint is_closing_slash(self, int position):
        cdef int backslash_count
        if self.path[position] == '/' and self.depth == 0:
            backslash_count = 0
            while self.path[position - (backslash_count + 1)] == '\\':
                backslash_count += 1
            if fmod(backslash_count, 2) == 0:
                return True
        return False

    cpdef object scan_regex(self):
        from jsonata import jexception
        cdef int start = self.position
        cdef str current_char
        cdef str pattern = ""
        cdef str flags = ""
        cdef int _flags = 0

        while self.position < self.length:
            current_char = self.path[self.position]

            if self.is_closing_slash(self.position):
                pattern = self.path[start:self.position]
                if pattern == "":
                    raise jexception.JException("S0301", self.position)
                self.position += 1
                current_char = self.path[self.position]
                start = self.position

                while current_char in ('i', 'm'):
                    self.position += 1
                    if self.position < self.length:
                        current_char = self.path[self.position]
                    else:
                        break
                flags = self.path[start:self.position] + 'g'

                if 'i' in flags:
                    _flags |= re.I
                if 'm' in flags:
                    _flags |= re.M
                return re.compile(pattern, _flags)

            if (current_char in '([{') and self.path[self.position - 1] != '\\':
                self.depth += 1
            elif (current_char in ')]}') and self.path[self.position - 1] != '\\':
                self.depth -= 1

            self.position += 1

        raise jexception.JException("S0302", self.position)

    cpdef object next(self, bint prefix):
        from jsonata import jexception, utils
        cdef str current_char
        cdef str quote_type
        cdef str qstr
        cdef str name
        cdef int i
        match_ = None
        numregex = re.compile(r"^-?(0|([1-9][0-9]*))(\.[0-9]+)?([Ee][-+]?[0-9]+)?")

        if self.position >= self.length:
            return None

        current_char = self.path[self.position]

        # Skip whitespace
        while self.position < self.length and current_char in " \t\n\r":
            self.position += 1
            if self.position >= self.length:
                return None
            current_char = self.path[self.position]

        # Comments
        if current_char == '/' and self.path[self.position + 1] == '*':
            comment_start = self.position
            self.position += 2
            current_char = self.path[self.position]
            while not (current_char == '*' and self.path[self.position + 1] == '/'):
                self.position += 1
                if self.position >= self.length:
                    raise jexception.JException("S0106", comment_start)
                current_char = self.path[self.position]
            self.position += 2
            return self.next(prefix)

        # Regex
        if not prefix and current_char == '/':
            self.position += 1
            return self.create("regex", self.scan_regex())

        # Two-char operators
        if self.position < self.length - 1:
            two_char_ops = {
                '..': "..", ':=': ":=", '!=': "!=", '>=': ">=",
                '<=': "<=", '**': "**", '~>': "~>", '?:': "?:", '??': "??"
            }
            pair = self.path[self.position:self.position + 2]
            if pair in two_char_ops:
                self.position += 2
                return self.create("operator", pair)

        # One-char operators
        if current_char in self.operators:
            self.position += 1
            return self.create("operator", current_char)

        # String literals
        if current_char in ('"', "'"):
            quote_type = current_char
            self.position += 1
            qstr = ""
            while self.position < self.length:
                current_char = self.path[self.position]
                if current_char == '\\':
                    self.position += 1
                    current_char = self.path[self.position]
                    if current_char in self.escapes:
                        qstr += self.escapes[current_char]
                    elif current_char == 'u':
                        octets = self.path[self.position + 1:self.position + 5]
                        if re.match("^[0-9a-fA-F]+$", octets):
                            qstr += chr(int(octets, 16))
                            self.position += 4
                        else:
                            raise jexception.JException("S0104", self.position)
                    else:
                        raise jexception.JException("S0301", self.position, current_char)
                elif current_char == quote_type:
                    self.position += 1
                    return self.create("string", qstr)
                else:
                    qstr += current_char
                self.position += 1
            raise jexception.JException("S0101", self.position)

        # Numbers
        match_ = numregex.search(self.path[self.position:])
        if match_:
            num = float(match_.group(0))
            if not math.isnan(num) and math.isfinite(num):
                self.position += len(match_.group(0))
                return self.create("number", utils.Utils.convert_number(num))
            else:
                raise jexception.JException("S0102", self.position)

        # Quoted names
        if current_char == '`':
            self.position += 1
            end = self.path.find('`', self.position)
            if end != -1:
                name = self.path[self.position:end]
                self.position = end + 1
                return self.create("name", name)
            self.position = self.length
            raise jexception.JException("S0105", self.position)

        # Names and variables
        i = self.position
        while True:
            if i >= self.length:
                break
            ch = self.path[i]
            if ch in " \t\n\r" or ch in self.operators:
                if self.path[self.position] == '$':
                    name = self.path[self.position + 1:i]
                    self.position = i
                    return self.create("variable", name)
                else:
                    name = self.path[self.position:i]
                    self.position = i
                    if name in ("or", "in", "and"):
                        return self.create("operator", name)
                    elif name == "true":
                        return self.create("value", True)
                    elif name == "false":
                        return self.create("value", False)
                    elif name == "null":
                        return self.create("value", None)
                    elif name == "":
                        return None
                    else:
                        return self.create("name", name)
            i += 1
