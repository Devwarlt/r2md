from argparse import ArgumentParser
from utils.logger import Log
from json import dumps
from typing import Any


class LocalTestVars:

    __LOGS_FOLDER = 'logs'

    def __init__(self, file: str, type: str, encoding: str = 'utf8') -> None:
        from pathlib import Path
        self.__filename = Path(file).stem
        self.__type = type
        self.__encoding = encoding
        self.__parser = LocalTestVars.__create_parser()
        self.__displayed = False

    def handle(self, payload: Any) -> None:
        args = self.__parser.parse_args()
        log: Log = Log.get_singleton()

        if not self.__displayed:
            from sys import argv
            if len(argv[1:]) > 0:
                log.debug(
                    self.__parser.description,
                    origin=__file__, is_file=True)
                self.__displayed = True

        if payload and args.show:
            LocalTestVars.__show_action(
                self.__type, payload,
                self.__filename, self.__encoding)
        if payload and args.log:
            LocalTestVars.__log_action(
                self.__type, payload,
                self.__filename, self.__encoding)

    @staticmethod
    def __create_parser() -> ArgumentParser:
        parser = ArgumentParser(description="Local Test Vars enabled!")
        parser.add_argument(
            "-s", "--show", required=False,
            action='store_true', default=False)
        parser.add_argument(
            "-l", "--log", required=False,
            action='store_true', default=False)
        return parser

    @staticmethod
    def __show_action(
            type: str, payload: Any,
            filename: str, encoding: str = 'utf8') -> None:
        encoded_payload_dump = dumps(
            payload, sort_keys=True, indent=3)\
            .encode(encoding)

        log: Log = Log.get_singleton()
        log.debug(
            f"Processing '{type}' message for '{filename}'...:"
            f"\n{encoded_payload_dump.decode()}",
            origin=__file__, is_file=True)

    @staticmethod
    def __log_action(
            type: str, payload: Any,
            filename: str, encoding: str = 'utf8') -> None:
        from os import path, makedirs
        if not path.exists(LocalTestVars.__LOGS_FOLDER):
            makedirs(LocalTestVars.__LOGS_FOLDER)

        log: Log = Log.get_singleton()
        log.debug(
            f"Saving {type} log...", origin=__file__, is_file=True)

        with open(
                f"{LocalTestVars.__LOGS_FOLDER}/test.{filename}.log",
                "w", encoding=encoding) as log_file:
            encoded_payload_dump = dumps(
                payload, sort_keys=True,
                indent=3, ensure_ascii=False)\
                .encode(encoding)
            log_file.write(encoded_payload_dump.decode())
