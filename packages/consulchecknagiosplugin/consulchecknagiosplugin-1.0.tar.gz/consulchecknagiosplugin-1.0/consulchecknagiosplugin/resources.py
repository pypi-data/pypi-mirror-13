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
    def __init__(self, code, output):
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
            code=status_to_code(dct["Status"]),
            output=dct["Output"],
        )


class ConsulNodeCheckStatus(Resource):
    """
    Returns node-specific check status and output information (from Consul).
    """
    def __init__(self,
                 host,
                 port,
                 token,
                 check_id):
        self.host = host
        self.port = port
        self.token = token
        self.check_id = check_id
        self.logger = getLogger('nagiosplugin')

    def get_node_health(self):
        """
        Query a Consul node for the health of all local checks.
        """
        url = "http://{}:{}/v1/health/node/{}?token=".format(
            self.host,
            self.port,
            self.host,
            self.token or ""
        )
        self.logger.info("Query node health at url: '{}'".format(
            url,
        ))
        response = get(url)
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
                self.host,
            ))

    def probe(self):
        """
        Query consul for a specific check's health.

        Returns a metric with the checks status and output in its value.
        """
        value = self.get_check_health()
        yield Metric(self.check_id, value, context=PassThroughContext.NAME)
