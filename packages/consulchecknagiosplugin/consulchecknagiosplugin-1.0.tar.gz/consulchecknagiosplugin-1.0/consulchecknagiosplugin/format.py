"""
Consul check formatting.
"""
from re import search


# The default output extraction pattern works well for certain LocationLabs use cases
# but might not be generally applicable (and can be overwritten with the --pattern argument).
#
# The "Output: " matching handles Consul's internal HTTP checks.
# The "result: " matching handles an internal/legacy check output format.
#
# Other output formats tend to "just work" as the fall through case.
DEFAULT_PATTERN = "(?:(.*) Output: .*)|(.* result: (.*))"


def output_to_line(output, pattern=".*", max_length=80):
    """
    Translate Consult check output to something Nagios friendly.

    Consul check output can be literally anything. At the same time, we don't want
    to show arbitrary text because newlines and other special characters won't show up well
    and very long output can obscure useful information.

    We use the following algorithm to extract a useful line of text:

        for each line of text
           continue if line does not match a regex
           return first eighty characters of match
        otherwise return first eight characters of first line
    """
    lines = output.split("\n")
    for line in lines:
        match = search(pattern, line)
        if not match:
            continue

        # use first matching line
        for group in match.groups():
            if group is not None:
                # use first matching group
                return group[:max_length]
        else:
            # use entire match
            return match.group(0)[:max_length]
    else:
        if lines:
            # fall through here
            return lines[0][:max_length]
        else:
            return None
