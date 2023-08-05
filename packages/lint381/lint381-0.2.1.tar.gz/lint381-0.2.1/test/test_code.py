"""Test the code-manipulation functions."""
from lint381.code import match_tokens, Position, Token, tokenize


def test_tokenize():
    """Ensure that we tokenize code correctly."""
    assert tokenize("""
int main() {

}
foo ();
""".strip()) == [
        Token(start=Position(row=0, column=0),
              end=Position(row=0, column=2),
              value="int"),
        Token(start=Position(row=0, column=4),
              end=Position(row=0, column=7),
              value="main"),
        Token(start=Position(row=0, column=8),
              end=Position(row=0, column=8),
              value="("),
        Token(start=Position(row=0, column=9),
              end=Position(row=0, column=9),
              value=")"),
        Token(start=Position(row=0, column=11),
              end=Position(row=0, column=11),
              value="{"),
        Token(start=Position(row=2, column=0),
              end=Position(row=2, column=0),
              value="}"),

        Token(start=Position(row=3, column=0),
              end=Position(row=3, column=2),
              value="foo"),
        Token(start=Position(row=3, column=4),
              end=Position(row=3, column=4),
              value="("),
        Token(start=Position(row=3, column=5),
              end=Position(row=3, column=5),
              value=")"),
        Token(start=Position(row=3, column=6),
              end=Position(row=3, column=6),
              value=";"),
    ]


def test_match_tokens():
    """Ensure that we match tokens correctly."""
    code = """
foo qux bar
foo grault bar
foo bar
"""

    @match_tokens(start="foo", end="bar")
    def func(tokens, match):
        return match

    expected = [["foo", "qux", "bar"],
                ["foo", "grault", "bar"],
                ["foo", "bar"]]
    assert [[i.value for i in match]
            for match in func(tokenize(code))] == expected


def test_no_matching_token():
    """Ensure that we handle cases when there is no match."""
    code = """
foo
"""

    @match_tokens(start="foo", end="bar")
    def func(tokens, match):
        return match

    assert not list(func(tokenize(code)))


def test_not_enough_lookahead():
    """Ensure that we don't return a match if there's not enough lookahead."""
    code = """
foo bar
"""

    @match_tokens(start="foo", end="bar", lookahead=1)
    def func(tokens, match):
        return match

    assert not list(func(tokenize(code)))
