import os
import traceback

from flask import Flask, request, render_template_string

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024 # 100mb max size


global_inference_function = None
global_inputs_schema = None

@app.route('/', methods=['GET', 'POST'])
def hello():
    global global_inference_function
    global global_inputs_schema
    if request.method == 'POST':
        inputs_dict = {}
        for key, value in global_inputs_schema.items():
            if key in request.files:
                inputs_dict[key] = request.files[key].read()
            elif key in request.form:
                inputs_dict[key] = request.form[key]
            else:
                return 'Input not provided: '+key

        print('Attempting inference...')
        try:
            result = global_inference_function(inputs_dict)
        except Exception:
            return 'fail, inference produced an exception:'+traceback.print_exc()

        if result['success'] == True:
            return result['data'], 200, {'Content-Type': result.get('content-type')}
        else:
            return 'Model indicated that it failed: '+ repr(result)

    return render_template_string('''
    <!doctype html>
    <title>Model Test</title>
    <h1>Test Model</h1>
    <form method=post enctype=multipart/form-data target='result_iframe'>
       {% for key, value in input_schema.items() %}
       
          Input {{key}}: 
          {% if value.type == 'image' %}
            <input type=file name={{key}}>
          {% else %}
            <input type=text name={{key}}>
          {% endif %}
          
          
          <br/>
       {% endfor %}
      
      <input type=submit value=Upload>
    </form>
    <iframe name="result_iframe" src="" style="width:100%; height:600px;"></iframe>

    ''', input_schema=global_inputs_schema
    )

def http(inference_function=None, inputs_schema=None):
    global global_inference_function
    global global_inputs_schema
    global_inference_function = inference_function
    global_inputs_schema = inputs_schema
    os.environ['FLASK_ENV']='development'
    app.run(debug=True, host='0.0.0.0', use_reloader=False)


http.hint = 'Run a HTTP Server with a simple web UI, docker run flags: -e MODE=http -p 5000:5000'

MODULE_MODES = {
    'http': http
}
