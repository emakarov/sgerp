FROM python

RUN apt-get update

WORKDIR /sgerp

ADD . /sgerp

RUN apt-get update -qq && apt-get upgrade -y
RUN apt-get install -y build-essential libgeos-dev

RUN pip install -r requirements.txt

EXPOSE 9191

CMD ["./runserv.sh"]
