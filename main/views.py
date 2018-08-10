from django.shortcuts import render
from django.http.response import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from .models import Job
from django.http import JsonResponse

# Create your views here.


def sitemap(request):
    return render(request, 'main/sitemap.xml')


def google_search_console(request):
    return render(request, 'main/google_search_console.html')


def index(request):
    from .forms import JobForm
    import glob
    import os
    form = JobForm()
    jobs_dir = 'static/jobs'
    jobs_count = len(glob.glob(os.path.join(jobs_dir, '*')))
    return render(request, 'main/index.html', {'form': form, 'nav': 'home', 'jobs_count': jobs_count})


def results(request):
    return render(request, 'main/results.html', {'nav': 'results'})


def theory(request):
    return render(request, 'main/theory.html', {'nav': 'theory'})


def contact_us(request):
    return render(request, 'main/contact_us.html', {'nav': 'contact_us'})


def process_input_pdb(request):
    import pypdb
    import re

    pdb_file = None
    try:
        pdb_file = request.FILES['pdb_file']
    except:
        pass
    pdb_search = request.POST.get('pdb_search')
    pdb = None
    chains = []
    if (pdb_file):
        pdb = pdb_file.read().decode('utf-8')
    if (pdb_search):
        pdb = pypdb.get_pdb_file(pdb_search)

    if (pdb):
        chains = get_chains(pdb)
    data = {
        'chains': chains
    }
    return JsonResponse(data)


def submit(request):
    import subprocess
    import os
    import re
    from . import helpers
    from .forms import JobForm
    import pypdb

    pdb_search = request.POST['pdb_search']

    pdb_file = None
    pdb_filename = None
    available_chains = []
    if (pdb_search):
        pdb = pypdb.get_pdb_file(pdb_search)
        pdb_filename = pdb_search + '.pdb'
    else:
        pdb_file = None
        try:
            pdb_file = request.FILES['pdb_file']
        except:
            pass
        if (pdb_file):
            pdb_filename = re.sub('[^0-9a-zA-Z.]+', '_', pdb_file.name)
            pdb = pdb_file.read().decode('utf-8')

    available_chains = [[x,x] for x in get_chains(pdb)]

    form = JobForm(available_chains, request.POST, request.FILES)
    if form.is_valid():
        name = form.cleaned_data['name']
        temperature = form.cleaned_data['temperature']
        ph = form.cleaned_data['ph']
        ph_range = form.cleaned_data['ph_range']
        email = form.cleaned_data['email']
        chain = form.cleaned_data['chain']

        job = Job(name=name, ph=ph, ph_range=ph_range,
                  temperature=temperature, email=email, chain=chain)
        job.save()
        job_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), '../static/jobs/', str(job.id))
        os.makedirs(job_dir)

        if (not chain):
            chain = ['^\s']

        with open(os.path.join(job_dir, pdb_filename), 'w') as destination:
            new_pdb = '\n'.join(re.findall(r'^ATOM\s+(?:[^\s]+\s+){3}[%s]\s+.*' % ('|'.join(chain)), pdb, re.MULTILINE))
            destination.write(new_pdb)
            
        [os.symlink(os.path.join(os.path.dirname(os.path.realpath(__file__)), '../pulo_do_gato_bin', f),
                    os.path.join(job_dir, f)) for f in os.listdir(os.path.join(os.path.dirname(os.path.realpath(__file__)), '../pulo_do_gato_bin'))]

        with helpers.change_workingdir(job_dir):
            subprocess.Popen(['/bin/sed', '-i', 's/AALA/ ALA/g;s/ACYS/ CYS/g;s/AASP/ ASP/g;s/AGLU/ GLU/g;s/APHE/ PHE/g;s/AGLY/ GLY/g;s/AHIS/ HIS/g;s/AILE/ ILE/g;s/ALYS/ LYS/g;s/ALEU/ LEU/g;s/AMET/ MET/g;s/AASN/ ASN/g;s/APRO/ PRO/g;s/AGLN/ GLN/g;s/AARG/ ARG/g;s/ASER/ SER/g;s/ATHR/ THR/g;s/AVAL/ VAL/g;s/ATRP/ TRP/g;s/ATYR/ TYR/g', pdb_filename], shell=False)
            subprocess.Popen(['/bin/sed', '-i', '/BALA/d;/BCYS/d;/BASP/d;/BGLU/d;/BPHE/d;/BGLY/d;/BHIS/d;/BILE/d;/BLYS/d;/BLEU/d;/BMET/d;/BASN/d;/BPRO/d;/BGLN/d;/BARG/d;/BSER/d;/BTHR/d;/BVAL/d;/BTRP/d;/BTYR/d', pdb_filename], shell=False)
            subprocess.Popen(['/usr/bin/gmx', 'editconf', '-f', pdb_filename, '-c', '-resnr',
                              '1', '-label', 'A', '-o', 'processed_{0}'.format(pdb_filename)], shell=False)

            if job.name != '':
                archive_name = job.name
            else:
                archive_name = str(job.id)

            if job.ph_range:
                subprocess.Popen(['./run_pdg-ph.sh', 'processed_{}'.format(
                    pdb_filename.split('.')[0]), 'MC', archive_name], shell=False)
            else:
                subprocess.Popen(['./run_pdg.sh', str(temperature), str(ph),
                                  'processed_{}'.format(pdb_filename), archive_name], shell=False)

            if email != '':
                job_url = request.build_absolute_uri(
                    reverse('check_job', args=[job.id]))
                helpers.send_email(email, job.name, job_url)

        return HttpResponseRedirect(reverse('check_job', args=[job.id]))
    else:
        return render(request, 'main/index.html', {'form': form, 'nav': 'home'})


