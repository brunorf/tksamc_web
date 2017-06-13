from django.shortcuts import render
from django.http.response import HttpResponse
from models import Job

# Create your views here.

def index(request):
    return render(request, 'main/index.html')


def submit(request):
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
