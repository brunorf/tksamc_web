FROM debian:10

RUN apt-get clean && apt-get update

# definindo locale
RUN apt-get install -y locales
ENV TZ=America/Sao_Paulo
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# gromacs
RUN apt-get install -y gromacs

# python2 para tksamc
RUN apt-get install -y python python-scipy python-matplotlib python-numpy

# python3 para o gtksamc
RUN apt-get install -y python3 python3-scipy python3-matplotlib python3-numpy

# preparação para rodar o django
RUN apt-get install -y virtualenv
RUN mkdir /code
WORKDIR /code
COPY ./requirements.txt /code/
RUN virtualenv -p python3 /venv/
RUN . /venv/bin/activate && pip install -r requirements.txt
RUN . /venv/bin/activate && pip install gunicorn==20.0.4
COPY . /code/
