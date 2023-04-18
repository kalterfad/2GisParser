FROM python:3.9

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN mkdir -p /usr/src/app/
WORKDIR /usr/src/app/

COPY . /usr/src/app/

RUN pip3 install --no-cache-dir -r req.txt
RUN apt-get update && apt-get -y install cron
RUN touch /usr/src/app/cron.log

RUN (crontab -l ; echo "0 9-18 * * 1-5 /usr/local/bin/python /usr/src/app/main.py >> /usr/src/app/cron.log 2>&11") | crontab -

RUN python3 /usr/src/app/init_models.py

CMD cron && tail -f /var/log/cron.log