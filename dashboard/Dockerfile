FROM python:latest

WORKDIR /app

COPY Home.py .
COPY pages ./pages
COPY data_access.py .
COPY requirements.txt .

RUN pip install -r requirements.txt

CMD streamlit run Home.py