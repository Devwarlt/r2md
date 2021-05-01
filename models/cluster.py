from models.project import Project
from json import dumps


class Cluster(object):
    def __init__(self) -> None:
        pass

    def serialize(self, data: dict) -> None:
        self.__data: dict = data
        self.__id: str = data.get('id')
        self.__name: str = data.get('name')
        self.__projects: list = []

        projects_data: list = data.get('projects')
        for i in range(len(projects_data)):
            project_data: dict = projects_data[i]
            project: Project = Project()
            project.serialize(project_data)
            self.__projects.append(project)

    def get_id(self) -> str:
        return self.__id

    def get_name(self) -> str:
        return self.__name

    def get_projects(self) -> list:
        return self.__projects

    def get_total_pods(self) -> int:
        total_pods: int = 0

        for i in range(len(self.__projects)):
            project: Project = self.__projects[i]
            total_pods += len(project.get_workloads())

        return total_pods

    def is_valid(self) -> bool:
        return self.__id and self.__name and self.__projects

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
        if not self.__projects:
            reports.append("Projects aren't valid.")
        if not reports:
            reports.append("There is nothing to blame.")

        dumped_reports: str = dumps(reports, indent=3)
        return dumped_reports
