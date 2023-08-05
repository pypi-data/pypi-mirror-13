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
from nagiosplugin.output import Output

from consulchecknagiosplugin.format import DEFAULT_PATTERN, extract_line


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
        line = extract_line(metric.value.output, self.pattern)

        # nagiosplugin will warn about pipes in the output line because pipes are
        # normally used to separate context and performance data in line output
        #
        # ideally, we'd split on pipes and implement `performance(metric, resource)` here,
        # but since that requires some non-trivial parsing of data that might not actually
        # be performance data, we just remove pipes for now
        clean_line = line.replace(Output.ILLEGAL, "")

        return self.result_cls(state, clean_line, metric)
