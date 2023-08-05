import click


@click.group()
def cli():
    pass

from .register import register_check  # noqa

# Import checks here...
from .checks import cpu  # noqa
from .checks import load  # noqa

# Register checks here...
register_check(cpu.CPUCheck)
register_check(load.LoadCheck)

if __name__ == '__main__':
    cli()
