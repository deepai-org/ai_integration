# coding=utf-8

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import argparse
import sys
import traceback


def command_line(inference_function=None, inputs_schema=None):
    print('Entering command line mode')

    parser = argparse.ArgumentParser()

    for input in inputs_schema:
        parser.add_argument("--"+input, dest=input, type=argparse.FileType('rb'), required=True, help="Input file for {} input".format(input))

    parser.add_argument("--output", dest='output', type=argparse.FileType('wb'), required=False, help="Output file")

    args = parser.parse_args()

    inputs_dict = {}
    for input in inputs_schema:
        inputs_dict[input] = getattr(args, input).read()

    print('Attempting inference...')
    try:
        result = inference_function(inputs_dict)
    except Exception:
        print('fail, inference produced an exception:')
        traceback.print_exc()
        sys.exit(1)

    if result['success'] == True:
        print('Model indicated that it succeeded')
        if args.output:
            print('Writing output to file...')
            args.output.write(result['data'])
            args.output.close()
        else:
            print('No output file option passed, dumping to console')
            print(repr(result))
    else:
        print('Model indicated that it failed')
        print(repr(result))


command_line.hint = 'Pass file paths on the command line with options'

MODULE_MODES = {
    'command_line': command_line
}
