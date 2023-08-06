from functools import partial
from contextlib import contextmanager

from colorama import Fore, Back


def function_name(s):
    return Fore.LIGHTYELLOW_EX + s + Fore.RESET


def param_name(s):
    return Fore.GREEN + s + Fore.RESET


def path_in(s):
    return Fore.GREEN + s + Fore.RESET


def path_out(s):
    return Fore.LIGHTRED_EX + s + Fore.RESET


def fn(tuples, cell):
    return cell.format(*tuples)


def multi_format(cell, dict, func=fn):
    return ''.join([func(each, cell) for each in dict])


def m_format(dict):
    f = partial(multi_format, cell='{}: {}\n', func=fn)
    return f(dict=dict)


@contextmanager
def ignored(*exceptions):
    try:
        yield
    except exceptions:
        pass
