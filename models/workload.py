from json import dumps


class Workload(object):
    def __init__(self) -> None:
        pass

    def serialize(self, data: dict) -> None:
        self.__data: dict = data
        self.__id: str = data.get('id')
        self.__name: str = data.get('name')
        self.__namespace: str = data.get('namespace')
        self.__version: str = data.get('version')

    def get_id(self) -> str:
        return self.__id

    def get_name(self) -> str:
        return self.__name

    def get_namespace(self) -> str:
        return self.__namespace

    def get_version(self) -> str:
        return self.__version

    def is_valid(self) -> bool:
        return self.__id and self.__name\
            and self.__namespace and self.__version

    def to_string(self) -> str:
        data: dict = self.__data
        dumped_data: str = dumps(data, indent=3)
        return dumped_data

    def blame(self) -> str:
        reports: list = []

        if not self.__id:
            reports.append("ID isn't valid.")
        if not self.__name:
            reports.append("Name isn't valid.")
        if not self.__namespace:
            reports.append("Namespace isn't valid.")
        if not self.__version:
            reports.append("Version isn't valid.")
        if not reports:
            reports.append("There is nothing to blame.")

        dumped_reports: str = dumps(reports, indent=3)
        return dumped_reports
