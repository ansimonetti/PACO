from typing import TypedDict, Dict, List
import enum

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
    if 'impacts_names' not in bpmn and 'impacts' in bpmn:
        names = set()
        for task in bpmn['impacts']:
            names.update(bpmn['impacts'][task].keys())
        bpmn['impacts_names'] = sorted(list(names))
    if 'h' not in bpmn:
        bpmn['h'] = 0

    required_keys = BPMNDict.__annotations__.keys()
    missing = [key for key in required_keys if key not in bpmn]

    if missing:
        raise ValueError(f"Missing required BPMN fields: {missing}")
    return bpmn


def get_active_region_by_pn(petri_net, marking):
    """
    Given a Petri net and a marking, return the set of active region IDs.
    A region is considered active if any of its entry places have tokens in the marking.

    :param petri_net: Petri net object
    :param marking: Current marking of the Petri net
    :return: Set of active region IDs
    """
    active_regions = set()

    for place in petri_net.get("places", []):
        place_id = place["id"]
        entry_region_id = place.get("entry_region_id")
        place_state = marking.get(place_id, {"token": 0})
        if entry_region_id is not None and place_state['token'] > 0:
            active_regions.add(entry_region_id)

    return active_regions

class ActivityState(enum.IntEnum):
    WILL_NOT_BE_EXECUTED = -1
    WAITING = 0
    ACTIVE = 1
    COMPLETED = 2
    COMPLETED_WITHOUT_PASSING_OVER = 3

    def __str__(self):
        if self.value > 2:
            return "Completed"
        return self.name.lower().replace("_", " ").capitalize()
