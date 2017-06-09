from contextlib import contextmanager

@contextmanager
def change_workingdir(path):
    oldpwd=os.getcwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(oldpwd)
