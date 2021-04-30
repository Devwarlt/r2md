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
    def __build_clusters_table(
            reports: dict, tables: dict, entries: dict) -> str:
        header: str = tables['clusters']['header']
        entry: str = tables['clusters']['entry']
        footer: str = tables['clusters']['footer']
        report: str = header
        base_url: str = app_config['rancher']['base_url']
        clusters: list = entries.get('clusters')

        for i in range(len(clusters)):
            cluster: dict = clusters[i]
            cluster_report: str = entry
            cluster_id: str = cluster.get('id')
            cluster_name: str = cluster.get('name')
            cluster_projects: list = cluster.get('projects')
            number_pods: int = 0
            number_projects: int = len(cluster_projects)
            for j in range(len(cluster_projects)):
                cluster_project: dict = cluster_projects[j]
                cluster_project_pods: list = cluster_project.get('workloads')
                number_pods += len(cluster_project_pods)

            avg_number_pods: int = number_pods
            if number_projects > 1:
                avg_number_pods /= number_projects

            occurrences: dict = {
                '[BASE_URL]': base_url,
                '[CLUSTER_ID]': cluster_id,
                '[CLUSTER_NAME]': cluster_name,
                '[CLUSTER_NAME_LOWER]': cluster_name.lower().replace(' ', '-'),
                '[NUMBER_PROJECTS]': number_projects,
                '[NUMBER_PODS]': number_pods,
                '[AVG_NUMBER_PODS]': f"{avg_number_pods:.3g}"
            }
            cluster_report = MarkdownMediator.__dynamic_replace(
                cluster_report, occurrences)
            report += cluster_report

        report += "\n"
        # occurrences: dict = {
        #     '[PROJECTS]': all_projects_report
        # }
        # footer = MarkdownMediator.__dynamic_replace(footer, occurrences)
        report += footer
        return report

    @staticmethod
    def __build_projects_table(
            reports: dict, tables: dict, cluster: dict) -> str:
        header: str = tables['projects']['header']
        entry: str = tables['projects']['entry']
        footer: str = tables['projects']['footer']
        report: str = header
        base_url: str = app_config['rancer']['base_url']
        cluster_id: str = cluster.get('id')
        projects: list = cluster.get('projects')
        all_workloads_report: str = ""

        for i in range(len(projects)):
            project: dict = projects[i]
            project_report: str = entry
            project_id: str = project.get('id')
            project_name: str = project.get('name')
            project_workloads: list = project.get('workloads')
            workloads_report: str = MarkdownMediator.__build_workloads_table(
                tables, project)
            all_workloads_report += f"\n{workloads_report}"
            occurrences: dict = {
                '[BASE_URL]': base_url,
                '[CLUSTER_ID]': cluster_id,
                '[PROJECT_ID]': project_id,
                '[PROJECT_NAME]': project_name,
                '[PROJECT_NAME_LOWER]': project_name.lower().replace(' ', '-'),
                '[NUMBER_PODS]': len(project_workloads)
            }
            project_report = MarkdownMediator.__dynamic_replace(
                project_report, occurrences)
            report += project_report

        cluster_name: str = cluster.get('name')
        occurrences: dict = {
            '[CLUSTER_NAME]': cluster_name,
            '[PROJECTS]': all_workloads_report
        }
        footer = MarkdownMediator.__dynamic_replace(footer, occurrences)
        report += footer
        return report

    @staticmethod
    def __build_workloads_table(tables: dict, project: dict) -> str:
        header: str = tables['workloads']['header']
        entry: str = tables['workloads']['entry']
        footer: str = tables['workloads']['footer']
        report: str = header
        base_url: str = app_config['rancer']['base_url']
        project_id: str = project.get('id')
        workloads: list = project.get('workloads')

        for i in range(len(workloads)):
            workload: dict = workloads[i]
            workload_report: str = entry
            workload_id: str = workload.get('id')
            workload_name: str = workload.get('name')
            workload_version: str = workload.get('version')
            workload_namespace: str = workload.get('namespace')
            occurrences: dict = {
                '[BASE_URL]': base_url,
                '[PROJECT_ID]': project_id,
                '[WORKLOAD_ID]': workload_id,
                '[WORKLOAD_NAME]': workload_name,
                '[WORKLOAD_VERSION]': workload_version,
                '[WORKLOAD_NAMESPACE]': workload_namespace
            }
            workload_report = MarkdownMediator.__dynamic_replace(
                workload_report, occurrences)
            report += workload_report

        report += footer
        return report

    @staticmethod
    def __build_markdown(time: datetime, entries: dict) -> str:
        templates: dict = app_config['templates']
        reports: dict = templates['reports']
        tables: dict = templates['tables']
        creation_timestamp: str = time.strftime('%Y-%m-%d %H:%M:%S,%f')
        main_report: str = reports['main']
        clusters_report: str = MarkdownMediator.__build_clusters_table(
            reports, tables, entries)

        occurrences: dict = {
            '[CLUSTERS]': clusters_report,
            '[CREATION_TIMESTAMP]': creation_timestamp
        }
        main_report = MarkdownMediator.__dynamic_replace(
            main_report, occurrences)
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
        templates = MarkdownMediator.__load_all_templates(templates)
        app_config['templates'] = templates

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
