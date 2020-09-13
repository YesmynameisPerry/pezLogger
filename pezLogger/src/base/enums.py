from enum import Enum

__all__ = [
    "LogLevel",
    "LogLocation"
]

class LogLevel(Enum):
    DEBUG = 0
    INFO = 1
    WARNING = 2
    ERROR = 3
    FATAL = 4

class LogLocation(Enum):
    FILE = "log location - file"
    CONSOLE = "log location - console"