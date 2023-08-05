import sys

from .cli import cli


def register_check(cls):
    """
    Register a check as a click subcommand.
    Decorates the __init__ method on a check with click.command and applies options in cls.options.
    """

    name = cls.check_name()
    method_name = name.lower()

    def check_method(*args, **kwargs):
        return cls(*args, **kwargs)

    # Register options
    for option in cls.options:
        check_method = option(check_method)

    check_method.__doc__ = getattr(cls, 'description', "%s check" % method_name)
    check_method.__name__ = method_name
    setattr(sys.modules[__name__], check_method.__name__,
            cli.command(name=method_name)(check_method))
