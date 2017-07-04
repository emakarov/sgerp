FROM ubuntu:14.04

RUN apt-get update

WORKDIR /sgerp

ADD . /sgerp

RUN apt-get update -qq && apt-get upgrade -y
RUN apt-get install -y build-essential libgeos-dev python-dev python-pip python3

RUN pip install -r requirements.txt

EXPOSE 9191

CMD ["./runserv.sh"]
