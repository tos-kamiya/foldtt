#!/usr/bin/env python3

import sys
import os
import re
import tempfile
from typing import TextIO


VALUE_SEPARATOR_PAT = re.compile(r',\s*')


def expand_column_at_index(outp: TextIO, inp: TextIO, idx: int) -> (int, int):
    number_of_target_values = 0
    number_of_separated_values = 0
    for L in inp:
        while L and L[-1] in ('\r', '\n'):
            L = L[:-1]
        values = L.split('\t')
        if idx < len(values):
            separated_values = VALUE_SEPARATOR_PAT.split(values[idx])
            if len(separated_values) >= 2:
                number_of_separated_values += 1
            for sv in separated_values:
                values[idx] = sv
                print('\t'.join(values), file=outp)
            number_of_target_values += 1
        else:
            print('\t'.join(values), file=outp)
    
    return number_of_target_values, number_of_separated_values


class InvalidTargetLabel(ValueError):
    pass


def expand_column_at_label(outp: TextIO, inp: TextIO, label: str) -> (int, int):
    L = inp.readline()
    while L and L[-1] in ('\r', '\n'):
        L = L[:-1]
    labels = L.split('\t')
    for idx, lbl in enumerate(labels):
        if lbl == label:
            target_index = idx
            break  # for idx, label
    else:
        raise InvalidTargetLabel('Label not found in first line: %s' % repr(L))

    print('\t'.join(labels), file=outp)

    return expand_column_at_index(outp, inp, target_index)


def expand_column(outp, inp, cmd, silent=False):
    if cmd.startswith('I:'):
        target_index = int(cmd[2:])
        assert target_index >= 1
        r = expand_column_at_index(outp, inp, target_index - 1)
    elif cmd.startswith('L:'):
        target_label = cmd[2:]
        r = expand_column_at_label(outp, inp, target_label)
    else:
        assert False
    
    if not silent:
        number_of_target_values, number_of_separated_values = r
        if number_of_target_values == 0:
            print('> Warning: found no values to be separated.', file=sys.stderr)
        elif number_of_separated_values == 0:
            print('> Warning: None of the values were separated.', file=sys.stderr)


__doc__ = """Expand folded (text) table.

Usage:
  {argv0} --in-place [options] <cmd> <file>
  {argv0} [options] <cmd> [<file>]

Options:
  <cmd>         `I:<index>` to expand the column of the index, 1-based (1, 2, 3, ...). 
                `L:<label>` to expand the column of the label. Implicitly assume the 1st line contains labels of columns.
  -o FILE       Output file.
  --in-place    Overwrite given file.
  --silent      No warning messages.
""".format(argv0=os.path.basename(sys.argv[0]))


def main():
    import docopt
    args = docopt.docopt(__doc__)
    input_file = args['<file>']
    output_file = args['-o']
    cmd = args['<cmd>']
    option_in_place = args['--in-place']
    option_silent = args['--silent']
    assert re.match(r'^[IL]:.*$', cmd) is not None
    assert input_file is None or output_file is None or os.path.abspath(input_file) != os.path.abspath(output_file)

    if option_in_place:
        assert input_file is not None
        assert output_file is None
        inp = open(input_file, 'r')
        outp = tempfile.TemporaryFile()

        expand_column(outp, inp, cmd, silent=option_silent)

        outp.seek(0)
        with open(input_file, 'w') as p:
            for L in outp:
                p.write(L)
        outp.close()
    else:
        inp = open(input_file, 'r') if input_file is not None else sys.stdin
        outp = open(output_file, 'w') if output_file is not None else sys.stdout

        expand_column(outp, inp, cmd, silent=option_silent)

        if input_file is not None:
            inp.close()
        if output_file is not None:
            outp.close()


if __name__ == '__main__':
    main()
