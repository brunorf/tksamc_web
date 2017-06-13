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
