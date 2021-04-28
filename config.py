app_config: dict = {
    'auth': (),  # this is replaced during runtime
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
        'url': 'https://rancher.fabrica.local',
        'endpoint': None,  # this is replaced during runtime
        'token': None  # this is replaced during runtime
    }
}
