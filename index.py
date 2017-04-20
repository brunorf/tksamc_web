from flask import Flask, render_template, Response, jsonify, request
from werkzeug.utils import secure_filename
import os
import hashlib
from datetime import datetime
import subprocess
import glob

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

        job_dir = 'jobs/{}'.format(datetime.today().strftime('%Y-%m-%d_%H:%M:%S:%f'))
        os.makedirs(job_dir)
        [ os.symlink(os.path.join('../../pulo_do_gato_bin', f), os.path.join(job_dir,f)) for f in os.listdir('pulo_do_gato_bin') ]


        file = request.files.get('input_file')
        filename = secure_filename(file.filename)
        file.save(os.path.join(job_dir, filename))

        cwd = os.getcwd()
        os.chdir(job_dir)
        print(os.getcwd())
        subprocess.call('python2 ./pulo_do_gato.py -T 20 -ph 3.4 -s MC -f 5vab.pdb > output.txt', shell=True)

        output_file = open('output.txt', 'r')
        image_filename = os
        return_data = jsonify(
            job_dir=job_dir,
            stdout=output_file.read(),
            image=glob.glob('*.jpg')[0],
            output=glob.glob('Output*.dat')[0]
        )
        output_file.close()

        os.chdir(cwd)

        return return_data
    else:
        return ''
