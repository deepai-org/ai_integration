# ai_integration
[![PyPI version](https://badge.fury.io/py/ai-integration.svg)](https://badge.fury.io/py/ai-integration)
AI Model Integration for Python 2.7/3

# Purpose
### Expose your AI model under a standard interface so that you can run the model under a variety of usage modes and hosting platforms - all working seamlessly, automatically, with no code changes.
### Designed to be as simple as possible to integrate.

### Create a standard "ai_integration Docker Container Format" for interoperability.


![Diagram showing integration modes](https://yuml.me/diagram/plain;dir:RL/class/[Your%20Model]%20->%20[AI%20Integration],%20[AI%20Integration]<-[Many%20more%20coming!],%20[AI%20Integration]<-[DeepAI%20Platform],%20[AI%20Integration]<-[Pickle],%20[AI%20Integration]<-[JSON],%20[AI%20Integration]<-[HTTP%20API],%20[AI%20Integration]<-[Command%20Line].jpg)

# Built-In Usage Modes
There are several built-in modes for testing:

* Command Line using argparse (command_line)
* HTTP Web UI / multipart POST API using Flask (http)
* Pipe inputs dict as JSON (test_inputs_dict_json)
* Pipe inputs dict as pickle (test_inputs_pickled_dict)
* Pipe single image for models that take a single input named image (test_single_image)
* Test single image models with a built-in solid gray image (test_model_integration)

# Example Models
* [Tensorflow AdaIN Style Transfer](https://github.com/deepai-org/tf-adain-style-transfer)
* [Sentiment Analysis](https://github.com/deepai-org/sentiment-analysis)


# How to call the integration library from your code

(An older version of this library required the user to expose their model as an inference function, but this caused pain in users and is no longer needed.)

Run a "while True:" loop in your code and call "get_next_input" to get inputs.

Pass an inputs_schema (see full docs below) to "get_next_input".

See the specification below for "Inputs Dicts"

"get_next_input" needs to be called using a "with" block ad demonstrated below.

Then process the data. Format the result or error as described under "Results Dicts"

Then send the result (or error back) with "send_result".

## Simplest Usage Example

This example takes an image and returns a constant string without even looking at the input. It is a very bad AI algorithm for sure!

```python
import ai_integration

while True:
    with ai_integration.get_next_input(inputs_schema={"image": {"type": "image"}}) as inputs_dict:
        # If an exception happens in this 'with' block, it will be sent back to the ai_integration library
        result_data = {
            "content-type": 'text/plain',
            "data": "Fake output",
            "success": True
        }
        ai_integration.send_result(result_data)
        
        
```

# Docker Container Format Requirements:

####This library is intended to allow the creation of standardized docker containers. This is the standard:

1. Use the ai_integration library

2. You install this library with pip (or pip3)

3. CMD is used to set your python code as the entry point into the container.

4. No command line arguments will be passed to your python entrypoint. (Unless using the command line interface mode)

5. Do not use argparse in your program as this will conflict with command line mode.

To test your finished container's integration, run:
    * nvidia-docker run --rm -it -e MODE=test_model_integration YOUR_DOCKER_IMAGE_NAME
    * use docker instead of nvidia-docker if you aren't using NVIDIA...
    * You should see a bunch of happy messages. Any sad messages or exceptions indicate an error.
    * It will try inference a few times. If you don't see this happening, something is not integrated right.


# Inputs Dicts

inputs_dict is a regular python dictionary.

- Keys are input names (typically image, or style, content)
- Values are the data itself. Either byte array of JPEG data (for images) or text string.
- Any model options are also passed here and may be strings or numbers. Best to accept either strings/numbers in your model.



# Result Dicts

Content-type, a MIME type, inspired by HTTP, helps to inform the type of the "data" field

success is a boolean.

"error" should be the error message if success is False.


```python
{
    'content-type': 'application/json', # or image/jpeg
    'data': "{JSON data or image data as byte buffer}",
    'success': True,
    'error': 'the error message (only if failed)'
}   
```

# Error Handling

If there's an error that you can catch:
- set content-type to text/plain
- set success to False
- set data to None
- set error to the best description of the error (perhaps the output of traceback.format_exc())

# Inputs Schema

An inputs schema is a simple python dict {} that documents the inputs required by your inference function.

Not every integration mode looks at the inputs schema - think of it as a hint for telling the mode what data it needs to provide your function.

All mentioned inputs are assumed required by default.

The keys are names, the values specify properties of the input.

### Schema Data Types
- image
- text
- Suggest other types to add to the specification!

### Schema Examples

##### Single Image
By convention, name your input "image" if you accept a single image input
```python
{
    "image": {
        "type": "image"
    }
}
```

##### Multi-Image
For example, imagine a style transfer model that needs two input images.
```python
{
    "style": {
        "type": "image"
    },
    "content": {
        "type": "image"
    },    
}
```

##### Text
```python
{
    "sentence": {
        "type": "text"
    }
}
```

# Creating Usage Modes

A mode is a function that lives in a file in the modes folder of this library.


To create a new mode:

1. Add a python file in this folder
2. Add a python function to your file that takes two args:
    
    def http(inference_function=None, inputs_schema=None):
3. Attach a hint to your function
4. At the end of the file, declare the modes from your file (each python file could export multiple modes), for example:
```python
MODULE_MODES = {
    'http': http
}

```

Your mode will be called with the inference function and inference schema, the rest is up to you!

The sky is the limit, you can integrate with pretty much anything.

See existing modes for examples.



# Older Integration Mode

#### This documents the older way to use this library, identified by wrapping your model as a python function.

### Entrypoint Shims

Your docker entrypoint should be a simple python file (so small we call it a shim)
* imports start_loop from this library
* passes your inference function to it
* passes your inputs schema to it

The library handles everything else.



### Example Shim
If your inference function matches the specification, this would be the only code you have to write.

Assume that you put your model in a file called pretend_model.
```python
from ai_integration.public_interface import start_loop

from pretend_model import initialize_model, infer

initialize_model()

start_loop(inference_function=infer, inputs_schema={
    "image": {
        "type": "image"
    }
} )

```
inference_function should never intentionally throw exceptions.
- If an error occurs, set success to false and set the error field.
- If your inference function throws an Exception, the library will assume it is a bad issue and restart the script, so that the framework, CUDA, and everything else can reinitialize.
