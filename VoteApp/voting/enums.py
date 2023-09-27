from enum import Enum

class OptionTypeEnum(Enum):
    Candidate = 1
    ElectoralPlate = 2 #chapa

class VoteTypeEnum(Enum):
    Valid = 1
    Blank = 2
    Null = 3
