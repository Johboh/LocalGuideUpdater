FROM python:3.12.8-alpine3.21

ADD ./requirements.txt /

RUN apk update
RUN apk add bash
RUN pip install -r requirements.txt

ADD ./crontab /etc/cron.d/job-cron
RUN chmod 0644 /etc/cron.d/job-cron
RUN crontab /etc/cron.d/job-cron

ADD ./*.sh /
ADD ./*.py /
ADD ./.env /

RUN chmod +x -R /*.py /*.sh

CMD [ "/entrypoint.sh" ]
