from utils.input_dialogs import confirm_input_dialog
from utils.logger import Log
from utils.local_settings import LocalSettings
from extensions.url import format_url, get_base_url
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

    success, settings = LocalSettings.try_load()
    if success and LocalSettings.try_parse(settings):
        r_endpoint: str = app_config['rancher']['endpoint']
        if not r_endpoint:
            r_endpoint = confirm_input_dialog("Insert the Rancher endpoint:")

        r_base_url: str = get_base_url(r_endpoint)
        r_username: str = app_config['rancher']['username']
        r_password: str = app_config['rancher']['password']
        if not (r_username or r_password):
            __log.warning(
                "Provide your credentials to access Rancher API.\n"
                "If you don't have any API key yet, consider to visit:\n"
                f"\t{format_url(r_base_url, app_config['static']['api_keys'])}"
            )

            if not r_username:
                r_username = confirm_input_dialog(
                    "Insert your Rancher Access Key (username):")
            if not r_password:
                r_password = confirm_input_dialog(
                    "Insert your Rancher Secret Key (password):")
    else:
        r_endpoint = confirm_input_dialog("Insert the Rancher endpoint:")
        r_base_url: str = get_base_url(r_endpoint)

        __log.warning(
            "Provide your credentials to access Rancher API.\n"
            "If you don't have any API key yet, consider to visit:\n"
            f"\t{format_url(r_base_url, app_config['static']['api_keys'])}"
        )

        r_username = confirm_input_dialog(
            "Insert your Rancher Access Key (username):")
        r_password = confirm_input_dialog(
            "Insert your Rancher Secret Key (password):")

    app_config['rancher']['base_url'] = r_base_url
    app_config['rancher']['endpoint'] = r_endpoint
    app_config['rancher']['username'] = r_username
    app_config['rancher']['password'] = r_password

    LocalSettings.save()
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
