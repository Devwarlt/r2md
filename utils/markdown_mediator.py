from models.workload import Workload
from models.project import Project
from models.cluster import Cluster
from utils.local_test_vars import LocalTestVars
from config import app_config
from datetime import datetime
from utils.logger import Log
from os.path import exists
from os import mkdir


class MarkdownMediator:
    _DEFAULT_DIR: str = 'reports'
    _DEFAULT_PATH: str = f'{_DEFAULT_DIR}/.r2md.snapshot-report-[ID].md'

    def __init__(self) -> None:
        pass

    @staticmethod
    def __load_all_templates(templates: dict) -> dict:
        log: Log = Log.get_singleton()
        log.info(
            "Gimme a sec... Let me organize these "
            "templates real quick!", origin='Markdown'
        )

        reports: dict = templates['reports']
        for key, value in reports.items():
            reports[key] = MarkdownMediator.__load_template(key, value)

        tables: dict = templates['tables']
        for key1, value1 in tables.items():
            table: dict = value1
            for key2, value2 in table.items():
                tables[key1][key2] = MarkdownMediator.__load_template(
                    f"{key1}-{key2}", value2)

        templates['reports'] = reports
        templates['tables'] = tables
        return templates

    @staticmethod
    def __load_template(template: str, path: str) -> str:
        log: Log = Log.get_singleton()
        log.info(
            f"Loading template '{template}' -> {path}",
            origin='Markdown'
        )
        with open(path, 'r') as file:
            return file.read()

    @staticmethod
    def __validate_serialized_data(clusters: list) -> bool:
        log: Log = Log.get_singleton()
        if not clusters:
            log.error(
                "D'oh! There is no cluster.",
                origin='Markdown'
            )
            return False

        for i in range(len(clusters)):
            cluster: Cluster = clusters[i]
            if not cluster.is_valid():
                log.error(
                    "D'oh! This cluster is invalid.",
                    origin='Markdown',
                    args={
                        'Cluster': cluster.to_string(),
                        'Blame': cluster.blame()
                    }
                )
                return False

            projects: list = cluster.get_projects()
            for j in range(len(projects)):
                project: Project = projects[j]
                if not project.is_valid():
                    log.error(
                        "D'oh! This project is invalid.",
                        origin='Markdown',
                        args={
                            'Project': project.to_string(),
                            'Blame': project.blame()
                        }
                    )
                    return False

                workloads: list = project.get_workloads()
                for k in range(len(workloads)):
                    workload: Workload = workloads[k]
                    if not workload.is_valid():
                        log.error(
                            "D'oh! This workload is invalid.",
                            origin='Markdown',
                            args={
                                'Workload': workload.to_string(),
                                'Blame': workload.blame()
                            }
                        )
                        return False
        return True

    @staticmethod
    def __get_unique_report_id() -> tuple:
        time: datetime = datetime.now()
        report_id: str = time.strftime('%Y-%m-%d %H.%M.%S.%f')
        template: str = MarkdownMediator._DEFAULT_PATH
        return time, template.replace('[ID]', report_id)

    @staticmethod
    def __save_report(path: str, content: str) -> None:
        with open(path, 'w') as file:
            file.write(content)

    @staticmethod
    def __keys_replace(reference: str, **kwargs: dict) -> str:
        for formatted_key, value in kwargs.items():
            formatted_key: str = f"[{formatted_key.upper()}]"
            formatted_key = formatted_key.replace(' ', '-')
            reference = reference.replace(formatted_key, str(value))
        return reference

    @staticmethod
    def __make_workloads_table(
        templates: dict, project: Project
    ) -> str:
        # Templates
        tables_template: dict = templates['tables']
        header_template: str = tables_template['workloads']['header']
        entry_template: str = tables_template['workloads']['entry']
        footer_template: str = tables_template['workloads']['footer']

        # Base URl from Rancher domain
        base_url: str = app_config['rancher']['base_url']

        table_header: str = header_template
        table: str = table_header
        table += "\n"

        table_entries: list = []

        workloads: list = project.get_workloads()
        for i in range(len(workloads)):
            workload: Workload = workloads[i]

            table_entry: str = entry_template
            table_entry = MarkdownMediator.__keys_replace(
                table_entry,
                **{
                    'base_url': base_url,
                    'project_id': project.get_id(),
                    'workload_id': workload.get_id(),
                    'workload_namespace': workload.get_namespace(),
                    'workload_name': workload.get_name(),
                    'workload_version': workload.get_version()
                }
            )
            table_entries.append(table_entry)

        table += "\n".join(table_entries)
        table += "\n"

        table_footer: str = footer_template
        table += table_footer
        return table

    @staticmethod
    def __make_project_report(
        templates: dict, cluster: Cluster, project: Project
    ) -> str:
        # Templates
        reports_template: dict = templates['reports']
        report_template: str = reports_template['project']

        report: str = report_template
        report = MarkdownMediator.__keys_replace(
            report,
            **{
                'project_name': project.get_name(),
                'cluster_name_lower': cluster.get_name().lower(),
                'project_id': project.get_id(),
                'workloads': MarkdownMediator.
                __make_workloads_table(templates, project)
            }
        )
        return report

    @staticmethod
    def __make_cluster_projects_table(
        templates: dict, cluster: Cluster
    ) -> str:
        # Templates
        tables_template: dict = templates['tables']
        header_template: str = tables_template['projects']['header']
        entry_template: str = tables_template['projects']['entry']
        footer_template: str = tables_template['projects']['footer']

        # Base URl from Rancher domain
        base_url: str = app_config['rancher']['base_url']

        table_header: str = header_template
        table_header = MarkdownMediator.__keys_replace(
            table_header,
            **{
                'cluster_name': cluster.get_name(),
                'cluster_id': cluster.get_id()
            }
        )
        table: str = table_header
        table += "\n"

        table_entries: list = []

        projects: list = cluster.get_projects()
        for i in range(len(projects)):
            project: Project = projects[i]
            name: str = project.get_name()

            table_entry: str = entry_template
            table_entry = MarkdownMediator.__keys_replace(
                table_entry,
                **{
                    'project_name_lower': name.lower(),
                    'base_url': base_url,
                    'project_id': project.get_id(),
                    'project_name': name,
                    'number_pods': project.get_total_pods()
                }
            )
            table_entries.append(table_entry)

        table += "\n".join(table_entries)
        table += "\n"

        table_footer: str = footer_template
        table_footer = MarkdownMediator.__keys_replace(
            table_footer,
            **{
                'cluster_name': cluster.get_name(),
                'projects': "\n\n".join(
                    MarkdownMediator
                    .__make_project_report(templates, cluster, project)
                    for project in projects
                )
            }
        )
        table += table_footer
        return table

    @staticmethod
    def __make_clusters_table(templates: dict, clusters: list) -> str:
        # Templates
        tables_template: dict = templates['tables']
        header_template: str = tables_template['clusters']['header']
        entry_template: str = tables_template['clusters']['entry']
        footer_template: str = tables_template['clusters']['footer']

        # Base URl from Rancher domain
        base_url: str = app_config['rancher']['base_url']

        table_header: str = header_template
        table: str = table_header
        table += "\n"

        table_entries: list = []

        for i in range(len(clusters)):
            cluster: Cluster = clusters[i]
            name: str = cluster.get_name()
            projects: list = cluster.get_projects()
            num_projects: int = len(projects)
            num_pods: int = cluster.get_total_pods()
            avg_num_pods: int = num_pods
            if num_projects > 1:
                avg_num_pods /= num_projects

            table_entry: str = entry_template
            table_entry = MarkdownMediator.__keys_replace(
                table_entry,
                **{
                    'cluster_name_lower': name.lower(),
                    'base_url': base_url,
                    'cluster_id': cluster.get_id(),
                    'cluster_name': name,
                    'number_projects': num_projects,
                    'avg_number_pods': f"{avg_num_pods:.3g}",
                    'number_pods': num_pods
                }
            )
            table_entries.append(table_entry)

        table += "\n".join(table_entries)
        table += "\n"

        table_footer: str = footer_template
        table_footer = MarkdownMediator.__keys_replace(
            table_footer,
            **{
                'projects': "\n".join(
                    MarkdownMediator
                    .__make_cluster_projects_table(templates, cluster)
                    for cluster in clusters
                )
            }
        )
        table += table_footer
        return table

    @staticmethod
    def __make_report(
        templates: dict, time: datetime, clusters: list
    ) -> str:
        # Timestamp
        creation_timestamp: str = time.strftime('%Y-%m-%d %H:%M:%S,%f')

        # Templates
        reports_template: dict = templates['reports']
        main_report_template: str = reports_template['main']

        # Make & fill clusters table
        clusters_table_info: str = MarkdownMediator\
            .__make_clusters_table(templates, clusters)

        # Make main report
        main_report: str = main_report_template
        main_report = MarkdownMediator.__keys_replace(
            main_report,
            **{
                'clusters': clusters_table_info,
                'creation_timestamp': creation_timestamp
            }
        )
        return main_report

    @staticmethod
    def build_report(clusters: list) -> None:
        log: Log = Log.get_singleton()

        if not MarkdownMediator.__validate_serialized_data(clusters):
            log.error(
                "Unable to build report without valid data!",
                origin='Markdown'
            )
            return

        if not exists(MarkdownMediator._DEFAULT_DIR):
            log.info(
                "Looks like it's your first time generating a report, "
                "let me create a new folder to save all snapshots.",
                origin='Markdown'
            )

            mkdir(MarkdownMediator._DEFAULT_DIR)

        log.info(
            "Great! All entries are valid to proceed with "
            "report building.", origin='Markdown'
        )

        templates: dict = app_config['templates']
        templates = MarkdownMediator.__load_all_templates(
            templates)

        time: datetime = None
        path: str = None
        time, path = MarkdownMediator.__get_unique_report_id()
        report = MarkdownMediator.__make_report(templates, time, clusters)
        MarkdownMediator.__save_report(path, report)

        clusters_data: list = []
        for i in range(len(clusters)):
            cluster: Cluster = clusters[i]
            clusters_data.append(cluster.to_string())

        ltv: LocalTestVars = LocalTestVars(__file__, 'entries')
        ltv.handle(clusters_data)

        log.info(
            f"Done! Your report is at '{path}'.",
            origin='Markdown'
        )
