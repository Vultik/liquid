"""Tokenize liquid loop expressions."""
import re
from typing import Iterator

from liquid.expressions.common import Token
from liquid.expressions.common import GROUP_IDENTINDEX
from liquid.expressions.common import GROUP_IDENTQUOTED
from liquid.expressions.common import IDENTIFIER_PATTERN
from liquid.expressions.common import IDENTSTRING_PATTERN
from liquid.expressions.common import IDENTINDEX_PATTERN

from liquid.token import TOKEN_RANGE
from liquid.token import TOKEN_FLOAT
from liquid.token import TOKEN_INTEGER
from liquid.token import TOKEN_IN
from liquid.token import TOKEN_OFFSET
from liquid.token import TOKEN_LIMIT
from liquid.token import TOKEN_REVERSED
from liquid.token import TOKEN_COLS
from liquid.token import TOKEN_CONTINUE
from liquid.token import TOKEN_IDENTIFIER
from liquid.token import TOKEN_ILLEGAL
from liquid.token import TOKEN_SKIP
from liquid.token import TOKEN_NEWLINE
from liquid.token import TOKEN_LBRACKET
from liquid.token import TOKEN_RBRACKET
from liquid.token import TOKEN_LPAREN
from liquid.token import TOKEN_RPAREN
from liquid.token import TOKEN_COLON
from liquid.token import TOKEN_PIPE
from liquid.token import TOKEN_IDENTSTRING
from liquid.token import TOKEN_IDENTINDEX
from liquid.token import TOKEN_DOT

from liquid.exceptions import LiquidSyntaxError


token_rules = (
    (TOKEN_IDENTINDEX, IDENTINDEX_PATTERN),
    (TOKEN_IDENTSTRING, IDENTSTRING_PATTERN),
    (TOKEN_RANGE, r"\.\."),
    (TOKEN_FLOAT, r"-?\d+\.(?!\.)\d*"),
    (TOKEN_INTEGER, r"-?\d+\b"),
    (TOKEN_DOT, r"\."),
    (TOKEN_IDENTIFIER, IDENTIFIER_PATTERN),
    (TOKEN_LPAREN, r"\("),
    (TOKEN_RPAREN, r"\)"),
    (TOKEN_LBRACKET, r"\["),
    (TOKEN_RBRACKET, r"]"),
    (TOKEN_COLON, r":"),
    (TOKEN_PIPE, r"\|"),
    (TOKEN_NEWLINE, r"\n"),
    (TOKEN_SKIP, r"[ \t\r]+"),
    (TOKEN_ILLEGAL, r"."),
)

keywords = frozenset(
    [
        TOKEN_IN,
        TOKEN_OFFSET,
        TOKEN_LIMIT,
        TOKEN_REVERSED,
        TOKEN_COLS,
        TOKEN_CONTINUE,
    ]
)

OUTPUT_RE = re.compile(
    "|".join(f"(?P<{name}>{pattern})" for name, pattern in token_rules),
    re.DOTALL,
)


def tokenize(source: str, line_num: int = 1) -> Iterator[Token]:
    """Yield tokens from a loop expression."""
    _keywords = keywords
    for match in OUTPUT_RE.finditer(source):
        kind = match.lastgroup
        assert kind is not None

        value = match.group()
        newlines = value.count("\n")

        if kind == TOKEN_IDENTIFIER and value in _keywords:
            kind = value
        elif kind == TOKEN_IDENTINDEX:
            value = match.group(GROUP_IDENTINDEX)
        elif kind == TOKEN_IDENTSTRING:
            kind = TOKEN_IDENTIFIER
            value = match.group(GROUP_IDENTQUOTED)
        elif kind == TOKEN_NEWLINE:
            line_num += 1
            continue
        elif kind == TOKEN_SKIP:
            continue
        elif kind == TOKEN_ILLEGAL:
            raise LiquidSyntaxError(f"unexpected {value!r}", linenum=line_num)

        line_num += newlines
        yield (line_num, kind, value)
