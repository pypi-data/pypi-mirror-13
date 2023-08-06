import numpy as np
from numpy import linalg
from scipy.optimize import nnls
import pandas as pd
import argparse
import json

from .load_data import load_data, load_params, fill_in_params
from .constraints import define_variables, define_constraints


def solve_sankey(slices, allocations, node_values, exact=False):
    variables = define_variables(allocations)
    B, A, b, desc = define_constraints(variables, allocations, node_values)

    Nfree = len(variables) - B.shape[0]
    print(Nfree, A.shape, B.shape)
    if A.shape[0] < Nfree:
        raise ValueError(
            'Not enough observations: {} free variables, but only {} observations ({} constraints)'
            .format(Nfree, A.shape[0], B.shape[0]))
    # elif c.shape[0] > c.shape[1]:
    #     if exact:
    #         raise ValueError(
    #             'Too many constraints: {} variables, but {} constraints'
    #             .format(c.shape[1], c.shape[0]))
    #     solution = least_squares_solution(c, v, desc)
    # else:
    #     solution = np.linalg.solve(c, v)
    solution, residuals = constrained_solution(A, b, B)

    residuals = pd.Series(abs(residuals), index=desc)
    residuals.sort_values(ascending=False, inplace=True)
    print(residuals)

    # Set small negative flows to zero
    solution[(solution < 0) & (solution > -1e-6)] = 0

    if np.any(solution < 0):
        raise ValueError(
            'Negative flows in solution:\n{}'.format(
                '\n'.join('    {:30s} = {:.2g}'.format(k, v)
                          for k, v in zip(variables, solution)
                          if v < 0)))

    return {k: v for k, v in zip(variables, solution)}


def constrained_solution(A, b, B):
    """
    A: observation matrix
    b: observation values
    B: constraint matrix
    d: constraint values assumed zero
    """

    # number of constraints
    p = B.shape[0]

    Qc, Rc = linalg.qr(B.T, mode='complete')
    AQc = np.dot(A, Qc)
    A1 = AQc[:, :p]
    A2 = AQc[:, p:]
    z, resid, A2rank, A2s = linalg.lstsq(A2, b)

    # Solve with non-negative values of z -- not right, since I want non-negative x
    # z, resid = nnls(A2, b)

    # solution
    x = np.dot(Qc, np.r_[np.zeros(p), z])

    # residuals
    residuals = np.dot(A, x) - b

    return x, residuals


def least_squares_solution(c, v, desc):
    x, residuals, rank, s = np.linalg.lstsq(c, v)
    print(x)
    print(residuals)
    print(rank)
    print(s)
    print('Condition number: {}'.format(s[0] / s[-1]))

    mismatch = pd.Series(np.abs(np.dot(c, x) - v), index=desc)
    mismatch.sort_values(ascending=False, inplace=True)
    print(mismatch)

    return x


def write_as_json(slices, solution, filename):
    nodes = [
        {"slice": i, "id": n}
        for i, slice_nodes in enumerate(slices.values())
        for n in slice_nodes
    ]

    edge_values = ((k.split('-'), v) for k, v in solution.items())
    edge_values = ((k, v) for k, v in edge_values if len(k) == 2)
    edges = [
        {"source": a, "target": b, "values": [value]}
        for (a, b), value in edge_values
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
    return parser.parse_args()


def cli():
    args = parse_arguments()
    slices, allocations, node_values = load_data(args.spreadsheet)

    if args.params:
        parts = args.params.rsplit(':', 1)
        if len(parts) > 1:
            params_filename, params_column = parts
        else:
            params_filename, params_column = parts[0], 'Value'
        params = load_params(params_filename, params_column)
    else:
        params = pd.Series()

    try:
        fill_in_params(allocations, node_values, params)
    except KeyError as err:
        print('Unknown parameter "{}"'.format(err.args[0]))
        return 1

    solution = solve_sankey(slices, allocations, node_values)
    write_as_json(slices, solution, args.output)


if __name__ == '__main__':
    import sys
    sys.exit(cli())
