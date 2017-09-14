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

    title = 'Your job info on the TKSA-MC server'
    begin_message = 'Your job '
    if job_name:
        title = title + ' ({})'.format(job_name)
        begin_message += 'named as {} '.format(job_name)
    message = (begin_message + "successful ran on TKSA-MC Web Server. You can view the results in the link: {} If you have any problems with the results, let us know.\n\n".format(job_url) +
                "Please, cite us with this results are useful\n\n" +
                "Thank you! Tanford-Kirkwood Surface Accessibility - Monte Carlo TKSA-MC: A Web Server for rational mutation via optimizing the protein charge interactions")
    
    send_mail(
        title,
        message,
        'tksamc@ibilce.unesp.br',
        [email],
        fail_silently=False,
    )
