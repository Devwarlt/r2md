app_config: dict = {
    'name': 'R2MD',
    'log_level': 2,
    'description':
        "R2MD is a tool that wraps version details from all PODs via\n"
        "Rancher API and prettify results using Markdown notation.",
    'title':
        '\n'
        '                                       *                     * \n'
        '                                      **                     **\n'
        '     ******************************** ******************    ***\n'
        '    ********************************  ****************** ******\n'
        '  ************************************......************       \n'
        ' ***  **************************************************       \n'
        '      ************************************** ***********       \n'
        '      ************************************** ***********       \n'
        '      ************************************** .**********       \n'
        '      ***********                       ***********            \n'
        '      ***********                       ***********            \n'
        '      ***********                       ***********            \n'
        '\n'
        f"{'-' * 63}\n"
        '\n'
        '             ██████╗░██████╗░███╗░░░███╗██████╗░\n'
        '             ██╔══██╗╚════██╗████╗░████║██╔══██╗\n'
        '             ██████╔╝░░███╔═╝██╔████╔██║██║░░██║\n'
        '             ██╔══██╗██╔══╝░░██║╚██╔╝██║██║░░██║\n'
        '             ██║░░██║███████╗██║░╚═╝░██║██████╔╝\n'
        '             ╚═╝░░╚═╝╚══════╝╚═╝░░░░░╚═╝╚═════╝░',
    'rancher': {
        'base_url': None,  # this is replaced during runtime
        'endpoint': None,  # this is replaced during runtime
        'username': None,  # this is replaced during runtime
        'password': None  # this is replaced during runtime
    },
    'static': {
        'api_keys': '/apikeys',
        'clusters': '/clusters',
        'report_template':
            '# R2MD - Snapshot report\n'
            '\n'
            '[![rancher-logo](https://raw.githubusercontent.com/Devwarlt/r2'
            'md/1887185f20e945d21685904177e79e9fb29e011a/rancher-logo.png)]'
            '(#r2md-snapshot-report)\n'
            '\n'
            '> This report was generated automatically by **R2MD - Rancher '
            'to Markdown** application at [CREATION_TIMESTAMP]. To contribu'
            'te visit the public repository [**here**](https://github.com/D'
            'evwarlt/r2md) :heart: .\n'
            '\n'
            '# Clusters\n'
            '\n'
            '[CLUSTERS]\n'
            '\n'
            '---\n'
            '\n'
            '*EOF*',
        'clusters_table_header_template':
            '| :notepad_spiral: '
            '| :link: '
            '| ID '
            '| Name '
            '| Total of projects '
            '| Total of workloads (avg.) '
            '| Total of workloads |\n'
            '| --- | --- | --- | --- | --- | --- | --- |\n',
        'clusters_table_entry_template':
            '| [**report**](#cluster-[CLUSTER_NAME]) '
            '| [visit]([BASE_URL]/c/[CLUSTER_ID]/monitoring) '
            '| `[CLUSTER_ID]` '
            '| `[CLUSTER_NAME]` '
            '| **[NUMBER_PROJECTS]** '
            '| **~[AVG_NUMBER_PODS] PODs**/project '
            '| **[NUMBER_PODS] PODs** |'
    },
    'internal': {}  # this is replaced during runtime
}
