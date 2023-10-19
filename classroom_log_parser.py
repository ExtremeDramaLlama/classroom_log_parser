"""
Random notes about the log file:

At the start of every session is:
      Session Window Loaded
Which doesn't seem to be duplicated. Although I did find one that didn't have
any associated connections. Perhaps a different window logs that message as well?
Right before that (assuming it's a real session) are multiple:
  ConferenceManager_ConferenceMemberJoined! (<username> (<role>)
It looks like it shows me joining, does some setup, then shows
the other person joining, then me again, then the other person. Although I have
seen me, other person, me.

Note that <role> is either "Customer" or "Tutor."

At the end, normally it would show one person leaving, then the other, in short order.
      ConferenceManager_ConferenceMemberLeft! (<name>)

If an error occurs, it dumps the stacktrace into the log. These can be identified by lines
starting with a space, or being "Server stack trace:" or "Exception rethrown at [0]:". Or
just not starting with a digit.

To identify wage theft, I want to look for the customer leaving, and then me leaving,
but not for some time later. A few minutes later should cover any false positives,
although I should look at the actual data and find out what the average is.
"""

import re
from datetime import datetime, timedelta
from pathlib import Path
import os

TUTOR_CONNECTION = re.compile(
    r"ConferenceManager_ConferenceMemberJoined! \((.+)\(Tutor\)"
)
TUTOR_DISCONNECTION = re.compile(
    r"ConferenceManager_ConferenceMemberLeft! \((.+)\(Tutor\)"
)

CUSTOMER_CONNECTION = re.compile(
    r"ConferenceManager_ConferenceMemberJoined! \((.+)\(Customer\)"
)
CUSTOMER_DISCONNECTION = re.compile(
    r"ConferenceManager_ConferenceMemberLeft! \((.+)\(Customer\)"
)

TIMESTAMP = re.compile(r"^(\d{1,2}/\d{1,2}/\d{4} \d{1,2}:\d{2}:\d{2} (?:AM|PM))")

# How many minutes between the customer leaving and the tutor leaving before we
# decide that wage theft is happening. It shouldn't be instantly, because that
# would generate a lot of false positives. Note that as soon as you click "leave
# session", the "ConferenceMemberLeft!" message is logged, even though you can
# still see the session window behind the post-session survey window.
TIME_DELTA = 5


def parse_time(line: str) -> datetime:
    """
    Note that this is in US format -- I don't know if Classroom would log
    timestamps in another format if ran in a different locale.
    """
    match = TIMESTAMP.search(line)
    return datetime.strptime(match.group(0), "%m/%d/%Y %I:%M:%S %p")


class ChatStateMachine:
    def __init__(self):
        self.state = self.initial_state
        self.session_start_time = None
        self.customer_left_time = None
        self.customer_name_who_joined = ""
        self.customer_name_who_left = ""

    def initial_state(self, line: str):
        if self.customer_joined(line):
            self.state = self.initial_state
            return

        match = CUSTOMER_DISCONNECTION.search(line)
        if match:
            self.customer_name_who_left = match.group(1)
            self.customer_left_time = parse_time(line)
            self.state = self.customer_left

    def customer_left(self, line: str):
        # If the customer comes back, we want to reset the timer.
        if self.customer_joined(line):
            self.state = self.initial_state
            return

        # TODO: handle the tutor DCing and coming back (I assume it's possible?)

        if TUTOR_DISCONNECTION.search(line):
            tutor_left_time = parse_time(line)
            time_between_events = tutor_left_time - self.customer_left_time
            if time_between_events > timedelta(minutes=TIME_DELTA):
                information = (
                    f"Detected possible missing pay on {self.session_start_time}:\n"
                    f"  Customer: {self.customer_name_who_left}\n"
                    f"  Customer disconnect registered at {self.customer_left_time}\n"
                    f"  Tutor disconnect registered at {tutor_left_time}\n"
                    f"  Paid time: {self.customer_left_time - self.session_start_time}\n"
                    f"  Unpaid time: {time_between_events}\n"
                )
                print(information)
                # Clear the names to indicate that we're not in a session.
                self.customer_name_who_left = ""
                self.customer_name_who_joined = ""
                self.session_start_time = None
                self.customer_left_time = None

            self.state = self.initial_state

    def customer_joined(self, line: str) -> bool:
        """
        We want to keep track of when a session actually starts, so we can
        display some helpful information at the end. A connection will be logged
        multiple times if the customer DCs and reconnects (and often for no
        reason at all near the beginning of the session), so we check the name
        before overwriting the start time.

        There is an edge case where this will be problem: if classroom crashes
        (or if your computer shuts down suddenly) and classroom doesn't log the
        disconnect, AND the very next customer has the same name, then this
        parser will think it's part of the same session. But, it shouldn't
        actually generate a false positive because of that.
        """
        match = CUSTOMER_CONNECTION.search(line)
        if match:
            if match.group(1) != self.customer_name_who_joined:
                self.customer_name_who_joined = match.group(1)
                self.session_start_time = parse_time(line)
            return True
        return False

    def process(self, lines):
        for line in lines:
            self.state(line)


def main():
    appdata_dir = Path(os.getenv("LOCALAPPDATA"))
    log_dir = appdata_dir / "Tutor.com/Tutor.com Classroom"
    version_dirs = [x for x in log_dir.iterdir() if x.is_dir()]
    for directory in version_dirs:
        log_file = directory / "Log.txt"
        with open(log_file) as f:
            log_contents = f.read().split("\n")

        parser = ChatStateMachine()
        parser.process(log_contents)


main()
