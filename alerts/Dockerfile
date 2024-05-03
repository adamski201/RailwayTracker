FROM python:latest

ENV TZ=Europe/London

RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

COPY requirements.txt .

RUN pip3 install -r requirements.txt

COPY extract.py .

COPY transform.py .

COPY publish.py .

COPY load.py .

COPY main.py .

CMD ["python3", "main.py"]