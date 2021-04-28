from pathlib import Path
from typing import Any
from logging import (
    Logger, Formatter, getLogger,
    basicConfig, NOTSET, DEBUG,
    INFO, WARNING, ERROR, FATAL
)

__LOG = None


class Log:
    _DEBUG: str = ' '
    _INFO: str = '+'
    _WARNING: str = '!'
    _ERROR: str = '?'
    _CRITICAL: str = 'x'

    def __init__(self, name: str, level: int) -> None:
        self.__nome = name
        self.__level = Log.__log_level(level)
        self.__logs = {}
        self.__dependencies = {}

    def __log(self) -> Logger:
        return self.__logs.get(self.__nome)

    def get_basic_config(self) -> dict:
        formatter: Formatter = Formatter(
            '%(asctime)s,%(msecs)-3d - %(name)-12s - %(levelname)-8s => '
            '%(message)s')
        basic_config: dict = {
            'format': vars(formatter).get('_fmt'),
            'datefmt': '%Y-%m-%d %H:%M:%S',
            'level': self.__level
        }
        return basic_config

    def apply_basic_config(self, basic_config: dict) -> None:
        basicConfig(**basic_config)

    @staticmethod
    def __log_level(level: int) -> int:
        if level == 1:
            return DEBUG
        elif level == 2:
            return INFO
        elif level == 3:
            return WARNING
        elif level == 4:
            return ERROR
        elif level == 5:
            return FATAL
        else:
            return NOTSET

    @staticmethod
    def __format_message(symbol: str, text: str, **kwargs: dict) -> str:
        message: str = f" [{symbol}]"
        origin: str = kwargs.pop('origin', None)
        if origin:
            is_file: bool = kwargs.pop('is_file', False)
            if is_file:
                origin = Path(origin).stem

            message += f" [{origin}]"

        message += f" {text}"
        args: dict = kwargs.pop('args', {})
        if args:
            for key, value in args.items():
                message += f"\n- {key}: {value}"
        return message

    @staticmethod
    def get_singleton() -> Any:
        return __LOG

    @staticmethod
    def set_singleton(log) -> None:
        global __LOG
        __LOG = log

    def debug(self, text: str, **kwargs: dict) -> None:
        message: str = Log.__format_message(self._DEBUG, text, **kwargs)
        self.__log().debug(message)

    def info(self, text: str, **kwargs: dict) -> None:
        message: str = Log.__format_message(self._INFO, text, **kwargs)
        self.__log().info(message)

    def warning(self, text: str, **kwargs: dict) -> None:
        message: str = Log.__format_message(self._WARNING, text, **kwargs)
        self.__log().warning(message)

    def error(self, text: str, **kwargs: dict) -> None:
        message: str = Log.__format_message(self._ERROR, text, **kwargs)
        self.__log().error(message)

    def critical(self, text: str, **kwargs: dict) -> None:
        message: str = Log.__format_message(self._CRITICAL, text, **kwargs)
        self.__log().critical(message)

    def add_dependency(self, name: str, level: int) -> None:
        self.__dependencies.update({name: level})

    def configure(self) -> None:
        basic_config: dict = self.get_basic_config()
        self.apply_basic_config(basic_config)

        main_log: Logger = getLogger(self.__nome)
        main_log.setLevel(self.__level)
        self.__logs.update({self.__nome: main_log})
        self.critical(
            f"Configuring global logger to level '{self.__level}'.")

        for key, value in self.__dependencies.items():
            log: Logger = getLogger(key)
            log.setLevel(value)
            self.__logs.update({key: log})
            self.critical(
                f"Configuring dependency logger '{key}' "
                f"to level '{value}'.")
