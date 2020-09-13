from pezLogger.src.base.baseLogger import BaseLogger
from typing import Any, Dict

__all__ = ["MockLogger"]

# Mock logger to be used in tests and all
class MockLogger(BaseLogger):
    def __init__(self, *args, suppress: bool = True) -> None:
        self.__suppress: bool = suppress
        if not self.__suppress:
            print(f"MOCK-LOGGER: {args}")
        self.loggingEnabled: bool = True

    def setSuppress(self, suppress: bool) -> None:
        self.__suppress = suppress

    def debug(self, message: Any, *additionalMessages: Any, additionalContext: Dict[str, Any] = None) -> None:
        if self.__suppress:
            return
        if not self.loggingEnabled:
            print(f"Logging Disabled")
        print(f"MOCK-DEBUG: {message}")

    def info(self, message: Any, *additionalMessages: Any, additionalContext: Dict[str, Any] = None) -> None:
        if self.__suppress:
            return
        if not self.loggingEnabled:
            print(f"Logging Disabled")
        print(f"MOCK-INFO: {message}")

    def warning(self, message: Any, *additionalMessages: Any, additionalContext: Dict[str, Any] = None) -> None:
        if self.__suppress:
            return
        if not self.loggingEnabled:
            print(f"Logging Disabled")
        print(f"MOCK-WARNING: {message}")

    def error(self, message: Any, *additionalMessages: Any, additionalContext: Dict[str, Any] = None) -> None:
        if self.__suppress:
            return
        if not self.loggingEnabled:
            print(f"Logging Disabled")
        print(f"MOCK-ERROR: {message}")

    def fatal(self, message: Any, *additionalMessages: Any, additionalContext: Dict[str, Any] = None) -> None:
        if self.__suppress:
            return
        if not self.loggingEnabled:
            print(f"Logging Disabled")
        print(f"MOCK-FATAL: {message}")

    def captureException(self, *, additionalContext: Dict[str, Any] = None) -> None:
        if self.__suppress:
            return
        if not self.loggingEnabled:
            print(f"Logging Disabled")
        print(f"MOCK-CAPTURE-EXCEPTION")

    def dangerouslySetting(self, className: str, parameterName: str, value: Any, *, additionalContext: Dict[str, Any] = None) -> None:
        if self.__suppress:
            return
        if not self.loggingEnabled:
            print(f"Logging Disabled")
        print(f"MOCK-DANGEROUSLY-SETTING")

    def stopLogging(self) -> None:
        self.loggingEnabled = False
        if self.__suppress:
            return
        print(f"Logging Stopped")

    def restartLogging(self) -> None:
        self.loggingEnabled = True
        if self.__suppress:
            return
        print(f"Logging Restarted")