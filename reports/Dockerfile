FROM public.ecr.aws/lambda/python:latest

WORKDIR ${LAMBDA_TASK_ROOT}

ENV MPLCONFIGDIR /tmp/matplotlib_config

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY report_emailer.py .

CMD ["report_emailer.handler"]