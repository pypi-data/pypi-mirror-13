import logging
import numpy as np

from .sankey_error import SankeyError


def define_variables(allocations):
    variables = set()
    for table in allocations:
        for node in table.columns:
            variables.add(node)
        for target, row in table.iterrows():
            variables.add(target)
            for source, value in row.dropna().items():
                variables.add('{}-{}'.format(source, target))
    variables = list(variables)
    logging.debug('Defined %s node variables and %s flows',
                  len([v for v in variables if '-' not in v]),
                  len([v for v in variables if '-' in v]))
    logging.debug('Variables:\n%s', '\n'.join(sorted(variables)))
    return variables


def allocation_constraints(variables, table):
    '''explicit outgoing flow balance'''
    constraints = []
    for source in table.columns:
        if any(allocation == '?' for allocation in table[source].values):
            logging.debug('Allocation from %s: outgoing flow balance', source)
            # need an outgoing flow balance
            row = np.zeros(len(variables))
            row[variables.index(source)] = 1
            for target, _ in table[source].dropna().items():
                row[variables.index('{}-{}'.format(source, target))] = -1
            constraints.append(row)
        else:
            # should add up to 1
            total = table[source].sum()
            if not np.isnan(total) and not (
                    abs(total) < 0.01 or abs(total - 1) < 0.01):
                raise SankeyError('Allocations from node {} do not sum to 1 (total = {:.2f})'
                                  .format(source, total),
                                  'Check the column of the allocation matrix headed "{}".'
                                  .format(source))

        for target, allocation in table[source].dropna().items():
            if allocation == '?':
                continue
            if allocation < 0 or allocation > 1:
                raise SankeyError('Bad allocation value: {} -> {} = {}'
                                  .format(source, target, allocation),
                                  'Check the entry in the allocation matrix.')
            # logging.debug('Allocation from %s to %s: fraction = %.2f', source, target, allocation)
            row = np.zeros(len(variables))
            row[variables.index(source)] = allocation
            row[variables.index('{}-{}'.format(source, target))] = -1
            constraints.append(row)
    return constraints


def incoming_sum_constraints(variables, table):
    '''implicit incoming flow balance'''
    constraints = []
    for target, allocations in table.iterrows():
        if allocations.dropna().empty:
            # source node
            # print('skipping node with no incoming flows: {}'.format(target))
            continue

        row = np.zeros(len(variables))
        row[variables.index(target)] = 1
        for source, _ in allocations.dropna().items():
            row[variables.index('{}-{}'.format(source, target))] = -1
        constraints.append(row)
    return constraints


def node_value_constraints(variables, node_values):
    constraints = []
    values = []
    for node, value in node_values.items():
        if not np.isfinite(value):
            raise SankeyError('Bad node value constraint: {} = {}'
                              .format(node, value),
                              'Check the Node Values sheet of the sankey file, or the '
                              'corresponding parameter value if used.')
        row = np.zeros(len(variables))
        row[variables.index(node)] = 1
        constraints.append(row)
        values.append(value)
    return constraints, values


def define_constraints(variables, allocations, node_values):
    constraints = []
    values = []

    # Allocation constraints
    for table in allocations:
        c = allocation_constraints(variables, table)
        logging.debug('Defining allocation constraints: %d constraints', len(c))
        constraints.extend(c)
        values.extend([0] * len(c))

        c = incoming_sum_constraints(variables, table)
        constraints.extend(c)
        values.extend([0] * len(c))

    # Node value constraints
    c, v = node_value_constraints(variables, node_values)
    constraints.extend(c)
    values.extend(v)

    return np.array(constraints), np.array(values)
