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
        'clusters': '/clusters'
    },
    'internal': {}  # this is replaced during runtime
}
