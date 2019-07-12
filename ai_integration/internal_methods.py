# coding=utf-8
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import inspect
import os

import ai_integration.modes
from ai_integration.modes import *

DEBUG = False


def get_args_supported_by_function(x):
    if hasattr(inspect, 'getfullargspec'):
        # python3
        return inspect.getfullargspec(x).args
    return inspect.getargspec(x).args


def getValidKwargs(func, args):
    good_args = {}
    supported_args = get_args_supported_by_function(func)
    for arg in args:
        if arg in supported_args:
            good_args[arg] = args[arg]
        else:
            print('Warning, not passing this argument to the mode function:' + arg)

    return good_args


def _start_loop(inference_function=None, inputs_schema=None, visualizer_config=None):
    loaded_module_names = ai_integration.modes.__all__

    if DEBUG:
        print('Loaded these integration module files:')
        print(loaded_module_names)

    all_modes_by_name = {}

    for module_name in loaded_module_names:
        this_module = getattr(ai_integration.modes, module_name)
        this_modules_modes = getattr(this_module, 'MODULE_MODES', None)
        if this_modules_modes is None:
            if DEBUG:
                print('module exports no modes: ' + module_name)
            continue
        for name in this_modules_modes:
            all_modes_by_name[name] = this_modules_modes[name]

    if DEBUG:
        print('All loaded modes by name:')
        print(all_modes_by_name)

    chosen_mode = os.environ.get('MODE')

    if chosen_mode is None:
        print('No mode chosen - defaulting to command line and listing other integration modes:')
        for mode_name in sorted(all_modes_by_name.keys()):
            hint = getattr(all_modes_by_name[mode_name], 'hint', None)
            if hint:
                print(' * MODE={}: {}'.format(mode_name, hint))
            else:
                print(' * MODE={}: (No hint attached to this function)'.format(mode_name))
        chosen_mode = 'command_line'

    if chosen_mode not in all_modes_by_name:
        print('MODE not found: ' + str(chosen_mode))
        exit(1)

    mode_function = all_modes_by_name[chosen_mode]

    if inputs_schema is None:
        print(
            'Warning: No inputs schema was provided to start_loop. Using empty inputs schema. Some integration modes may not work, if they use the inputs schema!')

    all_keyword_args = {
        'inference_function': inference_function,
        'inputs_schema': inputs_schema,
        'visualizer_config': visualizer_config
    }

    # This passes only the supported named arguments to the mode function provided
    mode_function(**getValidKwargs(mode_function, all_keyword_args))

    print('Mode has exited cleanly: ' + chosen_mode)
    exit(0)
