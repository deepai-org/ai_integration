import sys
import time
import traceback
from contextlib import contextmanager
from threading import Thread
from multiprocessing import Queue

from internal_methods import  _start_loop

global background_thread
background_thread = None
global inputs_queue
inputs_queue = None
global outputs_queue
outputs_queue = None

MAX_QUEUE_LEN = 1

global waiting_for_user_code_response
waiting_for_user_code_response = False


def background_thread_handler(inputs_queue, outputs_queue, input_schema):
    print('Hello from background thread')

    # Runs in background (library) thread.
    def fake_inference_function(inputs_dict):
        inputs_queue.put(inputs_dict)

        return outputs_queue.get(block=True)

    print('About to start loop in background thread...')
    _start_loop(inference_function=fake_inference_function, inputs_schema=input_schema)
    print('_start_loop in background thread exited, now quitting whole process.')
    sys.exit(0)


# Runs in main (user) thread.
def send_result(results_dict):
    global outputs_queue
    global waiting_for_user_code_response
    waiting_for_user_code_response = False
    outputs_queue.put(results_dict)


# Runs in main (user) thread.
@contextmanager
def get_next_input(*args, **kwds):
    global waiting_for_user_code_response
    global background_thread
    global outputs_queue
    global inputs_queue

    if background_thread is None:
        print('Launching background thread')
        # First time calling - need to launch background thread
        #print('args {}, kwd {} '.format(args, kwds))
        input_schema = kwds.get('inputs_schema')
        if input_schema is None:
            print('WARNING: no input_schema passed to context manager.')
        inputs_queue = Queue(MAX_QUEUE_LEN)
        outputs_queue = Queue(MAX_QUEUE_LEN)
        background_thread = Thread(target=background_thread_handler,
                                    args=(inputs_queue, outputs_queue, input_schema,))
        background_thread.daemon = True
        background_thread.start()
        print('Launched background thread')

    inputs_dict = inputs_queue.get(block=True)
    print('Main thread got an input, now handing it to the users code')
    try:
        waiting_for_user_code_response = True
        yield inputs_dict
        print('User code returned')


        # The user's code must now call send_result before this returns.

    except Exception as e:
        print('User code threw an exception')
        print("ai_integration Context handler caught error, sending it back over the queue...", e)
        result_data = {
            "content-type": 'text/plain',
            "data": None,
            "success": False,
            "error": traceback.format_exc()
        }
        send_result(result_data)

        time.sleep(3)  # Wait a bit to allow the background thread to do something with the output before quitting...

        raise e

    # User should have called send_result or crashed with an exception...
    if waiting_for_user_code_response:
        # If the context manager is re-entered without responding - the user messed up and we should log this
        message = "Caught Programming Error - no success or error was received before the context manager exited"
        print(message)
        result_data = {
            "content-type": 'text/plain',
            "data": None,
            "success": False,
            "error": message
        }
        send_result(result_data)
    else:
        print('Good, we have a valid response after the end of the context manager.')
