from django.shortcuts import render
from django.http.response import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from .models import Job

# Create your views here.

def index(request):
    from .forms import JobForm
    form = JobForm()
    return render(request, 'main/index.html', {'form':form})


def submit(request):
    import subprocess
    import os
    from . import helpers
    from .forms import JobForm

    form = JobForm(request.POST, request.FILES)
    if form.is_valid():
        name = form.cleaned_data['name']
        temperature = form.cleaned_data['temperature']
        ph = form.cleaned_data['ph']
        ph_range = form.cleaned_data['ph_range']
        email = form.cleaned_data['email']

        pdb_file = request.FILES['pdb_file']

        job = Job(name=name, ph=ph, ph_range=ph_range, temperature=temperature, email=email)
        job.save()
        job_dir = os.path.join('jobs/', str(job.id))
        os.makedirs(job_dir)

        with open(os.path.join(job_dir, pdb_file.name), 'wb+') as destination:
            for chunk in pdb_file.chunks():
                destination.write(chunk)

        [ os.symlink(os.path.join('../../pulo_do_gato_bin', f), os.path.join(job_dir,f)) for f in os.listdir('pulo_do_gato_bin') ]

        with helpers.change_workingdir(job_dir):
            subprocess.Popen('gmx editconf -f {0} -c -resnr 1 -label A -o processed_{0}'.format(pdb_file.name), shell=True)

            if job.ph_range:
                subprocess.Popen('./run_pdg-ph.sh processed_{} MC > output.txt; touch finished'.format(pdb_file.name.split('.')[0]), shell=True)
            else:
                subprocess.Popen('python2 ./pulo_do_gato.py -T {} -ph {} -s MC -f processed_{} > output.txt; touch finished'.format(temperature, ph, pdb_file.name), shell=True)

            if email != '':
                send_email(email, job_id)

    return HttpResponseRedirect(reverse('check_job', args=[job.id]))


def check_job(request, job_id):
    return HttpResponse(job_id)
