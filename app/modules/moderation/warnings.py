from datetime import timedelta
from datetime import datetime

FIRST_WARNING = 1
FINAL_WARNING = 2
MUTE_WARNING = 3

def get_action(warns):

    if warns == FIRST_WARNING:
        return "first_warning"

    if warns == FINAL_WARNING:
        return "final_warning"

    if warns >= MUTE_WARNING:
        return "mute"

    return None