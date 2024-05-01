FROM python:latest

COPY requirements.txt .

RUN pip3 install -r requirements.txt

COPY stations.csv .
COPY performance_extract.py .
COPY entities.py .
COPY performance_transform.py .
COPY performance_load.py .
COPY main.py .

CMD ["python3", "main.py"]