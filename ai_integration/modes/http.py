import base64
import json
import os
import traceback

from flask import Flask, request, render_template_string

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100mb max size

SCRIPT_PATH = os.path.dirname(__file__)

global_inference_function = None
global_inputs_schema = None
global_visualizer_config = None


@app.route('/', methods=['GET', 'POST'])
def hello():
    global global_inference_function
    global global_inputs_schema
    if request.method == 'POST':
        inputs_dict = {}
        inputs_returned = []
        for key, value in global_inputs_schema.items():
            if key in request.files:
                inputs_dict[key] = request.files[key].read()
            elif key in request.form:
                inputs_dict[key] = request.form[key]
            else:
                return 'Input not provided: ' + key

            if value['type'] == 'image':
                inputs_returned.append({
                    'is_img': True,
                    'url': 'data:' + 'image/jpeg' + ';base64,' + base64.b64encode(inputs_dict[key]).decode("utf-8")
                    # mime type may not be right here
                })
            else:
                input_bytestr = inputs_dict[key]
                if hasattr(input_bytestr, 'encode'):
                    input_bytestr = input_bytestr.encode('utf-8')
                inputs_returned.append({
                    'is_img': False,
                    'url': 'data:' + 'text/plain' + ';base64,' + base64.b64encode(input_bytestr).decode("utf-8")
                })

        print('Attempting inference...')
        try:
            result = global_inference_function(inputs_dict)
        except Exception:
            return 'fail, inference produced an exception:' + traceback.print_exc()

        if result['success'] == True:

            res_content_type = result.get('content-type')

            output = None
            output_url = None

            if res_content_type and res_content_type.startswith('image'):
                output_url = 'data:' + res_content_type + ';base64,' + base64.b64encode(result['data'])
            elif res_content_type and 'json' in res_content_type:
                output = json.loads(result['data'])
            else:
                output = result['data']

            return json.dumps({
                'id': "0000-0000-0000-0000-000012345",
                'output_url': output_url,
                'scale_applied': 1,
                'inputs': inputs_returned,
                'output': output,
                "visualizer_data": global_visualizer_config
            }), 200, {'Content-Type': 'application/json'}

        else:
            return json.dumps({
                'err': repr(result)
            }), 200, {'Content-Type': 'application/json'}

    js_script = open(os.path.join(SCRIPT_PATH, 'http_helpers/deepai.js'), 'rb').read().decode('utf-8')

    return render_template_string('''
    <!doctype html>
    <title>Model Test</title>
    
    <script>{{ js_script|safe }}</script>
    
    <h1>Test Model</h1>
    <form method=post enctype=multipart/form-data id='inputs-form'>
       {% for key, value in input_schema.items() %}
       
          Input {{key}}: 
          {% if value.type == 'image' %}
            <input type=file name={{key}}>
          {% else %}
            <input type=text name={{key}}>
          {% endif %}
          
          
          <br/>
       {% endfor %}
      
    </form>
    
    <button onclick='uploadForm()'> Upload </button>
    <div id="result_div" src="" style="border:1px solid gray; width: 50%; height: 600px;"></div>
    
    <script>
    
    async function uploadForm(){
        var form = new FormData(document.getElementById('inputs-form'));

        var postResults = await fetch('/', {
          method: 'POST',
          body: form
        });
        
        postResults = await postResults.json();
        
        deepai.renderAnnotatedResultIntoElement(postResults, document.getElementById('result_div'));
    }
    
    
    </script>

    ''',
                                  input_schema=global_inputs_schema,
                                  js_script=js_script
                                  )


def http(inference_function=None, inputs_schema=None, visualizer_config=None):
    global global_inference_function
    global global_inputs_schema
    global global_visualizer_config
    global_inference_function = inference_function
    global_inputs_schema = inputs_schema
    global_visualizer_config = visualizer_config
    os.environ['FLASK_ENV'] = 'development'
    app.run(debug=True, host='0.0.0.0', use_reloader=False)


http.hint = 'Run a HTTP Server with a simple web UI, docker run flags: -e MODE=http -p 5000:5000'

MODULE_MODES = {
    'http': http
}
