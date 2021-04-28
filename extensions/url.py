from urllib.parse import SplitResult, urlsplit


def format_url(url: str, path: str) -> str:
    '''
    Format path to the current base endpoint.
    '''

    if path.startswith('/'):
        path = path[1:]
    endpoint: str = f'{url}/{path}'
    return endpoint


def get_base_url(full_url: str) -> str:
    '''
    Gets the base URL from a full URL.
    '''

    result: SplitResult = urlsplit(full_url)
    base_url: str = f"{result.scheme}://"
    base_url += result.netloc
    return base_url
