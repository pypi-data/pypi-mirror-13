from . import __version__
from dodgy.checks import STRING_VALS, LINE_VALS, VAR_NAMES

full_check_list = (STRING_VALS, LINE_VALS, VAR_NAMES)
message = 'D000 Dodgy: {}'


def dodgy_checker(physical_line):
    """
    Check for possible scm markers, keys, secrets, passwords, and other
    "dodgy" looking code.

    Uses checks from
    https://github.com/landscapeio/dodgy/blob/master/dodgy/checks.py

    :param physical_line: The physical line as provided from flake8/pep8.
    :return: The position and message of a found issue, or None.
    """
    for check_list in full_check_list:
        for check in check_list:
            check = parse_check(check)

            # Match any regular expression in the group.
            if check['condition'] == any:

                for regex in check['regexps']:
                    match = regex.search(physical_line)
                    if match:
                        pos = match.start(0)
                        return pos, message.format(check['message'])

            # Match all regular expressions in the group.
            else:
                # Keep track of how many regular expressions match and the
                # position of the first match.
                match_count = 0
                first_position = None
                for regex in check['regexps']:
                    match = regex.search(physical_line)

                    if match:
                        match_count = match_count + 1
                        if first_position is None:
                            first_position = match.start(0)

                if match_count == len(check['regexps']):
                    return first_position, message.format(check['message'])

# Provide the metadata to flake8.
dodgy_checker.name = 'flake8_dodgy'
dodgy_checker.version = __version__


def parse_check(check):
    """
    Sort out the properties and types from the original dodgy check.
    :param check: A tuple or list from an individual check from dodgy.
    :return: A dict with key, message, regexps, and condition.
    :rtype: dict
    """

    # The dodgy checks have either 3 or 4 items.
    # Three items indicates a default condition of any.
    if len(check) == 3:
        key, msg, regexps = check
        cond = any
    else:
        key, msg, regexps, cond = check

    if not isinstance(regexps, (list, tuple)):
        regexps = [regexps]

    return {
        'key': key,
        'message': msg,
        'regexps': regexps,
        'condition': cond
    }
