from utils.local_test_vars import LocalTestVars
from config import app_config
from datetime import datetime
from utils.logger import Log
from os.path import exists
from os import mkdir

# Markdown Template structure:
# templates/reports/main.md
# |-> [CREATION_TIMESTAMP] <<datetime>>
# |-> [CLUSTERS] <<list>>
#     |-> templates/tables/clusters_header.md
#     |-> templates/tables/clusters_entry.md
#         |-> [CLUSTER_NAME_LOWER] <<str>>
#         |-> [BASE_URL] <<str>>
#         |-> [CLUSTER_ID] <<str>>
#         |-> [CLUSTER_NAME] <<str>>
#         |-> [NUMBER_PROJECTS] <<int>>
#         |-> [AVG_NUMBER_PODS] <<float>>
#         |-> [NUMBER_PODS] <<int>>
#     |-> templates/tables/clusters_footer.md
#         |-> [PROJECTS] <<list>>
#             |-> templates/tables/projects_header.md
#                 |-> [CLUSTER_NAME] <<str>>
#                 |-> [CLUSTER_ID] <<str>>
#             |-> templates/tables/projects_entry.md
#                 |-> [PROJECT_NAME_LOWER] <<str>>
#                 |-> [BASE_URL] <<str>>
#                 |-> [PROJECT_ID] <<str>>
#                 |-> [PROJECT_NAME] <<str>>
#                 |-> [NUMBER_PODS] <<int>>
#             |-> templates/tables/projects_footer.md
#                 |-> [CLUSTER_NAME] <<str>>
#                 |-> [PROJECTS] <<str>>
#                     |-> templates/reports/project.md
#                         |-> [CLUSTER_NAME_LOWER] <<str>>
#                         |-> [PROJECT_ID] <<str>>
#                         |-> [PROJECT_NAME] <<str>>
#                         |-> [WORKLOADS] <<list>>
#                             |-> templates/tables/workloads_header.md
#                             |-> templates/tables/workloads_entry.md
#                                 |-> [BASE_URL] <<str>>
#                                 |-> [PROJECT_ID] <<str>>
#                                 |-> [WORKLOAD_ID] <<str>>
#                                 |-> [WORKLOAD_NAMESPACE] <<str>>
#                                 |-> [WORKLOAD_NAME] <<str>>
#                                 |-> [WORKLOAD_VERSION] <<str>>
#                             |-> templates/tables/workloads_footer.md


