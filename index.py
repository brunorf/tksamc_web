#!/usr/bin/python3

from flask import Flask, render_template, Response, jsonify, request, send_from_directory, redirect, url_for, abort
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


SERVER_NAME='http://localhost:5000'

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
        "Hello, you can check your job results on the link bellow:\n" +
        url_for('check_job', job_id=job_id, _external=True)
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

@app.route('/jobs/<job_id>/<filename>')
def get_job_files(job_id,filename):
    # check if requested file is not part of the system
    if filename not in ['aux', 'pulo_do_gato.py', 'radii.txt', 'README', 'src', 'surfrace5_0_linux_64bit']:
        return send_from_directory('jobs/' + job_id, filename)
    else:
        return abort(404)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit():
    import hashlib
    import random

    file = request.files.get('input_file')
    filename = secure_filename(file.filename)
    temperature = request.form.get('temperature')
    ph = request.form.get('pH')
    email = request.form.get('email')


    job_id = hashlib.sha1(bytearray(str(datetime.today()) + filename + temperature + ph + str(random.random()),'ascii')).hexdigest()
    job_dir = os.path.join('jobs', job_id )
    os.makedirs(job_dir)
    [ os.symlink(os.path.join('../../pulo_do_gato_bin', f), os.path.join(job_dir,f)) for f in os.listdir('pulo_do_gato_bin') ]
    file.save(os.path.join(job_dir, filename))

    cwd = os.getcwd()
    os.chdir(job_dir)
    print(os.getcwd())

    subprocess.Popen('python2 ./pulo_do_gato.py -T {} -ph {} -s MC -f {} > output.txt; touch finished'.format(temperature, ph, filename), shell=True)

    os.chdir(cwd)

    if email != '':
        send_email(email, job_id)

    return redirect(url_for('check_job', job_id=job_id))

@app.route('/check_job/<job_id>')
def check_job(job_id):
    job_dir = os.path.join('jobs', job_id )
    finished = False

    if os.path.isfile( os.path.join(job_dir, 'finished') ):
        finished = True
    stdout = ''
    with open(os.path.join(job_dir,'output.txt') ) as stdout_file:
        stdout='<br/>'.join(stdout_file.read().split('\n')),


    return render_template('check_job.html', finished=finished, job_id=job_id,
                    output_file=os.path.basename(glob.glob(os.path.join(job_dir, 'Output*.dat'))[0]),
                    image=os.path.basename(glob.glob(os.path.join(job_dir,'*.jpg') )[0]),
                    stdout=stdout)

if __name__ == '__main__':
      app.run(host='0.0.0.0')
