"""
Nagios Plugin resource(s).
"""
from json import loads
from logging import getLogger

from nagiosplugin import (
    CheckError,
    Metric,
    Resource,
)
from requests import get

from consulchecknagiosplugin.context import PassThroughContext


DEFAULT_HOST = "localhost"
DEFAULT_PORT = 8500

STATUSES = {
    "critical": 2,
    "passing": 0,
    "unknown": 3,
    "warning": 1,
}


def status_to_code(status):
    """
    Translate Consul's check status to a Nagios code.
    """
    return STATUSES.get(status, 3)


class ConsulCheckHealth(object):
    """
    Wrapper around Consul's node health check results.
    """
    def __init__(self, check_id, code, output):
        self.check_id = check_id
        self.code = code
        self.output = output

    @classmethod
    def from_dict(cls, dct):
        # body will be a list of dictionaries with keys:
        #  - Node
        #  - CheckID
        #  - ServiceName
        #  - Notes
        #  - Status
        #  - ServiceID
        #  - Output
        return cls(
            check_id=dct["CheckID"],
            code=status_to_code(dct["Status"]),
            output=dct["Output"],
        )

    def as_metric(self):
        return Metric(self.check_id, self, context=PassThroughContext.NAME)


class ConsulCheck(Resource):
    """
    Returns node-specific check status and output information (from Consul).
    """
    def __init__(self,
                 node,
                 check_id,
                 host=DEFAULT_HOST,
                 port=DEFAULT_PORT,
                 token=None):
        self.node = node
        self.check_id = check_id
        self.host = host
        self.port = port
        self.token = token
        self.logger = getLogger('nagiosplugin')

    @property
    def url(self):
        return "http://{}:{}/v1/health/node/{}?token=".format(
            self.host,
            self.port,
            self.node,
            self.token or ""
        )

    def get_node_health(self):
        """
        Query a Consul node for the health of all local checks.
        """
        self.logger.info("Query node health at url: '{}'".format(
            self.url,
        ))
        response = get(self.url)
        self.logger.debug("HTTP response was: '{} {}'".format(
            response.status_code,
            response.reason,
        ))
        response.raise_for_status()
        return {
            check["CheckID"]: ConsulCheckHealth.from_dict(check)
            for check in loads(response.text)
        }

    def get_check_health(self):
        """
        Query a Consul node for the health of a single check.

        Consul does not (yet?) have an API to query the outcome of a single check, so
        this function fetches all checks for a node and selects one.
        """
        node_health = self.get_node_health()
        try:
            return node_health[self.check_id]
        except KeyError:
            raise CheckError("No Consul data for check: '{}' on node '{}'".format(
                self.check_id,
                self.node,
            ))

    def probe(self):
        """
        Query consul for a specific check's health.

        Returns a metric with the checks status and output in its value.
        """
        value = self.get_check_health()
        self.logger.debug("Check health is: {} - {}".format(
            value.code,
            value.output,
        ))
        yield value.as_metric()
