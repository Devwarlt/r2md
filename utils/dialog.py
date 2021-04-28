from utils.logger import Log
from utils.str_extensions import is_null_or_whitespace


def confirm_input_dialog(question: str, nullable: bool = False) -> str:
    log: Log = Log.get_singleton()
    result: str = None
    while True:
        log.warning(question)
        result = input()

        if nullable:
            if is_null_or_whitespace(result):
                log.error("This answer is invalid, try again!")
                continue

        log.warning("Are you sure? (Y/N)")
        response: str = input()
        if not response:
            continue

        response = response.lower()
        if response != 'y':
            continue

        break

    return result
