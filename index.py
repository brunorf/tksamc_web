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
from database import db_session
from models import Job

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

@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()

@app.route('/jobs/<job_id>/<filename>')
def get_job_files(job_id,filename):
    # check if requested file is not part of the system
    if filename not in ['aux', 'pulo_do_gato.py', 'radii.txt', 'README', 'src', 'surfrace5_0_linux_64bit']:
        return send_from_directory('jobs/' + str(job_id), filename)
    else:
        return abort(404)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit():
    import hashlib
    import random
    import helpers

    file = request.files.get('input_file')
    filename = secure_filename(file.filename)
    job_name = request.form.get('job_name')
    temperature = request.form.get('temperature')
    pH = request.form.get('pH')
    email = request.form.get('email')

    pH_range = False
    if request.form.get('pH_range') != None:
        pH_range = True

    job = Job(job_name=job_name, pH=pH, pH_range=pH_range, temperature=temperature, email=email)

    db_session.add(job)
    db_session.commit()

    job_id = job.id
    job_dir = os.path.join('jobs', str(job_id) )
    os.makedirs(job_dir)
    [ os.symlink(os.path.join('../../pulo_do_gato_bin', f), os.path.join(job_dir,f)) for f in os.listdir('pulo_do_gato_bin') ]
    file.save(os.path.join(job_dir, filename))


    with helpers.change_workingdir(job_dir):
        subprocess.Popen('gmx editconf -f {0} -c -resnr 1 -label A -o processed_{0}'.format(filename), shell=True)

        if job.pH_range:
            subprocess.Popen('./run_pdg-ph.sh processed_{} MC > output.txt; touch finished'.format(filename.split('.')[0]), shell=True)
        else:
            subprocess.Popen('python2 ./pulo_do_gato.py -T {} -ph {} -s MC -f processed_{} > output.txt; touch finished'.format(temperature, pH, filename), shell=True)

    if email != '':
        send_email(email, job_id)

    return redirect(url_for('check_job', job_id=job_id))


@app.route('/get_job_archive/<job_id>')
def get_job_archive(job_id):
    import shutil
    import tempfile
    import time
    import helpers

    with helpers.change_workingdir(os.path.join('jobs', str(job_id))):
        job = Job.query.filter(Job.id==job_id).first()
        if job != None:
            if job.job_name and job.job_name != '':
                archive_name = job.job_name
            else:
                archive_name = str(job.id)

            # print(os.getcwd())
            subprocess.call('find . -type l -delete', shell=True)
            subprocess.call('find . -name "*.zip" -delete', shell=True)

            tmp_zip_dir = tempfile.TemporaryDirectory()
            filename = shutil.make_archive(os.path.join(tmp_zip_dir.name,archive_name),'zip')
            shutil.move(os.path.join(tmp_zip_dir.name, filename), '.')
            # return send_from_directory(os.path.join('jobs/', str(job_id)), filename)
            return redirect(url_for('get_job_files', job_id=job_id, filename=os.path.basename(filename)))
        return abort(404)


@app.route('/check_job/<job_id>')
def check_job(job_id):
    job_dir = os.path.join('jobs', str(job_id) )
    finished = False


    job = Job.query.filter(Job.id==job_id).first()
    if job == None:
        return abort(404)

    job_data = None
    if os.path.isfile( os.path.join(job_dir, 'finished') ):
        finished = True
        stdout = ''
        # with open(os.path.join(job_dir,'output.txt'), encoding='utf-8') as stdout_file:
        #     stdout='<br/>'.join(stdout_file.read().split('\n')),

        # print(job.pH_range == False)
        if job.pH_range:
            image1 = os.path.basename(glob.glob(os.path.join(job_dir,'Fig_Gqq*.jpg') )[0])
            image2 = os.path.basename(glob.glob(os.path.join(job_dir,'*pH_7.0*.jpg') )[0])
            stdout = subprocess.check_output("grep -e 'T\s=*' {0} | tail -1; grep 'Total dG Energy' {0} | tail -1".format(os.path.join(job_dir,'output.txt')), shell=True, universal_newlines=True)
        else:
            image1 = os.path.basename(glob.glob(os.path.join(job_dir,'*.jpg') )[0])
            image2 = None
            stdout = (subprocess.check_output("grep -e 'pH\s=*' {0}; grep -e 'T\s=*' {0}; grep 'Total dG Energy' {0}".format(os.path.join(job_dir,'output.txt')), shell=True, universal_newlines=True).split('\n'))

        job_data = dict(
            job_id=str(job_id),
            output_file=os.path.basename(glob.glob(os.path.join(job_dir, 'Output*.dat'))[0]),
            image1=image1,
            image2=image2,
            stdout=stdout
        )

    return render_template('check_job.html', finished=finished, job_data=job_data)

if __name__ == '__main__':
      app.run(host='0.0.0.0')
