import re
import pandas as pd
from collections import OrderedDict

from .sankey_error import SankeyError


def load_data(filename):
    xls = pd.ExcelFile(filename)
    assert 'Slices' in xls.sheet_names, 'missing Slices sheet'
    slice_sheets = [
        sheet_name for sheet_name in xls.sheet_names
        if sheet_name.startswith('Slice') and sheet_name != 'Slices']

    s = xls.parse('Slices')
    slices = OrderedDict([
        (col, list(s[col].dropna()))
        for col in s.columns
    ])
    all_nodes = sum(slices.values(), [])
    assert len(all_nodes) == len(set(all_nodes)), 'nodes not unique'

    allocations = [parse_allocation(xls, slices, sheet_name)
                   for sheet_name in slice_sheets]

    assert 'Node values' in xls.sheet_names, 'missing "Node values" sheet'
    node_values = xls.parse('Node values', index_col=0)['Value']

    return slices, allocations, node_values


def parse_allocation(xls, slices, sheet_name):
    s = xls.parse(sheet_name)
    slice_name = re.sub(r'^Slice[ -]*', '', sheet_name)
    assert slice_name in slices, 'Unknown slice {}'.format(slice_name)

    nodes = slices[slice_name]
    assert set(nodes) == set(s.columns), \
        '{}: Headings do not match Slice table'.format(sheet_name)

    # row headings should be next slice
    slice_names = list(slices.keys())
    i = slice_names.index(slice_name)
    assert i + 1 < len(slices), 'Allocation table for last slice'
    next_slice = slice_names[i+1]
    next_nodes = s.index
    assert set(next_nodes) == set(slices[next_slice]), \
        '{}: Rows do not match Slice table'.format(sheet_name)

    # Check all columns sum to either NaN or 1
    # XXX parameter values have not been replaced yet
    # assert (abs(s.sum().dropna() - 1) < 1e3).all(), \
    #     'columns do not sum to 1: {}'.format(sheet_name)

    return s


def load_params(filename, column='Value'):
    params = pd.read_excel(filename, index_col=0)
    params.index = [x.strip().lower() for x in params.index]
    return params[column]


def fill_in_params(allocations, node_values, params):
    try:
        for table in allocations:
            for target, row in table.iterrows():
                for source, allocation in row.items():
                    if isinstance(allocation, str) and allocation != '?':
                        key = allocation.strip().lower()
                        value = params[key]
                        if isinstance(value, pd.Series):
                            raise SankeyError('Multiple values given for parameter "{}"'.format(key),
                                            'The parameter was used in an allocation matrix. '
                                            'Check the parameters spreadsheet for duplicate rows.')
                        table.loc[target, source] = value

        for node, value in node_values.items():
            if isinstance(value, str):
                key = value.strip().lower()
                value = params[key]
                if isinstance(value, pd.Series):
                    raise SankeyError('Multiple values given for parameter "{}"'.format(key),
                                    'The parameter was used in the Node Values list. '
                                    'Check the parameters spreadsheet for duplicate rows.')
                node_values[node] = value

    except KeyError as err:
        raise SankeyError('Unknown parameter: {}'.format(err),
                          'Check it is spelled correctly and is present in the parameters sheet.')
