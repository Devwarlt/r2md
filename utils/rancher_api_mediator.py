from extensions.url import format_url
from typing import Any
from utils.reload_credentials import ask_for_new_credentials
from utils.input_dialogs import yes_or_no_input_dialog
from requests.models import Response
from config import app_config
from requests import get
from utils.logger import Log
from json import loads


class RancherAPIMediator:
    def __init__(self) -> None:
        pass

    @staticmethod
    def __get_response(path: str = '') -> tuple:
        r_endpoint: str = app_config['rancher']['endpoint']
        r_username: str = app_config['rancher']['username']
        r_password: str = app_config['rancher']['password']
        result: Response = get(
            format_url(r_endpoint, path),
            auth=(r_username, r_password),
            verify=False)
        status_code: int = result.status_code
        content: dict = {}
        if result.text:
            content = loads(result.text)
        return status_code, content

    @staticmethod
    def __add_key_value_pair(key: str, value: Any) -> None:
        internal: dict = app_config['internal']
        internal.update({key: value})
        app_config['internal'] = internal

    @staticmethod
    def __try_get_value(key: str) -> tuple:
        internal: dict = app_config['internal']
        if not key in internal:
            return False, None

        return True, internal.get(key)

    @staticmethod
    def __try_update_value(key: str, value: Any) -> bool:
        internal: dict = app_config['internal']
        if not key in internal:
            return False

        internal[key] = value
        app_config['internal'] = internal
        return True

    @staticmethod
    def __validate_credentials() -> bool:
        log: Log = Log.get_singleton()
        log.info("Hold on, let me validate your credentials to proceed...")

        status_code: int = 0
        content: dict = {}
        status_code, content = RancherAPIMediator.__get_response()
        if status_code != 200:
            log.error(
                "Unable to authenticate! Consider to check your credentials.",
                args={
                    'Status Code': status_code,
                    'Message': content.get('message')
                })
            return False

        log.info("Cool! I'm ready to use Rancher API :D")
        return True

    @staticmethod
    def __fetch_clusters() -> bool:
        log: Log = Log.get_singleton()
        log.info("Let me take a look into your clusters...")

        status_code: int = 0
        content: dict = {}
        path: str = app_config['static']['clusters']
        status_code, content = RancherAPIMediator.__get_response(path)
        if status_code != 200:
            log.error(
                "Something wrong happened!",
                args={
                    'Status Code': status_code,
                    'Message': content.get('message')
                })
            return False

        clusters: list = []
        data: list = content.get('data')
        for i in range(len(data)):
            cluster_data: dict = data[i]
            cluster_id: str = cluster_data.get('id')
            cluster_name: str = cluster_data.get('name')
            cluster: dict = {
                'id': cluster_id,
                'name': cluster_name
            }
            clusters.append(cluster)

        RancherAPIMediator.__add_key_value_pair('clusters', clusters)
        return True

    @staticmethod
    def __fetch_projects(cluster: dict) -> bool:
        cluster_id: str = cluster.get('id')
        cluster_name: str = cluster.get('name')

        log: Log = Log.get_singleton()
        log.info(
            "Seeking for all projects inside cluster "
            f"{cluster_name} [ID: {cluster_id}]...")

        status_code: int = 0
        content: dict = {}
        path: str = f"{app_config['static']['clusters']}"
        f"/{cluster_id}/projects"
        status_code, content = RancherAPIMediator.__get_response(path)
        if status_code != 200:
            log.error(
                "Something wrong happened!",
                args={
                    'Status Code': status_code,
                    'Message': content.get('message')
                })
            return False

        projects: list = []
        data: dict = content.get('data')
        for i in range(len(data)):
            project_data: dict = data[i]
            project_id: str = project_data.get('id')
            project_name: str = project_data.get('name')
            project_links: dict = project_data.get('links')
            project: dict = {
                'id': project_id,
                'name': project_name,
                'links': project_links
            }
            projects.append(project)

        cluster['projects'] = projects
        return True

    # @staticmethod
    # def __fetch_workloads

    @staticmethod
    def core() -> None:
        log: Log = Log.get_singleton()
        log.info("Initializing internal services!")

        while True:
            if not RancherAPIMediator.__validate_credentials():
                if yes_or_no_input_dialog("Do you want to retry with new credentials?"):
                    ask_for_new_credentials()
                    continue
                else:
                    break

            if not RancherAPIMediator.__fetch_clusters():
                log.error(
                    "Unable to fetch any cluster! Therefore, I cannot proceed...")
                break

            clusters: list = []
            _, clusters = RancherAPIMediator.__try_get_value('clusters')

            log.info(
                "Clusters found!",
                args={'Number of clusters': len(clusters)})

            for i in range(len(clusters)):
                cluster: dict = clusters[i]
                if not RancherAPIMediator.__fetch_projects(cluster):
                    log.warning(
                        "Well... There is no project for this cluster.")
                    continue

                projects: list = cluster.get('projects')
                for i in range(len(projects)):
                    project: dict = projects[i]

                RancherAPIMediator.__try_update_value('clusters', clusters)

            break

        log.warning("All services are preparing to shutdown...")
