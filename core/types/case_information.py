from core.types.stage_type import StageType


class CaseInformation:
    def __init__(self, case: int):
        self.case = case
        self.episode = None
        self.step = None
        self.stage = None
