from models.workload import Workload
from json import dumps


class Project(object):
    def __init__(self) -> None:
        pass

    def serialize(self, data: dict) -> None:
        self.__data: dict = data
        self.__id: str = data.get('id')
        self.__name: str = data.get('name')
        self.__workloads: list = []

        workloads_data: list = data.get('workloads')
        for i in range(len(workloads_data)):
            workload_data: dict = workloads_data[i]
            workload: Workload = Workload()
            workload.serialize(workload_data)
            self.__workloads.append(workload)

    def get_id(self) -> str:
        return self.__id

    def get_name(self) -> str:
        return self.__name

    def get_workloads(self) -> list:
        return self.__workloads

    def get_total_pods(self) -> int:
        total_pods: int = len(self.__workloads)
        return total_pods

    def is_valid(self) -> bool:
        return self.__id and self.__name and self.__workloads

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
        if not self.__workloads:
            reports.append("Workloads aren't valid.")
        if not reports:
            reports.append("There is nothing to blame.")

        dumped_reports: str = dumps(reports, indent=3)
        return dumped_reports
