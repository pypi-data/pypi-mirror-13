import numpy as np


def define_variables(allocations):
    variables = set()
    for table in allocations:
        for node in table.columns:
            variables.add(node)
        for target, row in table.iterrows():
            variables.add(target)
            for source, value in row.dropna().items():
                variables.add('{}-{}'.format(source, target))
    return list(variables)


def allocation_observations(variables, table):
    '''explicit outgoing flow balance'''
    observations = []
    descriptions = []
    for source in table.columns:
        # if any(allocation == '?' for allocation in table[source].values):
        #     # need an outgoing flow balance
        #     row = np.zeros(len(variables))
        #     row[variables.index(source)] = 1
        #     for target, _ in table[source].dropna().items():
        #         row[variables.index('{}-{}'.format(source, target))] = -1
        #     constraints.append(row)
        #     descriptions.append('Outgoing sum at {}'.format(source))

        for target, allocation in table[source].dropna().items():
            if allocation == '?':
                continue
            row = np.zeros(len(variables))
            row[variables.index(source)] = allocation
            row[variables.index('{}-{}'.format(source, target))] = -1
            observations.append(row)
            descriptions.append('Allocation {} to {}'.format(source, target))
    return descriptions, observations


def outgoing_sum_constraints(variables, table):
    '''implicit outgoing flow balance'''
    constraints = []
    # descriptions = []
    for source in table.columns:
        allocations = table[source]
        if allocations.dropna().empty:
            # source node
            print('skipping node with no outgoing flows: {}'.format(source))
            continue

        row = np.zeros(len(variables))
        row[variables.index(source)] = 1
        for target, _ in table[source].dropna().items():
            row[variables.index('{}-{}'.format(source, target))] = -1
        constraints.append(row)
        # descriptions.append('Outgoing sum at {}'.format(source))
    return constraints


def incoming_sum_constraints(variables, table):
    '''implicit incoming flow balance'''
    constraints = []
    # descriptions = []
    for target, allocations in table.iterrows():
        if allocations.dropna().empty:
            # source node
            print('skipping node with no incoming flows: {}'.format(target))
            continue

        row = np.zeros(len(variables))
        row[variables.index(target)] = 1
        for source, _ in allocations.dropna().items():
            row[variables.index('{}-{}'.format(source, target))] = -1
        constraints.append(row)
        # descriptions.append('Incoming sum at {}'.format(target))
    return constraints


def node_value_observations(variables, node_values):
    observations = []
    values = []
    descriptions = []
    for node, value in node_values.items():
        row = np.zeros(len(variables))
        row[variables.index(node)] = 1
        observations.append(row)
        values.append(value)
        descriptions.append('Node value {}'.format(node))
    return descriptions, observations, values


def define_constraints(variables, allocations, node_values):
    zero_constraints = []
    observations = []
    descriptions = []
    values = []

    # Allocation constraints
    for table in allocations:
        desc, c = allocation_observations(variables, table)
        observations.extend(c)
        descriptions.extend(desc)
        values.extend([0] * len(c))

        c = incoming_sum_constraints(variables, table)
        zero_constraints.extend(c)

        c = outgoing_sum_constraints(variables, table)
        zero_constraints.extend(c)

    # Node value constraints
    desc, c, v = node_value_observations(variables, node_values)
    observations.extend(c)
    descriptions.extend(desc)
    values.extend(v)

    return np.array(zero_constraints), np.array(observations), np.array(values), descriptions
