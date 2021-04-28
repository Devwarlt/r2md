from utils.local_settings import LocalSettings
from utils.input_dialogs import confirm_input_dialog
from extensions.url import format_url
from config import app_config
from utils.logger import Log


def ask_for_new_credentials() -> None:
    r_base_url: str = app_config['rancher']['base_url']

    log: Log = Log.get_singleton()
    log.warning(
        "Provide your credentials to access Rancher API.\n"
        "If you don't have any API key yet, consider to visit:\n"
        f"\t{format_url(r_base_url, app_config['static']['api_keys'])}"
    )

    r_username = confirm_input_dialog(
        "Insert your Rancher Access Key (username):")
    r_password = confirm_input_dialog(
        "Insert your Rancher Secret Key (password):")

    app_config['rancher']['username'] = r_username
    app_config['rancher']['password'] = r_password

    LocalSettings.save()
