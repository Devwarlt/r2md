from utils.dialog import confirm_input_dialog
from utils.logger import Log
from config import app_config
from traceback import format_exc
from sys import exit

__exit_code: int = 0
__log: Log = Log(app_config['name'], app_config['log_level'])
__log.configure()

Log.set_singleton(__log)

try:
    __log.info(
        f"Hello, world!\n"
        f"{'~' * 50}\n"
        f"{app_config['title']}\n\n"
        f"{app_config['description']}\n"
        f"{'~' * 50}")
    __log.warning(
        "Provide your credentials to access Rancher API.\n"
        "If you don't have any API key yet, consider to visit "
        f"URL:\n\t{app_config['rancher']['url']}/apikeys")

    r_endpoint: str = confirm_input_dialog("Insert the Rancher endpoint:")
    r_token: str = confirm_input_dialog("Insert the Bearer Token:")
    r_token: list = r_token.split(':')
    r_username: str = r_token[0]
    r_password: str = r_token[1]

    app_config['rancher']['endpoint'] = r_endpoint
    app_config['rancher']['username'] = r_username
    app_config['rancher']['password'] = r_password
except KeyboardInterrupt:
    __log.warning(f"{app_config['name']} is preparing to shutdown...")
except Exception as error:
    __log.critical(
        f"{app_config['name']} stopped suddenly!",
        args={'Stacktrace': format_exc()}
    )
    __exit_code = 1
finally:
    __log.warning("Killing main thread.")
    exit(__exit_code)
