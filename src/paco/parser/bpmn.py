
from typing import TypedDict, Dict, List

class BPMNDict(TypedDict):
    expression: str
    h: int
    impacts: Dict[str, List[float]]
    durations: Dict[str, List[int]]
    impacts_names: List[str]
    probabilities: Dict[str, float]
    delays: Dict[str, float]
    loop_round: Dict[str, int]
    loop_probability: Dict[str, float]


def validate_bpmn_dict(bpmn: dict) -> BPMNDict:
    required_keys = BPMNDict.__annotations__.keys()
    missing = [key for key in required_keys if key not in bpmn]
    if missing:
        raise ValueError(f"Missing required BPMN fields: {missing}")

    return bpmn
