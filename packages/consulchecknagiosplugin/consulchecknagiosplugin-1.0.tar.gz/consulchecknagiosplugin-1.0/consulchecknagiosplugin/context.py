"""
Nagios Plugin context(s).
"""
from nagiosplugin import (
    Context,
    Critical,
    Ok,
    Unknown,
    Warn,
)

from consulchecknagiosplugin.format import DEFAULT_PATTERN, output_to_line


STATES = {
    state.code: state for state in [Critical, Ok, Unknown, Warn]
}


class PassThroughContext(Context):
    """
    Context that reports another system's status verbatim.
    """

    NAME = "PASS"

    def __init__(self, pattern=DEFAULT_PATTERN):
        super(PassThroughContext, self).__init__(PassThroughContext.NAME)
        self.pattern = pattern

    def evaluate(self, metric, resource):
        """
        Evaluate the metric by passing its code through.
        """
        state = STATES.get(metric.value.code, Unknown)
        line = output_to_line(metric.value.output, self.pattern)
        return self.result_cls(state, line, metric)
