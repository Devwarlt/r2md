from utils.logger import Log
from extensions.str import is_null_or_whitespace


def yes_or_no_input_dialog(question: str) -> bool:
    log: Log = Log.get_singleton()
    log.warning(f'{question} (Y/N)')
    response: str = input()
    return response and response.lower() == 'y'


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
        if not response or response.lower() != 'y':
            continue
        break
    return result
