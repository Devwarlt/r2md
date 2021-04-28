app_config: dict = {
    'name': 'R2MD',
    'log_level': 2,
    'description':
        "R2MD is a tool that wraps version details from all\n"
        "PODs via Rancher API and prettify results using\n"
        "Markdown notation.",
    'title':
        '\n'
        '\t██████╗░██████╗░███╗░░░███╗██████╗░\n'
        '\t██╔══██╗╚════██╗████╗░████║██╔══██╗\n'
        '\t██████╔╝░░███╔═╝██╔████╔██║██║░░██║\n'
        '\t██╔══██╗██╔══╝░░██║╚██╔╝██║██║░░██║\n'
        '\t██║░░██║███████╗██║░╚═╝░██║██████╔╝\n'
        '\t╚═╝░░╚═╝╚══════╝╚═╝░░░░░╚═╝╚═════╝░',
    'rancher': {
        'base_url': None,  # this is replaced during runtime
        'endpoint': None,  # this is replaced during runtime
        'username': None,  # this is replaced during runtime
        'password': None  # this is replaced during runtime
    },
    'static': {
        'api_keys': '/apikeys'
    }
}
