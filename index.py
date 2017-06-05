#!/usr/bin/python3

from flask import Flask, render_template, Response, jsonify, request, send_from_directory, redirect, url_for
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

@app.route('/submit', methods=['POST'])
def submit():
    import hashlib
    import random
    # check if the post request has the file part
    # if 'input_file' not in request.files:
        # return redirect(request.url)

    # job_dir = 'jobs/{}'.format(datetime.today().strftime('%Y-%m-%d_%H:%M:%S:%f'))


    file = request.files.get('input_file')
    filename = secure_filename(file.filename)
    temperature = request.form.get('temperature')
    ph = request.form.get('pH')


    job_id = hashlib.sha512(bytearray(str(datetime.today()) + filename + temperature + ph + str(random.random()),'ascii')).hexdigest()
    job_dir = os.path.join('jobs', job_id )
    os.makedirs(job_dir)
    [ os.symlink(os.path.join('../../pulo_do_gato_bin', f), os.path.join(job_dir,f)) for f in os.listdir('pulo_do_gato_bin') ]
    file.save(os.path.join(job_dir, filename))

    cwd = os.getcwd()
    os.chdir(job_dir)
    print(os.getcwd())

    subprocess.Popen('python2 ./pulo_do_gato.py -T {} -ph {} -s MC -f {} > output.txt; touch finished'.format(temperature, ph, filename), shell=True)

    os.chdir(cwd)

    return redirect(url_for('check_job', job_id=job_id))

@app.route('/check_job/<job_id>')
def check_job(job_id):
    job_dir = os.path.join('jobs', job_id )
    if os.path.isfile( os.path.join(job_dir, 'finished') ):
        return 'terminou'
    else:
        return 'ainda não'


if __name__ == '__main__':
      app.run(host='0.0.0.0')
