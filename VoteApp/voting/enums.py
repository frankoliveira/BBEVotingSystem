from enum import Enum

class CandidacyTypeEnum(Enum):
    Candidate = 1
    ElectoralPlate = 2 #chapa

class VoteTypeEnum(Enum):
    Valid = 1
    Null = 2

class ElectionPhaseEnum(Enum):
    PreVoting = 1
    Voting = 2
    PosVoting = 3

    @staticmethod
    def get_description(value: int) -> str:
        if value==1:
            return "Pré-votação"
        elif value==2:
            return "Votação"
        elif value==3:
            return "Pós-votação"
        else:
            None