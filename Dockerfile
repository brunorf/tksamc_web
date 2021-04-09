FROM debian:10

RUN apt-get clean && apt-get update

# definindo locale
RUN apt-get install -y locales
ENV TZ=America/Sao_Paulo
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# gromacs
RUN apt-get install -y gromacs

# python3 e dependências para o tksamc e gtksamc
RUN apt-get install -y python3 python3-pip
RUN pip3 install matplotlib==3.4.0 numpy==1.19.5 pandas==1.2.3 sympy==1.7.1 math3d==3.4.1 scipy==1.5.4 nestle==0.2.0 mdtraj==1.9.5

# dependencias para os scripts do tksamc
RUN apt-get install -y libstdc++5 zip

# preparação para rodar o django
RUN apt-get install -y virtualenv
RUN mkdir /code
WORKDIR /code
COPY ./requirements.txt /code/
RUN virtualenv -p python3 /venv/
RUN . /venv/bin/activate && pip install -r requirements.txt
RUN . /venv/bin/activate && pip install gunicorn==20.0.4
COPY . /code/
