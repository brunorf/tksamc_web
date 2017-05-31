#!/usr/bin/python3

from flask import Flask, render_template, Response, jsonify, request, send_from_directory
from werkzeug.utils import secure_filename
import os
import hashlib
from datetime import datetime
import subprocess
import glob
import smtplib
import smtpconfig

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = set(['pdb'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER



# os.chdir('/var/www/html/pdg/pdg')
os.chdir('/home/bruno/Projetos/pdg/pdg')


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def send_email(to, job_id):
    msg = "\r\n".join([
        "From: " + smtpconfig.FROM,
        "To: " + to,
        "Subject: " + smtpconfig.SUBJECT + str(job_id),
        "",
        "Why, oh why"
        ])
    try:
        smtp = smtplib.SMTP(smtpconfig.SERVER, smtpconfig.SERVER_PORT)
        smtp.ehlo()
        smtp.starttls()
        smtp.login(smtpconfig.LOGIN, smtpconfig.PASSWORD)
        smtp.sendmail(smtpconfig.FROM, to, msg)
        smtp.close()
    except:
        print("Error")

@app.route('/jobs/<path:job_dir>/<path:filename>')
def custom_static(job_dir,filename):
    return send_from_directory('jobs/' + job_dir, filename)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submit', methods=['GET','POST', 'PUT'])
def submit():
    if request.method == 'POST':
        # check if the post request has the file part
        # if 'input_file' not in request.files:
            # return redirect(request.url)

        job_dir = 'jobs/{}'.format(datetime.today().strftime('%Y-%m-%d_%H:%M:%S:%f'))
        os.makedirs(job_dir)
        [ os.symlink(os.path.join('../../pulo_do_gato_bin', f), os.path.join(job_dir,f)) for f in os.listdir('pulo_do_gato_bin') ]


        file = request.files.get('input_file')
        filename = secure_filename(file.filename)
        file.save(os.path.join(job_dir, filename))
        temperature = request.form.get('temperature')
        ph = request.form.get('pH')

        cwd = os.getcwd()
        os.chdir(job_dir)
        print(os.getcwd())

        subprocess.call('python2 ./pulo_do_gato.py -T {} -ph {} -s MC -f {} > output.txt'.format(temperature, ph, filename), shell=True)

        output_file = open('output.txt', 'r', encoding='utf-8')
        image_filename = os
        return_data = jsonify(
            job_dir=job_dir,
            stdout='<br/>'.join(output_file.read().split('\n')),
            image=glob.glob('*.jpg')[0],
            output=glob.glob('Output*.dat')[0]
        )
        output_file.close()

        os.chdir(cwd)

        return return_data
    else:
        return ''


if __name__ == '__main__':
      app.run(host='0.0.0.0')
