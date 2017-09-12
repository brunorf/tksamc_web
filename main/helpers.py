from contextlib import contextmanager
import os

@contextmanager
def change_workingdir(path):
    oldpwd=os.getcwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(oldpwd)

def job_dir(job_id):
    from models import Job
    job = Job.query.filter(Job.id==job_id).first()
    return os.path.join('jobs', '{}_{}'.format(str(job.id), job.submit_date.strftime('%Y%m%d%H%M%S%f')))

def send_email(email, job_name, job_url):
    from django.urls import reverse
    from django.core.mail import send_mail

    message = """This is an automatic email regarding your request on the TKSA-MC server. When your job is done running you can see the results at """ + job_url
    title = 'Your job info on the TKSA-MC server'
    if job_name:
        title = title + ' ({})'.format(job_name)
    send_mail(
        title,
        message,
        'tksamc@ibilce.unesp.br',
        [email],
        fail_silently=False,
    )
