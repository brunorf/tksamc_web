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
    import os
    form = JobForm()
    jobs_count = Job.objects.count()
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
    import shutil

    pdb_search = request.POST['pdb_search']

    pdb_file = None
    pdb_filename = None
    available_chains = []

    
    def run_script(processed_pdb_path, job_dir, orig_bin_dir, archive_name):
        [os.symlink(os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', orig_bin_dir, f),
                    os.path.join(job_dir, f)) for f in os.listdir(os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', orig_bin_dir))]

        with helpers.change_workingdir(job_dir):
            shutil.copy(processed_pdb_path, job_dir)

            if job.ph_range:
                subprocess.Popen(['./run_pdg-ph.sh', 'processed_{}'.format(
                    pdb_filename.split('.')[0]), 'MC', archive_name], shell=False)
            else:
                subprocess.Popen(['./run_pdg.sh', str(temperature), str(ph),
                                  'processed_{}'.format(pdb_filename), archive_name], shell=False)

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
        tksamc_version = int(form.cleaned_data['tksamc_version'])

        job = Job(name=name, ph=ph, ph_range=ph_range,
                  temperature=temperature, email=email, chain=chain, tksamc_version=tksamc_version)
        job.save()
        job_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), '../static/jobs/', str(job.id))
        os.makedirs(job_dir)
        
        tksamc_job_dir = None
        ntksamc_job_dir = None
        if tksamc_version == 1 or tksamc_version == 0:
            tksamc_job_dir = os.path.join(job_dir, 'tksamc')
            os.makedirs(tksamc_job_dir)
        if tksamc_version == 2 or tksamc_version == 0:
            ntksamc_job_dir = os.path.join(job_dir, 'ntksamc')
            os.makedirs(ntksamc_job_dir)

        if (not chain):
            chain = ['^\s']

        with open(os.path.join(job_dir, pdb_filename), 'w') as destination:
            new_pdb = '\n'.join(re.findall(r'^ATOM\s+(?:[^\s]+\s+){3}[%s]\s+.*' % ('|'.join(chain)), pdb, re.MULTILINE))
            destination.write(new_pdb)
        
        with helpers.change_workingdir(job_dir):
            subprocess.check_output(['/bin/sed', '-i', 's/AALA/ ALA/g;s/ACYS/ CYS/g;s/AASP/ ASP/g;s/AGLU/ GLU/g;s/APHE/ PHE/g;s/AGLY/ GLY/g;s/AHIS/ HIS/g;s/AILE/ ILE/g;s/ALYS/ LYS/g;s/ALEU/ LEU/g;s/AMET/ MET/g;s/AASN/ ASN/g;s/APRO/ PRO/g;s/AGLN/ GLN/g;s/AARG/ ARG/g;s/ASER/ SER/g;s/ATHR/ THR/g;s/AVAL/ VAL/g;s/ATRP/ TRP/g;s/ATYR/ TYR/g', pdb_filename], shell=False)
            subprocess.check_output(['/bin/sed', '-i', '/BALA/d;/BCYS/d;/BASP/d;/BGLU/d;/BPHE/d;/BGLY/d;/BHIS/d;/BILE/d;/BLYS/d;/BLEU/d;/BMET/d;/BASN/d;/BPRO/d;/BGLN/d;/BARG/d;/BSER/d;/BTHR/d;/BVAL/d;/BTRP/d;/BTYR/d', pdb_filename], shell=False)
            subprocess.check_output(['/usr/bin/gmx', 'editconf', '-f', pdb_filename, '-c', '-resnr',
                                '1', '-label', 'A', '-o', 'processed_{0}'.format(pdb_filename)], shell=False)
        
        if job.name != '':
            base_archive_name = job.name
        else:
            base_archive_name = str(job.id)
        
        if tksamc_job_dir:
            run_script(os.path.join(job_dir, 'processed_{0}'.format(pdb_filename)),
            tksamc_job_dir, 'tksamc_bin', 'tksamc_' + base_archive_name)
        if ntksamc_job_dir:
            run_script(os.path.join(job_dir, 'processed_{0}'.format(pdb_filename)),
            ntksamc_job_dir, 'ntksamc_bin', 'ntksamc_' + base_archive_name)
        

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

    tksamc_versions = []
    if job.tksamc_version == 1 or job.tksamc_version == 0:
        tksamc_versions.append('tksamc')
    if job.tksamc_version == 2 or job.tksamc_version == 0:
        tksamc_versions.append('ntksamc')
    
    if job.name != '':
        base_archive_name = job.name
    else:
        base_archive_name = str(job.id)

    for version in tksamc_versions:
        job_data[version] = dict()
        current_job_dir = os.path.join(job_dir, version)
        if os.path.isfile(os.path.join(current_job_dir, 'finished')):
            stdout = ''

            try:
                if job.ph_range:
                    image1 = os.path.basename(
                        glob.glob(os.path.join(current_job_dir, '*pH_7.0*.jpg'))[0])
                    image2 = os.path.basename(
                        glob.glob(os.path.join(current_job_dir, 'Fig_Gqq*.jpg'))[0])
                    stdout = subprocess.check_output("grep -e 'T\s=*' {0} | tail -1; grep 'Total dG Energy' {0} | tail -1".format(
                        os.path.join(current_job_dir, 'output.txt')), shell=True, universal_newlines=True)
                else:
                    image1 = os.path.basename(
                        glob.glob(os.path.join(current_job_dir, '*.jpg'))[0])
                    image2 = None
                    stdout = (subprocess.check_output("grep -e 'pH\s=*' {0}; grep -e 'T\s=*' {0}; grep 'Total dG Energy' {0}".format(
                        os.path.join(current_job_dir, 'output.txt')), shell=True, universal_newlines=True).split('\n'))
            except:
                if not job.erro:
                    job.erro = True
                    job.save()

            stdout = '<br/>'.join(stdout)
            
            try:
                output_file_summary = os.path.basename(
                    glob.glob(os.path.join(current_job_dir, 'dG_Energy_*.dat'))[0])
            except:
                output_file_summary = None

            job_data[version] = dict(
                output_file=os.path.basename(
                    glob.glob(os.path.join(current_job_dir, 'Output*.dat'))[0]),
                output_file_summary=output_file_summary,
                image1=image1,
                image2=image2,
                stdout=stdout,
                ph_range=job.ph_range,
                archive_name=version + '_' + base_archive_name,
                finished=True
            )
        else:
            job_data[version]['finished'] = False

    return render(request, 'main/check_job.html', {**job_data})


def get_chains(pdb):
    import re
    return list(set(re.findall(r'^ATOM\s+(?:[^\s]+\s+){3}([^\s])\s+.*', pdb, re.MULTILINE)))
