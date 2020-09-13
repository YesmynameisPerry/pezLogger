from sys import stdout
from traceback import format_exc
from datetime import datetime
from typing import Dict, TextIO, Any, List, Callable
from json import dumps
from inspect import stack, getmembers, FrameInfo, signature
from pezLogger.src.base.baseLogger import BaseLogger
from pezLogger.src.base.enums import LogLevel, LogLocation
from pezLogger.src.base.ANSI import *
from copy import deepcopy

__all__ = ["Logger"]

class UnexpectedArgumentException(ValueError):
    pass

class Logger(BaseLogger):

    __logSeparator = "\n\n~~~~~~~~~~\n"

    def __init__(self, *,
                 logLocation: LogLocation = LogLocation.FILE,
                 logFileName: str = "logs.log",
                 errorFileName: str = "errors.log",
                 resetFile: bool = True,
                 minimumLogLevel: LogLevel = LogLevel.INFO,
                 globalContext: Dict[str, Any] = None,
                 logColours: bool = True,
                 customLogColours: Dict[LogLevel, str] = None
                 ):
        """
        Enables you to throw your words into it and have them logged nicely for you.

        :param logLocation: Determines where the log stream is. The error stream will always be to file.
        :param logFileName: The filename used for the log stream if logDestination is LogLocation.File.
        :param errorFileName: The filename used for the error stream.
        :param resetFile: Overwrite the log and error files if True, append the logs to the existing files if False.
        :param minimumLogLevel: Choose the minimum level of logs to be written to the log/error streams.
        :param globalContext: Context to be logged at the top of the log stream.
        :param logColours: Use ANSI colour codes when logging to the console.
        :param customLogColours: Colour overrides for the different log levels. Any values not provided will use the default for that level.
        """
        self.__validateInitArguments(vars())

        # Set up them variables
        self.__logFileName: str = logFileName
        self.__errorFileName: str = errorFileName
        self.__errorStream: TextIO = open(errorFileName, "w" if resetFile else "a")
        self.__logLocation: LogLocation = logLocation
        if self.__logLocation == LogLocation.FILE:
            self.__logStream: TextIO = open(logFileName, "w" if resetFile else "a")
        else:
            self.__logStream: TextIO = stdout
        self.__errorCount: int = 0
        self.__minimumLogLevel: LogLevel = minimumLogLevel
        self.__loggingEnabled: bool = True

        self.__logColours: bool = logColours and self.__logLocation == LogLocation.CONSOLE
        if customLogColours is None:
            customLogColours = dict()
        self.__logColourLookup: Dict[LogLevel, str] = {
            LogLevel.DEBUG: ANSI_FOREGROUND_WHITE,
            LogLevel.INFO: ANSI_FOREGROUND_GREEN,
            LogLevel.WARNING: ANSI_FOREGROUND_YELLOW,
            LogLevel.ERROR: ANSI_FOREGROUND_RED,
            LogLevel.FATAL: ANSI_BACKGROUND_RED,
            **customLogColours
        }

        # Set up them log streams
        self.__writeLogHeaders(globalContext=globalContext)

    def restartLogging(self) -> None:
        """
        Turns logging back on if you turned it off for some reason.

        :return: None.
        """
        if self.__loggingEnabled:
            return
        self.__loggingEnabled: bool = True

        # Reopen the streams in append mode (if files)
        self.__errorStream: TextIO = open(self.__errorFileName, "a")
        if self.__logLocation == LogLocation.FILE:
            self.__logStream: TextIO = open(self.__logFileName, "a")
        else:
            self.__logStream: TextIO = stdout

        self.__writeLogHeaders(restarting=True)

    def stopLogging(self) -> None:
        """
        Safely closes the log stream and error stream, should be called before the program exits.

        :return: None.
        """
        if not self.__loggingEnabled:
            return
        self.__loggingEnabled: bool = False

        self.__logStream.write(
            f"\n~~ LOGS ENDING AT {self.__getCurrentFormattedTime()} ~~\n")
        self.__errorStream.write(
            f"\n~~ ERRORS ENDING AT {self.__getCurrentFormattedTime()} ~~\n")

        # Don't close if stdout. That breaks `print()`
        if self.__logLocation is LogLocation.FILE:
            self.__logStream.close()
            self.__errorStream.close()

        # if self.__errorCount > 0:
        #     print(f"{self.__errorCount} error{('s' if self.__errorCount > 1 else '')} encountered. They have been logged to {self.__errorFileName}.")
        self.__errorCount: int = 0

    def debug(self, message: Any, *additionalMessages: Any, additionalContext: Dict[str, Any] = None) -> None:
        """
        Logs a debug message to the log stream if appropriate.

        :param message: The main message to be logged at a debug level.
        :param additionalMessages: Content to be concatenated with the main message, using a single space between each message.
        :param additionalContext: Additional content to be logged in human-readable JSON structure.
        :return: None.
        """
        self.__validateDictionary(additionalContext)
        if self.__minimumLogLevel.value <= LogLevel.DEBUG.value and self.__loggingEnabled:
            self.__logBase("DEBUG", self.__logStream, message, *additionalMessages, additionalContext=additionalContext, colour=self.__logColourLookup[LogLevel.DEBUG])

    def info(self, message: Any, *additionalMessages: Any, additionalContext: Dict[str, Any] = None) -> None:
        """
        Logs an info message to the log stream if appropriate.

        :param message: The main message to be logged at an info level.
        :param additionalMessages: Content to be concatenated with the main message, using a single space between each message.
        :param additionalContext: Additional content to be logged in human-readable JSON structure.
        :return: None.
        """
        self.__validateDictionary(additionalContext)
        if self.__minimumLogLevel.value <= LogLevel.INFO.value and self.__loggingEnabled:
            self.__logBase("INFO", self.__logStream, message, *additionalMessages, additionalContext=additionalContext, colour=self.__logColourLookup[LogLevel.INFO])

    def warning(self, message: Any, *additionalMessages: Any, additionalContext: Dict[str, Any] = None) -> None:
        """
        Logs a warning message to the log stream if appropriate.

        :param message: The main message to be logged at a warning level.
        :param additionalMessages: Content to be concatenated with the main message, using a single space between each message.
        :param additionalContext: Additional content to be logged in human-readable JSON structure.
        :return: None.
        """
        self.__validateDictionary(additionalContext)
        if self.__minimumLogLevel.value <= LogLevel.WARNING.value and self.__loggingEnabled:
            self.__logBase("WARNING", self.__logStream, message, *additionalMessages, additionalContext=additionalContext, colour=self.__logColourLookup[LogLevel.WARNING])

    def error(self, message: Any, *additionalMessages: Any, additionalContext: Dict[str, Any] = None) -> None:
        """
        Logs a error message to the log stream and error stream if appropriate.

        :param message: The main message to be logged at an error level.
        :param additionalMessages: Content to be concatenated with the main message, using a single space between each message.
        :param additionalContext: Additional content to be logged in human-readable JSON structure.
        :return: None.
        """
        self.__validateDictionary(additionalContext)
        if self.__minimumLogLevel.value <= LogLevel.ERROR.value and self.__loggingEnabled:
            self.__errorCount += 1
            self.__logBase("ERROR", self.__logStream, message, *additionalMessages, additionalContext=additionalContext, colour=self.__logColourLookup[LogLevel.ERROR])
            self.__logBase("ERROR", self.__errorStream, message, *additionalMessages, additionalContext=additionalContext)

    def fatal(self, message: Any, *additionalMessages: Any, additionalContext: Dict[str, Any] = None) -> None:
        """
        Logs a fatal message to the log stream and error stream if appropriate.

        :param message: The main message to be logged at a fatal level.
        :param additionalMessages: Content to be concatenated with the main message, using a single space between each message.
        :param additionalContext: Additional content to be logged in human-readable JSON structure.
        :return: None.
        """
        self.__validateDictionary(additionalContext)
        if self.__minimumLogLevel.value <= LogLevel.FATAL.value and self.__loggingEnabled:
            self.__errorCount += 1
            self.__logBase("FATAL", self.__logStream, message, *additionalMessages, additionalContext=additionalContext, colour=self.__logColourLookup[LogLevel.FATAL])
            self.__logBase("FATAL", self.__errorStream, message, *additionalMessages, additionalContext=additionalContext)

    def captureException(self, *, additionalContext: Dict[str, Any] = None) -> None:
        """
        Logs the most recent exception to the log stream and error stream. Put it inside an `except` block that should never run.

        :param additionalContext: Additional content to be logged in human-readable JSON structure.
        :return: None.
        """
        self.__validateDictionary(additionalContext)
        if not self.__loggingEnabled:
            return

        self.__errorCount += 1
        self.__logBase("FATAL - Unhandled Exception", self.__logStream, str(format_exc()), additionalContext=additionalContext, colour=self.__logColourLookup[LogLevel.FATAL])
        self.__logBase("FATAL - Unhandled Exception", self.__errorStream, str(format_exc()), additionalContext=additionalContext)

    def dangerouslySetting(self, className: str, parameterName: str, value: Any, *, additionalContext: Dict[str, Any] = None) -> None:
        """
        Writes a warning log indicating the use of a class's 'dangerously set' feature.

        :param className: The name of the class whose parameter is being dangerously set.
        :param parameterName: The name of the parameter being dangerously set.
        :param value: The value that the parameter is being set to.
        :param additionalContext: Additional content to be logged in human-readable JSON structure.
        :return: None.
        """
        self.__validateDictionary(additionalContext)
        if self.__minimumLogLevel.value <= LogLevel.WARNING.value and self.__loggingEnabled:
            message: str = f"Dangerously setting {className} {parameterName} to {type(value).__name__}: {value}"
            self.__logBase("WARNING", self.__logStream, message, additionalContext=additionalContext, colour=self.__logColourLookup[LogLevel.WARNING])

    def __logBase(self, prefix: str, stream: TextIO, message: Any, *additionalMessages: Any, additionalContext: Dict[str, Any], colour: str = '') -> None:
        """
        Logs content to the given stream, also collects the function name, arguments, and local variables of the parent function that logged in the first place.

        :param prefix: The prefix to the log, usually the log level.
        :param stream: The stream the log is being written to.
        :param message: The main message to be logged.
        :param additionalMessages: Content to be concatenated with the main message, using a single space between each message.
        :param additionalContext: Additional content to be logged in human-readable JSON structure.
        :param colour: ANSI colour code to be applied for this log, will be ignored if colours disabled.
        :return: None.
        """

        # Get info about the function that requested a log (requires the call stack to be `outerFunction-> logger.x -> logger._logBase`)
        outerFrame: FrameInfo = stack()[2]
        outerFunctionName: str = outerFrame[3]
        outerFunctionLocalVariables: Dict[str, str] = dict()
        outerFunctionArgumentNames: List[str] = list()

        # Getting local variables from the top level is super messy, so only bother if we're in a function
        if outerFunctionName[0] == "_":
            # TODO - see if there's an easy way to get argument values from protected/private methods
            outerGlobals: Dict[str, Any] = dict(dict(getmembers(outerFrame[0]))["f_globals"])
            outerFunctionName = f"protected/private method {outerFunctionName} ({outerGlobals['__name__'].replace('.', '/')}.py)"
        elif outerFunctionName[:5] == "test_":
            outerGlobals: Dict[str, Any] = dict(dict(getmembers(outerFrame[0]))["f_globals"])
            outerFunctionName = f"test method {outerFunctionName} ({outerGlobals['__name__'].replace('.', '/')}.py)"
        elif outerFunctionName != "<module>":
            outerFunctionLocalVariables: Dict[str, str] = dict(getmembers(outerFrame[0]))["f_locals"]
            outerFunction: Callable[[Any], Any] = dict(dict(getmembers(outerFrame[0]))["f_globals"])[outerFunctionName]
            # noinspection PyUnresolvedReferences
            outerFunctionArgumentNames: List[str] = list(outerFunction.__code__.co_varnames[:len(signature(outerFunction).parameters)])

        outerFunctionArguments: Dict[str, Any] = dict()
        outerFunctionVariables: Dict[str, Any] = dict()

        # Sort out any local variables into function arguments and locally defined variables
        for variableName in outerFunctionLocalVariables.keys():
            if variableName in outerFunctionArgumentNames:
                outerFunctionArguments[variableName] = outerFunctionLocalVariables[variableName]
            else:
                outerFunctionVariables[variableName] = outerFunctionLocalVariables[variableName]

        outerFunctionData: Dict[str, str] = {
            "functionName": outerFunctionName,
            "arguments": outerFunctionArguments,
            "localVariables": outerFunctionVariables
        }

        # Concat all our *args
        outputString: str = str(message)

        for additionalMessage in additionalMessages:
            outputString += " " + str(additionalMessage)

        # The useful bit that makes the output happen
        stream.write(
            f"\n{colour if self.__logColours else ''}{prefix} at {self.__getCurrentFormattedTime()}:")
        stream.write(f"\n\n{outputString}")
        self.__logOptional(stream, "\nCaller information", outerFunctionData)
        self.__logOptional(stream, "\nAdditional context", additionalContext)
        stream.write(ANSI_CONTROL_RESET if self.__logColours and colour else '')
        stream.write(self.__logSeparator)
        stream.flush()

    def __writeLogHeaders(self, *, globalContext: Dict[str, Any] = None, restarting: bool = False) -> None:
        """
        Write the headers to the log streams.

        :param globalContext: Content to be logged in human-readable JSON structure at the top of a log stream.
        :param restarting: Indicates whether the headers should say 'Beginning' or 'Restarting' logs.
        :return: None.
        """
        self.__errorStream.write(
            f"\n~~ ERRORS {'RESTARTING' if restarting else 'BEGINNING'} AT {self.__getCurrentFormattedTime()} ~~\n")
        self.__logOptional(self.__errorStream, "Global context", globalContext)
        if self.__minimumLogLevel == LogLevel.FATAL:
            return
        self.__logStream.write(
            f"\n~~ LOGS {'RESTARTING' if restarting else 'BEGINNING'} AT {self.__getCurrentFormattedTime()} ~~\n")
        self.__logOptional(self.__logStream, "Global context", globalContext)
        self.__errorStream.write(self.__logSeparator)
        self.__logStream.write(self.__logSeparator)

    def __validateInitArguments(self, variables: Dict[str, Any]) -> None:
        """
        Raises an exception if the arguments provided to Logger() are invalid.

        :param variables: A dictionary of Logger() arguments and there values. Equivalent to 'vars()'.
        :return: None.
        """
        knownArguments: List[str] = ["self", "logLocation", "logFileName", "errorFileName", "resetFile", "minimumLogLevel", "globalContext", "logColours", "customLogColours"]
        for variableName in variables.keys():
            if variableName not in knownArguments:
                raise UnexpectedArgumentException(f"Argument '{variableName}' does not have validation in Logger")

        if not type(variables["logLocation"]) is LogLocation:
            raise TypeError(f"Provided logLocation '{variables['logLocation']}' is of type {type(variables['logLocation']).__name__}, it needs to be of type LogLocation")

        self.__validateLogFileName(variables["logFileName"], argumentName="logFileName")

        self.__validateLogFileName(variables["errorFileName"], argumentName="errorFileName")

        if not type(variables["resetFile"]) is bool:
            raise TypeError(f"Provided resetFile '{variables['resetFile']}' is of type {type(variables['resetFile']).__name__}, it needs to be of type bool")

        if not type(variables["minimumLogLevel"]) is LogLevel:
            raise TypeError(f"Provided minimumLogLevel '{variables['minimumLogLevel']}' is of type {type(variables['minimumLogLevel']).__name__}, it needs to be of type LogLevel")

        self.__validateDictionary(variables["globalContext"], dictionaryName="globalContext")

        if not type(variables["logColours"]) is bool:
            raise TypeError(f"Provided logColours '{variables['logColours']}' is of type {type(variables['logColours']).__name__}, it needs to be of type bool")

        self.__validateDictionary(variables["customLogColours"], keyType=LogLevel, dictionaryName="customLogColours")

    @staticmethod
    def __validateDictionary(dictionary: Dict[str, Any], *, keyType: type = str, dictionaryName: str = "argument") -> None:
        """
        Raises an exception if 'dictionary' or it's keys are of the wrong type.

        :param dictionary: The dictionary to be validated.
        :param keyType: The type expected for the keys of the dictionary.
        :param dictionaryName: The name of the dictionary, used to give raised exceptions usable context.
        :return: None.
        """
        if dictionary is None:
            return
        if not type(dictionary) is dict:
            raise TypeError(f"Provided {dictionaryName} '{dictionary}' is of type {type(dictionary).__name__}, it needs to be of type dict")
        for key in dictionary.keys():
            if not type(key) is keyType:
                raise TypeError(f"Key '{key}' in dictionary '{dictionaryName}' is of type {type(key).__name__}, it needs to be of type {keyType.__name__}")

    @staticmethod
    def __validateLogFileName(fileName: str, *, argumentName: str = "argument"):
        """
        Raises an exception if 'fileName' is of the wrong type, or not a path to a 'log' file.

        :param fileName: the file name to be validated.
        :param argumentName: the name of the file name, used to give raised exceptions usable context.
        :return: None.
        """
        if not type(fileName) is str:
            raise TypeError(f"Provided {argumentName} '{fileName}' is of type {type(fileName).__name__}, it needs to be of type str")
        if fileName[-4:] != ".log":
            raise ValueError(f"Log file {argumentName} '{fileName}' is not in the format 'xyz.log'")

    @staticmethod
    def __getCurrentFormattedTime() -> str:
        """
        Gets the current time in "%d/%m/%Y %H:%M:%S.%f" format.

        :return: the current time in "%d/%m/%Y %H:%M:%S.%f" format.
        """
        return datetime.now().strftime("%d/%m/%Y %H:%M:%S.%f")

    @staticmethod
    def __logOptional(stream: TextIO, prefix: str, content: Dict[str, Any]) -> None:
        """
        Logs content to the given stream if the content exists.

        :param stream: The stream to write the content to.
        :param prefix: The prefix to be used for this content when writing to the stream.
        :param content: The content to be logged in human-readable JSON structure.
        :return: None.
        """
        if content is not None:
            mutableContent: dict = deepcopy(content)

            # custom types and classes aren't guaranteed to be json serializable, just get the string value of them instead
            for key in mutableContent.keys():
                try:
                    dumps(mutableContent[key])
                except TypeError:
                    mutableContent[key] = str(mutableContent[key])
            stream.write(f"\n{prefix}: {dumps(mutableContent, indent = 2)}")
