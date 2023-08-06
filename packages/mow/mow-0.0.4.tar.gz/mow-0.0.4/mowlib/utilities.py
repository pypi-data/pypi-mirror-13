import os
from functools import partial
import mowlib.configuration
import click
from .helpers import path_in, path_out, function_name, param_name


class Logger(object):
    _indentation = 0

    def __init__(self, params=None):
        self.params = params

    def indentation(self):
        return "\t" * (self.__class__._indentation - 1)

    def echo(self, func_name, **kwargs):
        p = None
        if self.params:
            lst = []
            for each in self.params.split(', '):
                # print(each)
                lst.append(kwargs[each])
            p = ', '.join(lst)

        if p:
            click.echo(self.indentation() + function_name(func_name) + ' ' + param_name(p))
        else:
            click.echo(self.indentation() + function_name(func_name))

    def __call__(self, f):
        def wrapped_f(*args, **kwargs):
            trace = mowlib.configuration.trace
            if trace > 0:
                self.__class__._indentation += 1
                if self.__class__._indentation <= trace:
                    self.echo(f.__name__, **kwargs)

                result = f(*args, **kwargs)
                self.__class__._indentation -= 1
                return result
            else:
                return f(*args, **kwargs)

        return wrapped_f


class Result:
    def __init__(self, value, is_success):
        self.value = value
        self.is_success = is_success

    @classmethod
    def failure(cls, failure_value):
        r = Result(value=failure_value, is_success=False)
        return r

    @classmethod
    def success(cls, success_value):
        r = Result(value=success_value, is_success=True)
        return r

    def __repr__(self):
        return "Result"


def log(msg):
    print(msg)


def format_filename(title, year, ext):
    return "{} ({}){}".format(title, year, ext)


def ensure_exists(path):
    if not os.path.exists(path):
        os.makedirs(path)
    return path


def m_format(zipped_data):
    p = partial(multi_format, cell='{0:>15}: {1}\n', func=fn)
    return p(zipped_data=zipped_data)


def multi_format(cell, zipped_data, func):
    return ''.join([func(each, cell) for each in zipped_data])


def fn(tuples, cell):
    return cell.format(*tuples)
