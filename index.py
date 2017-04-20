from flask import Flask
from flask import render_template
from flask import Response
from flask import jsonify
from flask import request


app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submit', methods=['GET','POST', 'PUT'])
def submit():
    # return request.args.get('pH', '')
    if request.method == 'POST':
        print(request.form.get('pH'))
        return ''
    else:
        return ''