def check_job(request, job_id):
    import os
    import glob
    import subprocess

    job_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), '../static/jobs', str(job_id))
    finished = False

    job = Job.objects.filter(id=job_id).first()
    if job == None:
        return HttpResponse('404')

    job_data = dict(job_id=str(job_id))
    if os.path.isfile(os.path.join(job_dir, 'finished')):
        finished = True
        stdout = ''
        # with open(os.path.join(job_dir,'output.txt'), encoding='utf-8') as stdout_file:
        #     stdout='<br/>'.join(stdout_file.read().split('\n')),

        # print(job.pH_range == False)
        if job.ph_range:
            try:
                image1 = os.path.basename(
                    glob.glob(os.path.join(job_dir, '*pH_7.0*.jpg'))[0])
                image2 = os.path.basename(
                    glob.glob(os.path.join(job_dir, 'Fig_Gqq*.jpg'))[0])
                stdout = subprocess.check_output("grep -e 'T\s=*' {0} | tail -1; grep 'Total dG Energy' {0} | tail -1".format(
                    os.path.join(job_dir, 'output.txt')), shell=True, universal_newlines=True)
            except:
                return render(request, 'main/job_error.html')
        else:
            try:
                image1 = os.path.basename(
                    glob.glob(os.path.join(job_dir, '*.jpg'))[0])
                image2 = None
                stdout = (subprocess.check_output("grep -e 'pH\s=*' {0}; grep -e 'T\s=*' {0}; grep 'Total dG Energy' {0}".format(
                    os.path.join(job_dir, 'output.txt')), shell=True, universal_newlines=True).split('\n'))
            except:
                return render(request, 'main/job_error.html')

        stdout = '<br/>'.join(stdout)
        if job.name != '':
            archive_name = job.name
        else:
            archive_name = str(job.id)
        try:
            output_file_summary = os.path.basename(
                glob.glob(os.path.join(job_dir, 'dG_Energy_*.dat'))[0])
        except:
            output_file_summary = None

        job_data = dict(
            job_id=str(job_id),
            job_name=job.name,
            output_file=os.path.basename(
                glob.glob(os.path.join(job_dir, 'Output*.dat'))[0]),
            output_file_summary=output_file_summary,
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

    return render(request, 'main/check_job.html', {'finished': finished, **job_data})


def get_chains(pdb):
    import re
    return list(set(re.findall(r'^ATOM\s+(?:[^\s]+\s+){3}([^\s])\s+.*', pdb, re.MULTILINE)))
