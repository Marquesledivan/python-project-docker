FROM python:3

WORKDIR /usr/src/app

COPY . .

ENV TZ 'America/Sao_Paulo'

RUN pip3 install --no-cache-dir -r requirements.txt && \
    echo $TZ > /etc/timezone && \
    apt-get update && apt-get install -y tzdata && \
    rm /etc/localtime && \
    ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && \
    dpkg-reconfigure -f noninteractive tzdata && \
    apt-get clean

CMD [ "python3", "./command.py" ]
