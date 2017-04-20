from flask import Flask, render_template, Response, jsonify, request
from werkzeug.utils import secure_filename
import os
import hashlib
from datetime import datetime

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = set(['pdb'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submit', methods=['GET','POST', 'PUT'])
def submit():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'input_file' not in request.files:
            return redirect(request.url)

        print(request.files.get('input_file').filename)
        file = request.files.get('input_file')
        # filename = hashlib.sha512(file.read()).hexdigest() + '.pdb'
        filename = datetime.today().strftime('%Y-%m-%d_%H:%M:%S:%f_') + secure_filename(file.filename)

        if not os.path.isfile(os.path.join(app.config['UPLOAD_FOLDER'], filename)):
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return request.form.get('temperature')
    else:
        return ''
