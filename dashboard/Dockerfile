FROM python:latest

WORKDIR /app

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY Home.py .
COPY pages ./pages
COPY data_access.py .
COPY subscribe.py .
COPY .streamlit/config.toml .streamlit/config.toml
COPY charts.py .
COPY logo.png .

CMD streamlit run Home.py