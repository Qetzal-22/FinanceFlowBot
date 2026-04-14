from enum import Enum

class EventOverflowBudget(Enum):
    NONE = "none"
    WARNING_80 = "warning_80"
    WARNING_90 = "warning_90"
    WARNING_100 = "warning_100"