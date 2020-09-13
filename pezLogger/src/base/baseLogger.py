from abc import ABC, abstractmethod
from typing import Dict, Any

__all__ = ["BaseLogger"]

class BaseLogger(ABC):
    @abstractmethod
    def debug(self, message: Any, *additionalMessages: Any, additionalContext: Dict[str, Any] = None) -> None:
        pass

    @abstractmethod
    def info(self, message: Any, *additionalMessages: Any, additionalContext: Dict[str, Any] = None) -> None:
        pass

    @abstractmethod
    def warning(self, message: Any, *additionalMessages: Any, additionalContext: Dict[str, Any] = None) -> None:
        pass

    @abstractmethod
    def error(self, message: Any, *additionalMessages: Any, additionalContext: Dict[str, Any] = None) -> None:
        pass

    @abstractmethod
    def fatal(self, message: Any, *additionalMessages: Any, additionalContext: Dict[str, Any] = None) -> None:
        pass

    @abstractmethod
    def captureException(self, *, additionalContext: Dict[str, Any] = None) -> None:
        pass

    @abstractmethod
    def dangerouslySetting(self, className: str, parameterName: str, value: Any, *, additionalContext: Dict[str, Any] = None):
        pass

    @abstractmethod
    def stopLogging(self) -> None:
        pass

    @abstractmethod
    def restartLogging(self) -> None:
        pass