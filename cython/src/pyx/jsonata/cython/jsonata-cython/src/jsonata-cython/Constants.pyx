# cython: language_level=3

# Error message constants
cdef public str _ERR_MSG_SEQUENCE_UNSUPPORTED = "Formatting or parsing an integer as a sequence starting with %s is not supported by this implementation"
ERR_MSG_SEQUENCE_UNSUPPORTED = _ERR_MSG_SEQUENCE_UNSUPPORTED

cdef public str _ERR_MSG_DIFF_DECIMAL_GROUP = "In a decimal digit pattern, all digits must be from the same decimal group"
ERR_MSG_DIFF_DECIMAL_GROUP = _ERR_MSG_DIFF_DECIMAL_GROUP

cdef public str _ERR_MSG_NO_CLOSING_BRACKET = "No matching closing bracket ']' in date/time picture string"
ERR_MSG_NO_CLOSING_BRACKET = _ERR_MSG_NO_CLOSING_BRACKET

cdef public str _ERR_MSG_UNKNOWN_COMPONENT_SPECIFIER = "Unknown component specifier %s in date/time picture string"
ERR_MSG_UNKNOWN_COMPONENT_SPECIFIER = _ERR_MSG_UNKNOWN_COMPONENT_SPECIFIER

cdef public str _ERR_MSG_INVALID_NAME_MODIFIER = "The 'name' modifier can only be applied to months and days in the date/time picture string, not %s"
ERR_MSG_INVALID_NAME_MODIFIER = _ERR_MSG_INVALID_NAME_MODIFIER

cdef public str _ERR_MSG_TIMEZONE_FORMAT = "The timezone integer format specifier cannot have more than four digits"
ERR_MSG_TIMEZONE_FORMAT = _ERR_MSG_TIMEZONE_FORMAT

cdef public str _ERR_MSG_MISSING_FORMAT = "The date/time picture string is missing specifiers required to parse the timestamp"
ERR_MSG_MISSING_FORMAT = _ERR_MSG_MISSING_FORMAT

cdef public str _ERR_MSG_INVALID_OPTIONS_SINGLE_CHAR = "Argument 3 of function %s is invalid. The value of the %s property must be a single character"
ERR_MSG_INVALID_OPTIONS_SINGLE_CHAR = _ERR_MSG_INVALID_OPTIONS_SINGLE_CHAR

cdef public str _ERR_MSG_INVALID_OPTIONS_STRING = "Argument 3 of function %s is invalid. The value of the %s property must be a string"
ERR_MSG_INVALID_OPTIONS_STRING = _ERR_MSG_INVALID_OPTIONS_STRING


# Decimal format symbols
cdef public str _SYMBOL_DECIMAL_SEPARATOR = "decimal-separator"
SYMBOL_DECIMAL_SEPARATOR = _SYMBOL_DECIMAL_SEPARATOR

cdef public str _SYMBOL_GROUPING_SEPARATOR = "grouping-separator"
SYMBOL_GROUPING_SEPARATOR = _SYMBOL_GROUPING_SEPARATOR

cdef public str _SYMBOL_INFINITY = "infinity"
SYMBOL_INFINITY = _SYMBOL_INFINITY

cdef public str _SYMBOL_MINUS_SIGN = "minus-sign"
SYMBOL_MINUS_SIGN = _SYMBOL_MINUS_SIGN

cdef public str _SYMBOL_NAN = "NaN"
SYMBOL_NAN = _SYMBOL_NAN

cdef public str _SYMBOL_PERCENT = "percent"
SYMBOL_PERCENT = _SYMBOL_PERCENT

cdef public str _SYMBOL_PER_MILLE = "per-mille"
SYMBOL_PER_MILLE = _SYMBOL_PER_MILLE

cdef public str _SYMBOL_ZERO_DIGIT = "zero-digit"
SYMBOL_ZERO_DIGIT = _SYMBOL_ZERO_DIGIT

cdef public str _SYMBOL_DIGIT = "digit"
SYMBOL_DIGIT = _SYMBOL_DIGIT

cdef public str _SYMBOL_PATTERN_SEPARATOR = "pattern-separator"
SYMBOL_PATTERN_SEPARATOR = _SYMBOL_PATTERN_SEPARATOR
