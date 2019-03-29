# coding=utf-8

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import io
import json
import pickle
import sys
import traceback


def check_inference_output(result):
    from PIL import Image
    if not isinstance(result, dict):
        print('Inference result is not a dict, total fail. Sad!')
        return

    if 'success' not in result:
        print('Error: "success" field is not passed.')

    if 'error' not in result:
        print('Error: "error" field is not passed.')

    if 'content-type' not in result:
        print('Error: "content-type" is not passed.')

    if 'data' not in result:
        print('Error: "data" is not passed.')

    if result['success'] == False:
        print('Model has indicated that it failed, success = False')
        print(result['error'])

    if result['success'] == True:
        print('Good, model has indicated that it succeeded!')

        if result['content-type'] == 'application/json':
            print('attempting to parse json response')
            parsed = json.loads(result['data'])
            print('parsed json successfully!')
            print(parsed)
        elif result['content-type'] == 'image/jpeg':
            print('attempting to parse jpeg response')
            image = Image.open(io.BytesIO(result['data']))
            print('opened image succesfully, I guess its ok')
        else:
            print('Unknown response content type:' + result['content-type'])


def test_inference_function(inference_function=None, inputs_schema=None):
    from PIL import Image

    solid_color_image = Image.new("RGB", (600, 400), (200, 200, 200))
    test_image_bytes = io.BytesIO()
    solid_color_image.save(test_image_bytes, format='JPEG')
    test_image_bytes = test_image_bytes.getvalue()

    print('Attempting inference a few times....')

    for i in range(5):
        print('Attempting inference...')
        try:
            result = inference_function({
                'image': test_image_bytes
            })
        except Exception:
            print('fail, inference produced an exception:')
            traceback.print_exc()
            sys.exit(1)
        print('Inference finished. Now inspecting the result.')
        check_inference_output(result)

    print('All done, quitting.')


def test_model_integration(inference_function=None, inputs_schema=None):
    print('Entering model integration test mode')

    test_inference_function(inference_function=inference_function, inputs_schema=inputs_schema)


test_model_integration.hint = 'Test running the function on a single gray image (docker run flag: -e MODE=test_model_integration )'


def test_single_image(inference_function=None, inputs_schema=None):
    print('Entering single input test mode')

    image_data = sys.stdin.read()
    print("the image data has type: " + str(type(image_data)))
    print("got %d bytes of image data" % len(image_data))
    print('Attempting inference...')
    try:
        result = inference_function({
            'image': image_data
        })
    except Exception:
        print('fail, inference produced an exception:')
        traceback.print_exc()
        sys.exit(1)
    print('Inference finished. Now inspecting the result.')
    check_inference_output(result)


test_single_image.hint = 'Single image: Pipe your image in with <, as in: nvidia-docker run --rm -i -e MODE=test_single_image ...reponame... < George-W-Bush.jpeg '


def test_inputs_dict_json(inference_function=None, inputs_schema=None):
    print('Entering test single inputs dict mode')

    json_data = sys.stdin.read()
    print("my json data: " + str(json_data))
    print("the json data has type: " + str(type(json_data)))
    print("got %d bytes of json data" % len(json_data))
    inputs_dict = json.loads(json_data)
    print("json after applying json.loads and stringified" + str(inputs_dict))
    print("the type of inputs dict is now: " + str(type(inputs_dict)))
    print('Attempting inference...')
    try:
        result = inference_function(inputs_dict)
    except Exception:
        print('fail, inference produced an exception:')
        traceback.print_exc()
        sys.exit(1)
    print('Inference finished. Now inspecting the result.')
    check_inference_output(result)


test_inputs_dict_json.hint = 'Pipe your dict in as JSON, as in: echo \'{"text":"i am some json data"}\' | nvidia-docker run --rm -i -e MODE=test_inputs_dict_json ...reponame...  '


def test_inputs_pickled_dict(inference_function=None, inputs_schema=None):
    print('Entering test pickled dict mode')

    pkl_data = sys.stdin.buffer.read()
    print("the pkl_data has type: " + str(type(pkl_data)))
    print("got %d bytes of pickle data" % len(pkl_data))
    inputs_dict = pickle.loads(pkl_data)
    print('Attempting inference...')
    try:
        result = inference_function(inputs_dict)
    except Exception:
        print('fail, inference produced an exception:')
        traceback.print_exc()
        sys.exit(1)
    print('Inference finished. Now inspecting the result.')
    check_inference_output(result)


test_inputs_pickled_dict.hint = 'Create a pickled dict of inputs, save as dict.pkl.  Then pipe your dict in, as in: cat dict.pkl | nvidia-docker run --rm -i -e MODE=test_inputs_pickled_dict ...reponame...  '

MODULE_MODES = {
    'test_model_integration': test_model_integration,
    'test_single_image': test_single_image,
    'test_inputs_dict_json': test_inputs_dict_json,
    'test_inputs_pickled_dict': test_inputs_pickled_dict
}
