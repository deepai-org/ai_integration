# coding=utf-8

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import argparse
import sys
import time
import traceback


def str2bool(v):
    if isinstance(v, bool):
        return v
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')


def command_line(inference_function=None, inputs_schema=None, visualizer_config=None):
    print('Entering command line mode')

    parser = argparse.ArgumentParser()
    parser.add_argument("--loop",
                        type=str2bool,
                        nargs='?',
                        const=True,
                        default=False,
                        help="Run the inference in a loop endlessly for performance testing."
                        )

    for input in inputs_schema:
        parser.add_argument("--" + input, dest=input, type=argparse.FileType('rb'), required=True,
                            help="Input file for {} input".format(input))

    parser.add_argument("--output", dest='output', type=argparse.FileType('wb'), required=False, help="Output file")

    args = parser.parse_args()

    inputs_dict = {}
    for input in inputs_schema:
        inputs_dict[input] = getattr(args, input).read()

    num_successes = 0
    tot_elapsed = 0.0
    while True:
        print('Attempting inference...')
        start_time = time.time()
        try:
            result = inference_function(inputs_dict)
        except Exception:
            print('fail, inference produced an exception:')
            traceback.print_exc()
            sys.exit(1)

        if result['success'] == True:
            print('Model indicated that it succeeded')
            end_time = time.time()
            elapsed_time = end_time - start_time
            num_successes += 1
            tot_elapsed += elapsed_time
            avg_time = tot_elapsed / num_successes
            qps = 1.0 / avg_time
            print('Inference took {:.3f} s, Average {:.3f} s, Average QPS {:.3f}'.format(elapsed_time, avg_time, qps))

            if args.output:
                if args.output.closed:
                    print('Not saving, file already closed')
                else:
                    print('Writing output to file...')
                    args.output.write(result['data'])
                    args.output.close()
            else:
                print('No output file option passed, dumping to console')
                print(repr(result))
        else:
            print('Model indicated that it failed')
            print(repr(result))

        if not args.loop:
            break # Only loop forever if the loop option was passed. Otherwise run once and quit.


command_line.hint = 'Pass file paths on the command line with options'

MODULE_MODES = {
    'command_line': command_line
}
