FROM python:latest

COPY requirements.txt .

RUN pip3 install -r requirements.txt

COPY extract.py .

COPY transform.py .

COPY publish.py .

COPY load.py .

COPY main.py .

CMD ["python3", "main.py"]