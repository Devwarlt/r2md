def is_null_or_whitespace(string: str) -> bool:
    '''
    Verify if input string is null or contains
    whitespace characters.
    '''

    return not string\
        or string == ''\
        or string.isspace()


def is_any_null_or_whitespace(**kwargs: dict) -> bool:
    '''
    Verify if any input strings is null or contains
    whitespace characters from dictionary collection.
    '''

    return any(
        is_null_or_whitespace(v)
        for _, v in kwargs.items()
        if type(v) is None or str)
