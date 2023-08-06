import sys
import logging

import numpy as np
import argparse
import json

from .sankey_error import SankeyError
from .load_data import load_data, load_params, fill_in_params
from .constraints import define_variables, define_constraints


def solve_sankey(slices, allocations, node_values):
    variables = define_variables(allocations)
    c, v = define_constraints(variables, allocations, node_values)

    logging.debug('defined %s constraint matrix, %s values', c.shape, v.shape)
    if c.shape[0] < c.shape[1]:
        raise SankeyError(
            'Not enough constraints: {} variables, but only {} constraints'
            .format(c.shape[1], c.shape[0]),
            'It\'s hard to say where the problem is... Try adding more constraints '
            'or specifying more node values?')
    elif c.shape[0] > c.shape[1]:
        raise SankeyError(
            'Too many constraints: {} variables, but {} constraints'
            .format(c.shape[1], c.shape[0]),
            'This may be because you have specified node values which are connected '
            'by an allocation constraint. Try removing rows from the Node Values sheet?')

    try:
        solution = np.linalg.solve(c, v)
    except np.linalg.LinAlgError as err:
        if str(err) == 'Singular matrix':
            raise SankeyError('Singular constraint matrix',
                              'This means that, although you have the right number of constraints, '
                              'they do not adequately define the whole diagram. Try to look for '
                              'constraints which are not adding any additional information (you '
                              'could work them out from the allocations and other node values) '
                              'and remove them')
        else:
            raise SankeyError('Solution error: {}'.format(err))

    # Set small negative flows to zero
    solution[(solution < 1e-6) & (solution > -1e-6)] = 0

    if np.any(solution < 0):
        details = '\n'.join('    {:30s} = {:.2g}'.format(k, v)
                            for k, v in zip(variables, solution)
                            if v < 0)
        raise SankeyError(
            'Negative flows in solution',
            'A solution cannot be calculated because some flows would have to be negative '
            '(i.e. flow backwards):\n{}\n\n'.format(details) +
            'Check any constraints on node values which occur in slices to the right?')

    return {k: v for k, v in zip(variables, solution)}


def write_as_json(slices, solution, filename):
    nodes = [
        {"slice": "s{}".format(i), "id": n}
        for i, slice_nodes in enumerate(slices.values())
        for n in slice_nodes
    ]

    edge_values = ((k.split('-'), v) for k, v in solution.items())
    edge_values = ((k, v) for k, v in edge_values if len(k) == 2)
    edges = [
        {"source": a, "target": b, "values": [value]}
        for (a, b), value in edge_values
        if abs(value) > 0
    ]

    data = {
        "submodels": [
            {
                "id": "sankey",
                "nodes": nodes,
                "edges": edges,
            }
        ]
    }

    with open(filename, 'wt') as f:
        json.dump(data, f, indent=2)


def parse_arguments():
    parser = argparse.ArgumentParser(description='Sankey tool')
    parser.add_argument('spreadsheet')
    parser.add_argument('output')
    parser.add_argument('-p', '--params',
                        help='params spreadsheet')
    parser.add_argument('-v', '--verbose', default=0, action='count')
    return parser.parse_args()


def print_error(err):
    message, details = err.args if len(err.args) == 2 else (err.args[0], None)
    print('\n>>> {}\n'.format(message), file=sys.stderr)
    if details:
        print(details + '\n', file=sys.stderr)


def cli():
    args = parse_arguments()

    if args.verbose > 0:
        logging.basicConfig(level=logging.DEBUG)

    if args.params:
        parts = args.params.rsplit(':', 1)
        if len(parts) > 1:
            params_filename, params_column = parts
        else:
            params_filename, params_column = parts[0], 'Value'
        params = load_params(params_filename, params_column)
        logging.debug('loaded %d parameters from %s (column %s)',
                      len(params), params_filename, params_column)
    else:
        logging.debug('no parameters file given')
        params = None

    try:
        slices, allocations, node_values = load_data(args.spreadsheet)
        logging.debug('loaded data for %d slices from %s', len(slices), args.spreadsheet)
        if params is not None:
            fill_in_params(allocations, node_values, params)
            logging.debug('filled in parameter values')
        solution = solve_sankey(slices, allocations, node_values)
        logging.debug('solved sankey')
    except SankeyError as err:
        print_error(err)
        return 1

    write_as_json(slices, solution, args.output)
    logging.debug('wrote output to %s', args.output)


if __name__ == '__main__':
    import sys
    sys.exit(cli())
