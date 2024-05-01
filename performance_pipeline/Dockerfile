FROM python:latest

COPY requirements.txt .

RUN pip3 install -r requirements.txt

COPY stations.csv .
COPY extract.py .
COPY entities.py .
COPY transform.py .
COPY load.py .
COPY main.py .

CMD ["python3", "main.py"]