# Use the official Python image from the Docker Hub
FROM python:3.9

# These two environment variables prevent __pycache__/ files.
#ENV PYTHONUNBUFFERED 1
#ENV PYTHONDONTWRITEBYTECODE 1

RUN apt-get clean && apt-get update && apt-get install -y locales
RUN echo "pt_BR.UTF-8 UTF-8" > /etc/locale.gen 
RUN locale-gen pt_BR.UTF-8
ENV TZ=America/Sao_Paulo
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone
#RUN apt-get install -y libblas-dev liblapack-dev libatlas-base-dev 


# Make a new directory to put our code in.
RUN mkdir /code

# Change the working directory. 
# Every command after this will be run from the /code directory.
WORKDIR /code

# Copy the requirements.txt file.
COPY ./requirements.txt /code/

# Upgrade pip
RUN pip install --upgrade pip

#CMD /bin/bash

# Install the requirements.
RUN pip install -r requirements.txt

RUN pip install gunicorn==20.0.4

# Copy the rest of the code. 
COPY . /code/
