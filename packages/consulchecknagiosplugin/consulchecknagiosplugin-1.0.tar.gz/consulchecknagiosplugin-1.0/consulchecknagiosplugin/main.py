"""
Command line entry point.
"""
from click import argument, command, option
from nagiosplugin import (
    Check,
    guarded,
)


from consulchecknagiosplugin.context import PassThroughContext
from consulchecknagiosplugin.format import DEFAULT_PATTERN
from consulchecknagiosplugin.resources import ConsulNodeCheckStatus


@command()
@guarded
@option("-v", "--verbose", count=True)
@option("--host", default="localhost", help="Consul host")
@option("--port", default=8500, help="Consul port")
@option("--token", help="Consul token")
@option("--pattern", default=DEFAULT_PATTERN, help="Check output extraction pattern")
@argument("check-id")
def main(verbose, host, port, token, pattern, check_id):
    """
    Command line entry point. Defines common arguments.
    """
    check = Check(
        ConsulNodeCheckStatus(
            host=host,
            port=port,
            token=token,
            check_id=check_id,
        ),
        PassThroughContext(
            pattern=pattern,
        ),
    )
    check.main(verbose)