class MarkdownMediator:
    _DEFAULT_DIR: str = 'reports'
    _DEFAULT_PATH: str = f'{_DEFAULT_DIR}/.r2md.snapshot-report-[ID].md'

    def __init__(self) -> None:
        pass

    @staticmethod
    def __validate_entries(entries: dict) -> bool:
        log: Log = Log.get_singleton()
        clusters: list = entries.get('clusters')
        if not clusters:
            log.error(
                "Well... There is no cluster into entries.",
                origin='Markdown'
            )
            return False

        for i in range(len(clusters)):
            cluster: dict = clusters[i]
            projects: list = cluster.get('projects')
            if not projects:
                log.error(
                    "Well... There is no project into cluster "
                    "from entries.", origin='Markdown'
                )
                return False

            for j in range(len(projects)):
                project: dict = projects[j]
                workloads: list = project.get('workloads')
                if not workloads:
                    log.error(
                        "Well... There is no workload into project "
                        "at cluster from entries.", origin='Markdown'
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
    def __dynamic_replace(reference: str, occurrences: dict) -> str:
        for key, value in occurrences.items():
            reference = reference.replace(key, str(value))
        return reference

    @staticmethod
    def __build_markdown(time: datetime, entries: dict) -> str:
        # Timestamp
        creation_timestamp: str = time.strftime('%Y-%m-%d %H:%M:%S,%f')

        # Base URl from Rancher domain
        base_url: str = app_config['rancher']['base_url']

        # Templates
        templates: dict = app_config['templates']
        reports: dict = templates['reports']
        tables: dict = templates['tables']

        # Reports templates
        main_report: str = reports['main']
        project_report: str = reports['project']

        # Cluster templates
        clusters_header: str = tables['clusters']['header']
        clusters_entry: str = tables['clusters']['entry']
        clusters_footer: str = tables['clusters']['footer']
        clusters_report: str = clusters_header

        clusters_projects_report: str = ""
        clusters: list = entries.get('clusters')

        for i in range(len(clusters)):
            # Cluster info
            cluster: dict = clusters[i]
            cluster_report: str = f"\n{clusters_entry}"
            cluster_id: str = cluster.get('id')
            cluster_name: str = cluster.get('name')
            cluster_project_number_pods: int = 0

            # Cluster projects info
            cluster_projects: list = cluster.get('projects')
            cluster_projects_header: str = tables['projects']['header']
            cluster_projects_report: str = cluster_projects_header
            cluster_projects_report_occurrences: dict = {
                '[CLUSTER_NAME]': cluster_name,
                '[CLUSTER_ID]': cluster_id
            }
            cluster_projects_report = MarkdownMediator.__dynamic_replace(
                cluster_projects_report,
                cluster_projects_report_occurrences
            )
            cluster_projects_entry: str = tables['projects']['entry']

            # Extra cluster + cluster projects info
            cluster_number_projects: int = len(cluster_projects)
            cluster_project_entry_reports: str = ""

            for j in range(cluster_number_projects):
                # Handle overall project stats per cluster
                cluster_project: dict = cluster_projects[j]
                cluster_project_id: str = cluster_project.get('id')
                cluster_project_name: str = cluster_project.get('name')
                cluster_project_pods: list = cluster_project.get('workloads')
                cluster_project_number_pods += len(cluster_project_pods)
                cluster_project_report: str = f"\n{cluster_projects_entry}"
                cluster_project_pods_number: int = len(cluster_project_pods)
                cluster_project_occurrences: dict = {
                    '[BASE_URL]': base_url,
                    '[PROJECT_ID]': cluster_project_id,
                    '[PROJECT_NAME]': cluster_project_name,
                    '[NUMBER_PODS]': cluster_project_pods_number,
                    '[PROJECT_NAME_LOWER]': cluster_project_name.lower().replace(' ', '-')
                }
                cluster_project_report = MarkdownMediator.__dynamic_replace(
                    cluster_project_report,
                    cluster_project_occurrences
                )
                cluster_projects_report += cluster_project_report

                # Handle each project entry report per cluster
                cluster_project_entry_report: str = project_report
                cluster_project_entry_report_occurrences: dict = {
                    '[PROJECT_ID]': cluster_project_id,
                    '[PROJECT_NAME]': cluster_project_name,
                    '[CLUSTER_NAME_LOWER]': cluster_name.lower().replace(' ', '-'),
                    # '[WORKLOADS]': cluster_project_workloads_report
                }
                cluster_project_entry_report = MarkdownMediator.__dynamic_replace(
                    cluster_project_entry_report,
                    cluster_project_entry_report_occurrences
                )
                cluster_project_entry_reports += cluster_project_entry_report

            cluster_project_avg_number_pods: int = cluster_project_number_pods
            if cluster_number_projects > 1:
                cluster_project_avg_number_pods /= cluster_number_projects

            # Append cluster report to clusters report
            cluster_report_occurrences: dict = {
                '[BASE_URL]': base_url,
                '[CLUSTER_ID]': cluster_id,
                '[CLUSTER_NAME]': cluster_name,
                '[CLUSTER_NAME_LOWER]': cluster_name.lower().replace(' ', '-'),
                '[NUMBER_PROJECTS]': cluster_number_projects,
                '[NUMBER_PODS]': cluster_project_number_pods,
                '[AVG_NUMBER_PODS]': f"{cluster_project_avg_number_pods:.3g}"
            }
            cluster_report = MarkdownMediator.__dynamic_replace(
                cluster_report,
                cluster_report_occurrences
            )

            # Append cluster report to clusters reports
            clusters_report += f"{cluster_report}\n"

            cluster_projects_footer: str = tables['projects']['footer']
            cluster_projects_footer_occurrences = {
                '[CLUSTER_NAME]': cluster_name,
                '[PROJECTS]': cluster_project_entry_reports
            }
            cluster_projects_footer = MarkdownMediator.__dynamic_replace(
                cluster_projects_footer,
                cluster_projects_footer_occurrences
            )
            cluster_projects_report += f"\n{cluster_projects_footer}"

            # Append cluster projects report to clusters projects reports
            clusters_projects_report += cluster_projects_report

        clusters_footer_occurrences: dict = {
            '[PROJECTS]': clusters_projects_report
        }
        clusters_footer = MarkdownMediator.__dynamic_replace(
            clusters_footer,
            clusters_footer_occurrences)
        clusters_report += clusters_footer

        main_report_occurrences: dict = {
            '[CLUSTERS]': clusters_report,
            '[CREATION_TIMESTAMP]': creation_timestamp
        }
        main_report = MarkdownMediator.__dynamic_replace(
            main_report,
            main_report_occurrences
        )
        return main_report

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
    def build_report(entries: dict) -> None:
        log: Log = Log.get_singleton()

        if not entries:
            log.error(
                "Unable to build report without entries! "
                "Therefore, I cannot proceed...",
                origin='Markdown'
            )
            return

        if not MarkdownMediator.__validate_entries(entries):
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
        app_config['templates'] = MarkdownMediator.__load_all_templates(
            templates)

        time: datetime = None
        path: str = None
        time, path = MarkdownMediator.__get_unique_report_id()
        report = MarkdownMediator.__build_markdown(time, entries)
        MarkdownMediator.__save_report(path, report)

        ltv: LocalTestVars = LocalTestVars(__file__, 'entries')
        ltv.handle(entries)

        log.info(
            f"Done! Your report is at '{path}'.",
            origin='Markdown'
        )
