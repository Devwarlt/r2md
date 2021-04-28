from config import app_config
from utils.logger import Log
from json import dump, load
from os.path import exists


class LocalSettings:
    _DEFAULT_PATH: str = '.r2md.settings.json'

    def __init__(self) -> None:
        pass

    @staticmethod
    def save() -> None:
        settings: dict = app_config['rancher']
        with open(LocalSettings._DEFAULT_PATH, 'w') as file:
            dump(settings, file, indent=3, sort_keys=True)

    @staticmethod
    def try_load() -> tuple:
        log: Log = Log.get_singleton()
        if not exists(LocalSettings._DEFAULT_PATH):
            log.warning("There is no settings yet.")
            return False, None

        with open(LocalSettings._DEFAULT_PATH) as file:
            settings: dict = load(file)
            log.info("Successfully loaded all settings!")
            return True, settings

    @staticmethod
    def try_parse(settings: dict) -> bool:
        log: Log = Log.get_singleton()

        try:
            app_config['rancher'] = settings
            log.info("Successfully parsed all settings!")
            return True
        except KeyError as error:
            log.critical("Unable to parse settings!", args={'Error': error})
        return False
