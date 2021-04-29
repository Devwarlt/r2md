from utils.reload_credentials import ask_for_new_credentials
from utils.input_dialogs import yes_or_no_input_dialog
from extensions.url import format_url
from requests.models import Response
from utils.logger import Log
from config import app_config
from requests import get
from typing import Any
from json import loads


class RancherMediator:
    def __init__(self) -> None:
        pass

    @staticmethod
    def __get_response(path: str = '', **kwargs: dict) -> tuple:
        r_endpoint: str = app_config['rancher']['endpoint']
        r_username: str = app_config['rancher']['username']
        r_password: str = app_config['rancher']['password']
        params: dict = {'limit': 1000}
        args: dict = kwargs.get('args', {})
        if args:
            params.update(args)
        url: str = None
        if kwargs.get('raw'):
            url = path
        else:
            url = format_url(r_endpoint, path)
        payload: dict = {
            'url': url,
            'auth': (r_username, r_password),
            'verify': False,
            'params': params
        }
        result: Response = get(**payload)
        status_code: int = result.status_code
        content: dict = {}
        if len(result.content) != 0:
            content = loads(result.content)
        return status_code, content

    @staticmethod
    def __handle_bad_response(status_code: int, content: dict) -> None:
        log: Log = Log.get_singleton()
        log.error(
            "Something wrong happened!",
            origin='Rancher',
            args={
                'Status Code': status_code,
                'Message': content.get('message')
            }
        )

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
        log.info(
            "Hold on, let me validate your credentials to proceed...",
            origin='Rancher'
        )

        status_code: int = 0
        content: dict = {}
        status_code, content = RancherMediator.__get_response()
        if status_code != 200:
            log.error(
                "Unable to authenticate! Consider to check your credentials.",
                origin='Rancher',
                args={
                    'Status Code': status_code,
                    'Message': content.get('message')
                }
            )
            return False

        log.info(
            "Cool! I'm ready to use Rancher API :D",
            origin='Rancher'
        )
        return True

    @staticmethod
    def __try_fetch_clusters() -> bool:
        log: Log = Log.get_singleton()
        log.info(
            "Let me take a look into your clusters...",
            origin='Rancher'
        )

        status_code: int = 0
        content: dict = {}
        path: str = app_config['static']['clusters']
        status_code, content = RancherMediator.__get_response(path)
        if status_code != 200:
            RancherMediator.__handle_bad_response(status_code, content)
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

        RancherMediator.__add_key_value_pair('clusters', clusters)
        return True

    @staticmethod
    def __try_fetch_projects(cluster: dict) -> bool:
        cluster_id: str = cluster.get('id')
        cluster_name: str = cluster.get('name')

        log: Log = Log.get_singleton()
        log.info(
            "Seeking for all projects inside cluster "
            f"'{cluster_name}' [ID: {cluster_id}]...",
            origin='Rancher'
        )

        status_code: int = 0
        content: dict = {}
        path: str = f"{app_config['static']['clusters']}/{cluster_id}/projects"
        status_code, content = RancherMediator.__get_response(path)
        if status_code != 200:
            RancherMediator.__handle_bad_response(status_code, content)
            return False

        projects: list = []
        data: list = content.get('data')
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

    @staticmethod
    def __try_fetch_workloads(project: dict) -> bool:
        project_id: str = project.get('id')
        project_name: str = project.get('name')
        project_links: dict = project.get('links')

        log: Log = Log.get_singleton()
        log.info(
            "Seeking for all workloads inside project "
            f"'{project_name}' [ID: {project_id}]...",
            origin='Rancher'
        )

        status_code: int = 0
        content: dict = {}
        path: str = project_links.get('workloads')
        status_code, content = RancherMediator.__get_response(path, raw=True)
        if status_code != 200:
            RancherMediator.__handle_bad_response(status_code, content)
            return False

        workloads: list = []
        data: list = content.get('data')
        for i in range(len(data)):
            workload_data: dict = data[i]
            workload_id: str = workload_data.get('id')
            workload_name: str = workload_data.get('name')
            workload_containers: list = workload_data.get('containers', [])
            workload_namespace: str = workload_data.get('namespaceId')
            workload: dict = {
                'id': workload_id,
                'name': workload_name,
                'containers': workload_containers,
                'namespace': workload_namespace
            }
            workloads.append(workload)

        project['workloads'] = workloads
        return True

    @staticmethod
    def __try_wraps_version(workload: dict) -> bool:
        workload_containers: list = workload.get('containers')
        if not workload_containers:
            return False

        workload_version: str = None
        for i in range(len(workload_containers)):
            workload_container: dict = workload_containers[i]
            if not 'environment' in workload_container:
                continue

            container_image: str = workload_container.get('image')
            container_version_split: str = container_image.split(':')
            workload_version = container_version_split[1]
            break

        workload['version'] = workload_version
        return True

    @staticmethod
    def core() -> None:
        log: Log = Log.get_singleton()
        log.info(
            "Initializing internal services!",
            origin='Rancher'
        )

        while True:
            if not RancherMediator.__validate_credentials():
                if yes_or_no_input_dialog("Do you want to retry with new credentials?"):
                    ask_for_new_credentials()
                    continue
                else:
                    break

            if not RancherMediator.__try_fetch_clusters():
                log.error(
                    "Unable to fetch any cluster! Therefore, I cannot proceed...",
                    origin='Rancher'
                )
                break

            clusters: list = []
            _, clusters = RancherMediator.__try_get_value('clusters')

            log.info(
                "Clusters detected in Rancher!",
                origin='Rancher',
                args={'Number of clusters': len(clusters)}
            )

            for i in range(len(clusters)):
                cluster: dict = clusters[i]
                if not RancherMediator.__try_fetch_projects(cluster):
                    log.warning(
                        "Well... There is no project for "
                        f"cluster '{cluster.get('name')}'.",
                        origin='Rancher'
                    )
                    continue

                projects: list = cluster.get('projects')

                log.info(
                    f"Projects detected in cluster '{cluster.get('name')}'!",
                    origin='Rancher',
                    args={'Number of projects': len(projects)}
                )

                for i in range(len(projects)):
                    project: dict = projects[i]
                    if not RancherMediator.__try_fetch_workloads(project):
                        log.warning(
                            "Well... There is no workload for "
                            f"project '{project.get('name')}' "
                            f"from cluster '{cluster.get('name')}'.",
                            origin='Rancher'
                        )
                        continue

                    workloads: list = project.get('workloads')

                    log.info(
                        f"Workloads detected in project '{project.get('name')}'"
                        f" from cluster '{cluster.get('name')}'!",
                        origin='Rancher',
                        args={'Number of projects': len(workloads)}
                    )

                    for j in range(len(workloads)):
                        workload: dict = workloads[j]
                        if not RancherMediator.__try_wraps_version(workload):
                            log.warning(
                                "Well... There is no container for "
                                f"workload '{workload.get('name')}' "
                                f"in project '{project.get('name')}' "
                                f"from cluster '{cluster.get('name')}'.",
                                origin='Rancher'
                            )
                            continue
                RancherMediator.__try_update_value('clusters', clusters)
            break

        log.warning(
            "All services are preparing to shutdown...",
            origin='Rancher'
        )
