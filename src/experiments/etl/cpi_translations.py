from src.utils.env import (
    EXPRESSION,
    IMPACTS_NAMES,
    IMPACTS,
    DURATIONS,
    PROBABILITIES,
    DELAYS,
    LOOP_ROUND,
    LOOP_PROBABILITY,
    H,
)


def cpi_to_standard_format(cpi_dict):
    """
    Converts a CPI dictionary to a standardized format that includes:
    - TASK_SEQ: String representation of the process structure
    - IMPACTS_NAMES: List of impact names
    - IMPACTS: Dictionary mapping task names to impact values
    - DURATIONS: Dictionary mapping task names to duration ranges [0, duration]
    - PROBABILITIES: Dictionary mapping nature node names to probability values
    - DELAYS: Dictionary with delay value 1 for each choice
    - LOOP_ROUND: Empty dictionary (placeholder)
    - H: 0 (placeholder)
    
    Args:
        cpi_dict (dict): CPI dictionary representing a process
        
    Returns:
        dict: Standardized format dictionary
    """
    # Initialize result dictionaries
    result = {
        EXPRESSION: '',
        IMPACTS_NAMES: [],
        IMPACTS: {},
        DURATIONS: {},
        PROBABILITIES: {},
        DELAYS: {},
        LOOP_ROUND: {},
        LOOP_PROBABILITY: {},
        H: 0
    }
    
    # Collect all impact names from tasks
    all_impact_names = set()
    task_counter = 1
    choice_counter = 1
    nature_counter = 1
    
    # Mapping from region ID to standardized name
    name_mapping = {}
    
    # First pass: collect all tasks, impacts, and assign standardized names
    def first_pass(node):
        nonlocal task_counter, choice_counter, nature_counter
        
        if node['type'] == 'task':
            task_name = f"T{task_counter}"
            name_mapping[node['id']] = task_name
            task_counter += 1

            # Collect impacts
            if 'impacts' in node:
                for impact_name in node['impacts'].keys():
                    all_impact_names.add(impact_name)

            # Store duration
            result[DURATIONS][task_name] = [0, node['duration']]
            
        elif node['type'] == 'choice':
            choice_name = f"C{choice_counter}"
            name_mapping[node['id']] = choice_name
            choice_counter += 1

            result[DELAYS][choice_name] = 1
            
            # Process children
            first_pass(node['true'])
            first_pass(node['false'])
            
        elif node['type'] == 'nature':
            nature_name = f"N{nature_counter}"
            name_mapping[node['id']] = nature_name
            nature_counter += 1

            result[PROBABILITIES][nature_name] = node['probability']
            
            # Process children
            first_pass(node['true'])
            first_pass(node['false'])
            
        elif node['type'] == 'sequence':
            first_pass(node['head'])
            first_pass(node['tail'])
            
        elif node['type'] == 'parallel':
            first_pass(node['first_split'])
            first_pass(node['second_split'])
    
    # Second pass: build the TASK_SEQ string and populate IMPACTS
    def second_pass(node):
        if node['type'] == 'task':
            task_name = name_mapping[node['id']]
            
            # For each task, create an impacts list in the same order as IMPACTS_NAMES
            if 'impacts' in node:
                impacts_list = []
                for impact_name in result[IMPACTS_NAMES]:#Already sorted
                    impacts_list.append(node['impacts'].get(impact_name, 0))
                result[IMPACTS][task_name] = impacts_list
            else:
                # If no impacts, fill with zeros
                result[IMPACTS][task_name] = [0] * len(result[IMPACTS_NAMES])
                
            return task_name
            
        elif node['type'] == 'choice':
            choice_name = name_mapping[node['id']]
            true_branch = second_pass(node['true'])
            false_branch = second_pass(node['false'])
            return f"({true_branch} /[{choice_name}] {false_branch})"
            
        elif node['type'] == 'nature':
            nature_name = name_mapping[node['id']]
            true_branch = second_pass(node['true'])
            false_branch = second_pass(node['false'])
            return f"({true_branch} ^[{nature_name}] {false_branch})"
            
        elif node['type'] == 'sequence':
            head_str = second_pass(node['head'])
            tail_str = second_pass(node['tail'])
            return f"({head_str}, {tail_str})"
            
        elif node['type'] == 'parallel':
            first_str = second_pass(node['first_split'])
            second_str = second_pass(node['second_split'])
            return f"({first_str} || {second_str})"
    
    # Run first pass to collect metadata
    first_pass(cpi_dict)
    
    # Sort impact names and store them
    result[IMPACTS_NAMES] = sorted(list(all_impact_names))
    
    # Run second pass to build TASK_SEQ and populate IMPACTS
    result[EXPRESSION] = second_pass(cpi_dict)
    
    return result