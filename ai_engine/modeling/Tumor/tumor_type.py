from enum import Enum

class TumorType(Enum):
    BRAIN = 'brain'
    BREAST = 'breast'
    LUNG = 'lung'
    PROSTATE = 'prostate'
    @classmethod
    def from_string(cls, s):
        try:
            return cls[s]
        except KeyError:
            raise ValueError(f"'{s}' is not a valid TumorType")