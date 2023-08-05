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
from consulchecknagiosplugin.resources import ConsulCheck, DEFAULT_HOST, DEFAULT_PORT


def make_check(host, port, token, pattern, node, check_id):
    return Check(
        ConsulCheck(
            node=node,
            check_id=check_id,
            host=host,
            port=port,
            token=token,
        ),
        PassThroughContext(
            pattern=pattern,
        ),
    )


@command()
@guarded
@option("-v", "--verbose", count=True)
@option("--host", default=DEFAULT_HOST, help="Consul host")
@option("--port", default=DEFAULT_PORT, help="Consul port")
@option("--token", help="Consul token")
@option("--pattern", default=DEFAULT_PATTERN, help="Check output extraction pattern")
@argument("node")
@argument("check-id")
def main(verbose, host, port, token, pattern, node, check_id):
    """
    Command line entry point. Defines common arguments.
    """
    check = make_check(host, port, token, pattern, node, check_id)
    return check.main(verbose)
