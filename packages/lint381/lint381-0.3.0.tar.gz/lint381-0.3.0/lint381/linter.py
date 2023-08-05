"""Linter tools."""
import collections

from .code import tokenize


Error = collections.namedtuple("Error", [
    "message",
    "tokens",
])
"""A linter error.

:ivar str message: The error message.
:ivar list tokens: A list of relevant tokens, in the order that they appear in
    the source code.
"""


class Linter:
    """A registry of linters for a specific language."""

    def __init__(self):
        """Initialize the linter registry to be empty."""
        self._linters = []

    def register(self, func):
        """Register the provided function as a linter.

        This should be used as a decorator:

        ```
        linters = Linter()

        @linters.register
        def linter():
            ...
        ```

        :param function func: The linting function.
        """
        self._linters.append(func)
        return func

    def lint(self, code):
        """Find linting errors on the specified lines of source code.

        :param str code: The source code.
        """
        errors = []

        for func in self._linters:
            errors.extend(func(tokenize(code)))

        return errors
