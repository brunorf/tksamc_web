from django.shortcuts import render
from django.http.response import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from .models import Job

# Create your views here.

def sitemap(request):
    return render(request, 'main/sitemap.xml')

def google_search_console(request):
    return render(request, 'main/google_search_console.html')

def index(request):
    from .forms import JobForm
    form = JobForm()
    return render(request, 'main/index.html', {'form':form, 'nav': 'home'})

def results(request):
    return render(request, 'main/results.html', {'nav': 'results'})

def theory(request):
    return render(request, 'main/theory.html', {'nav': 'theory'})

def submit(request):
    import subprocess
    import os
    import re
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
        job_dir = os.path.join('static/jobs/', str(job.id))
        os.makedirs(job_dir)

        pdb_file.name = re.sub('[^0-9a-zA-Z.]+', '_', pdb_file.name)
        with open(os.path.join(job_dir, pdb_file.name), 'wb+') as destination:
            for chunk in pdb_file.chunks():
                destination.write(chunk)

        [ os.symlink(os.path.join('../../../pulo_do_gato_bin', f), os.path.join(job_dir,f)) for f in os.listdir('pulo_do_gato_bin') ]

        with helpers.change_workingdir(job_dir):
            subprocess.Popen(['/usr/bin/gmx', 'editconf', '-f', pdb_file.name, '-c', '-resnr', '1', '-label', 'A', '-o', 'processed_{0}'.format(pdb_file.name)], shell=False)

            if job.name != '':
                archive_name = job.name
            else:
                archive_name = str(job.id)

            if job.ph_range:
                subprocess.Popen(['./run_pdg-ph.sh', 'processed_{}'.format(pdb_file.name.split('.')[0]), 'MC', archive_name], shell=False)
            else:
                subprocess.Popen(['./run_pdg.sh', str(temperature), str(ph), 'processed_{}'.format(pdb_file.name), archive_name], shell=False)

            if email != '':
                job_url = request.build_absolute_uri(reverse('check_job', args=[job.id]))
                helpers.send_email(email, job_url)

    return HttpResponseRedirect(reverse('check_job', args=[job.id]))


def check_job(request, job_id):
    import os
    import glob
    import subprocess

    job_dir = os.path.join('static/jobs', str(job_id) )
    finished = False

    job = Job.objects.filter(id=job_id).first()
    if job == None:
        return HttpResponse('404')

    job_data = dict(job_id=str(job_id))
    if os.path.isfile( os.path.join(job_dir, 'finished') ):
        finished = True
        stdout = ''
        # with open(os.path.join(job_dir,'output.txt'), encoding='utf-8') as stdout_file:
        #     stdout='<br/>'.join(stdout_file.read().split('\n')),

        # print(job.pH_range == False)
        if job.ph_range:
            try:
                image1 = os.path.basename(glob.glob(os.path.join(job_dir,'*pH_7.0*.jpg') )[0])
                image2 = os.path.basename(glob.glob(os.path.join(job_dir,'Fig_Gqq*.jpg') )[0])
                stdout = subprocess.check_output("grep -e 'T\s=*' {0} | tail -1; grep 'Total dG Energy' {0} | tail -1".format(os.path.join(job_dir,'output.txt')), shell=True, universal_newlines=True)
            except:
                return render(request, 'main/job_error.html')
        else:
            try:
                image1 = os.path.basename(glob.glob(os.path.join(job_dir,'*.jpg') )[0])
                image2 = None
                stdout = (subprocess.check_output("grep -e 'pH\s=*' {0}; grep -e 'T\s=*' {0}; grep 'Total dG Energy' {0}".format(os.path.join(job_dir,'output.txt')), shell=True, universal_newlines=True).split('\n'))
            except:
                return render(request, 'main/job_error.html')

        stdout = '<br/>'.join(stdout)
        if job.name != '':
            archive_name = job.name
        else:
            archive_name = str(job.id)
        job_data = dict(
            job_id=str(job_id),
            job_name=job.name,
            output_file=os.path.basename(glob.glob(os.path.join(job_dir, 'Output*.dat'))[0]),
            image1=image1,
            image2=image2,
            stdout=stdout,
            ph_range=job.ph_range,
            archive_name=archive_name
        )
    else:
        job_data = dict(
            job_id=str(job_id),
            job_name=job.name
        )

    return render(request, 'main/check_job.html', {'finished':finished, **job_data})
