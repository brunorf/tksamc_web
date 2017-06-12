from sqlalchemy import Column, Integer, String, Numeric, DateTime, Boolean
from database import Base
import datetime
import hashlib
import random

class Job(Base):
    __tablename__ = 'jobs'
    id = Column(Integer, primary_key=True)
    job_name = Column(String(30))
    pH = Column(Numeric(2,1))
    pH_range = Column(Boolean())
    temperature = Column(Numeric(10,2))
    submit_date = Column(DateTime)
    email = Column(String(30))

    def __init__(self, job_name=None, pH=None, pH_range=None, temperature=None, email=None):
        self.job_name = job_name
        self.pH = pH
        self.pH_range = pH_range
        self.temperature = temperature
        self.email = email
        self.submit_date = datetime.datetime.utcnow()

    def __repr__(self):
        return '<Job (%r) - %r>' % (self.id, self.job_name)
