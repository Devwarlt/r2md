from utils.local_test_vars import LocalTestVars
from config import app_config
from datetime import datetime
from utils.logger import Log
from os.path import exists
from json import dump
from os import mkdir


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
        report: str = app_config['static']['report_template']
        r_base_url: str = app_config['rancher']['base_url']
        clusters_report: str = app_config['static']['clusters_table_header_template']
        clusters: list = entries.get('clusters')
        for i in range(len(clusters)):
            cluster_template: str = app_config['static']['clusters_table_entry_template']
            cluster: dict = clusters[i]
            cluster_id: str = cluster.get('id')
            cluster_name: str = cluster.get('name')
            projects: list = cluster.get('projects')
            number_projects: str = str(len(projects))
            number_pods: int = 0
            for j in range(len(projects)):
                project: dict = projects[j]
                workloads: list = project.get('workloads')
                number_pods += len(workloads)
            avg_number_pods: int = number_pods / 2
            cluster_occurrences: dict = {
                '[BASE_URL]': r_base_url,
                '[CLUSTER_ID]': cluster_id,
                '[CLUSTER_NAME]': cluster_name,
                '[NUMBER_PROJECTS]': number_projects,
                '[AVG_NUMBER_PODS]': avg_number_pods,
                '[NUMBER_PODS]': number_pods
            }
            cluster_template = MarkdownMediator.__dynamic_replace(
                cluster_template, cluster_occurrences)
            clusters_report += cluster_template

        creation_timestamp: str = time.strftime('%Y-%m-%d %H:%M:%S,%f')
        report_occurrences: dict = {
            '[CREATION_TIMESTAMP]': creation_timestamp,
            '[CLUSTERS]': clusters_report
        }
        report = MarkdownMediator.__dynamic_replace(report, report_occurrences)
        return report

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
