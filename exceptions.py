from constants import (
    CONNECTION_ERROR_TEXT,
    ERROR_TEXT,
    PARSING_ERROR_TEXT,
    RECOGNIZING_ERROR_TEXT,
)


class BotError(Exception):
    """Base exception for expected bot errors.

    Attributes:
        user_message: Text shown to the user when the error occurs.
    """

    user_message: str = ERROR_TEXT


class BotConnectionError(BotError):
    """Raised when a web page or an image can't be downloaded."""

    user_message = CONNECTION_ERROR_TEXT


class BotParsingError(BotError):
    """Raised when the target image URL can't be found in the web page HTML."""

    user_message = PARSING_ERROR_TEXT


class BotRecognizingError(BotError):
    """Raised when the text can't be recognized from the image."""

    user_message = RECOGNIZING_ERROR_TEXT
