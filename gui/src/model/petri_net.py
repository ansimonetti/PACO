def get_targets(petri_net, component_id):
    """
    Given a Petri net and a component ID, return the target transitions or places
    :param petri_net: The Petri net dictionary
    :param component_id: The ID of the place or transition
    :return: A list of target IDs
    """
    component = None
    for place in petri_net['places']:
        if place['id'] == component_id:
            component = place
            break
    if not component:
        for transition in petri_net['transitions']:
            if transition['id'] == component_id:
                component = transition
                break
    if not component:
        return []

    return [arc['target'] for arc in petri_net['arcs'] if arc['source'] == component_id]


def get_choices_for_exclusive_gateway(petri_net, place_id):
    """
    Given a Petri net and a place ID, return the possible choices (transitions)
    :param petri_net: The Petri net dictionary
    :param place_id: The ID of the exclusive gateway place
    :return: A dictionary mapping transition labels to their IDs and probabilities
    """
    region_transitions = {}

    place_targets = get_targets(petri_net, place_id)
    for transition in place_targets:
        transition_targets = get_targets(petri_net, transition)
        transition_info = get_transition_info(petri_net, transition)
        if len(transition_targets) > 1:
            # TODO: log warning
            pass
        if not transition_info.get('stop', False):
            continue
        choice_place = get_place_info(petri_net, transition_targets[0])
        region_transitions[choice_place['label']] = dict(region_id=choice_place['entry_region_id'],
                                                         transition_id=transition,
                                                         probability=transition_info.get('probability', 0.5))

    return region_transitions

def get_loop_choices(petri_net, place_id, limit_reached):
    """
    Given a Petri net and a place ID, return the possible choices (transitions) for a loop
    If limit_reached is True, only return exit choices

    :param petri_net: The Petri net dictionary
    :param place_id: The ID of the loop place
    :param limit_reached: Boolean indicating if the visit limit has been reached
    :return: A dictionary of possible choices with their region IDs, transition IDs, and probabilities
    """
    region_transitions = {}

    place_targets = get_targets(petri_net, place_id)
    for transition in place_targets:
        transition_targets = get_targets(petri_net, transition)
        transition_info = get_transition_info(petri_net, transition)
        if len(transition_targets) > 1:
            # TODO: log warning
            pass

        if not transition_info.get('stop', False):
            continue

        choice_place = get_place_info(petri_net, transition_targets[0])

        is_exit = False
        region_id = choice_place.get('entry_region_id')
        if region_id is None:
            is_exit = True
            region_id = choice_place['exit_region_id']

        label = choice_place.get('label')
        if is_exit:
            label = f"Exit {label} (Limit reached)" if limit_reached else f"Exit {label}"

        if limit_reached and not is_exit:
            continue

        region_transitions[label] = dict(region_id=region_id,
                                         transition_id=transition,
                                         probability=transition_info.get('probability', 0.5))
    return region_transitions


def get_place_info(petri_net, place_id):
    """
    Given a Petri net and a place ID, return the place information

    :param petri_net: The Petri net dictionary
    :param place_id: The ID of the place
    :return: The place dictionary or None if not found
    """
    for place in petri_net['places']:
        if place['id'] == place_id:
            return place

    return None


def get_transition_info(petri_net, transition_id):
    """
    Given a Petri net and a transition ID, return the transition information
    :param petri_net: The Petri net dictionary
    :param transition_id: The ID of the transition
    :return: The transition dictionary or None if not found
    """
    for transition in petri_net['transitions']:
        if transition['id'] == transition_id:
            return transition

    return None


def get_pending_decisions(petri_net, marking):
    """
    Given a Petri net and a marking, return the pending decisions for gateways

    :param petri_net: The Petri net dictionary
    :param marking: The current marking dictionary
    :return: A dictionary mapping region labels to possible choices
    """
    # This function should analyze the petri_net and marking to find pending gateways
    # For simplicity, we will return a mock dictionary
    active_places = [place for place in marking if marking[place]['token'] > 0]
    pending_decisions = {}

    for place in active_places:
        place_info = get_place_info(petri_net, place)
        if place_info is None:
            continue
        region_label = place_info.get('label')
        if region_label is None:
            continue
        if place_info.get('region_type') not in ['choice', 'nature', 'loop']:
            # skip non-gateway places
            continue
        if marking[place]['age'] < place_info.get('duration', 0.0):
            # skip if not yet ready
            continue
        if place_info.get('region_type') == 'loop':
            visit_limit_reached = marking[place]['visit_count'] >= place_info.get('visit_limit', float('inf'))
            choices = get_loop_choices(petri_net, place_info['id'], visit_limit_reached)
        else:
            choices = get_choices_for_exclusive_gateway(petri_net, place_info['id'])
        if choices is not None and len(choices) > 0:
            pending_decisions[region_label] = choices

    return pending_decisions

def is_initial_marking(current_marking, petri_net):
    """
    Check if the current marking matches the initial marking

    :param current_marking: The current marking dictionary
    :param petri_net: The Petri net dictionary
    :return: True if current marking matches initial marking, False otherwise
    """
    initial_marking = petri_net['initial_marking']
    for place_id, initial_place in initial_marking.items():
        current_place = current_marking.get(place_id, {'token': 0})
        if current_place['token'] != initial_place['token']:
            return False
    return True

def is_final_marking(current_marking, petri_net):
    """
    Check if the current marking matches the final marking

    :param current_marking: The current marking dictionary
    :param petri_net: The Petri net dictionary
    :return: True if current marking matches final marking, False otherwise
    """
    final_marking = petri_net['final_marking']
    for place_id, final_place in final_marking.items():
        current_place = current_marking.get(place_id, {'token': 0})
        if current_place['token'] < final_place['token']:
            return False
    return True